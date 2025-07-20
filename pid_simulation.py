#!/usr/bin/env python3
"""Dynamics and PID simulation for STEREO-A pointing errors.

This script loads RA, DEC, and Roll errors from a CSV file and feeds
them to three PID controllers. The resulting torques are applied to a
simple physical model of the STEREO-A spacecraft, using its approximate
mass, dimensions, and heliocentric orbit parameters. The integrated
attitude and orbital angle are written to a CSV file and, when
``matplotlib`` is available, a plot of the PID outputs is saved.
"""

import argparse
import csv
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence, Tuple


@dataclass
class PID:
    kp: float = 1.0
    ki: float = 0.0
    kd: float = 0.0
    integral: float = 0.0
    prev_err: float = 0.0

    def update(self, err: float, dt: float = 1.0) -> float:
        """Return PID correction for a single error sample."""
        self.integral += err * dt
        derivative = (err - self.prev_err) / dt
        self.prev_err = err
        return self.kp * err + self.ki * self.integral + self.kd * derivative


@dataclass
class Spacecraft:
    """Simple STEREO-A spacecraft model."""

    mass: float = 620.0  # kg
    side_length: float = 1.1  # m (approximate cube)
    inertia: Tuple[float, float, float] = field(init=False)
    attitude: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    ang_vel: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

    def __post_init__(self) -> None:
        i = (1.0 / 6.0) * self.mass * (self.side_length ** 2)
        self.inertia = (i, i, i)

    def step(self, torque: Tuple[float, float, float], dt: float = 1.0) -> None:
        """Integrate angular velocity and attitude from applied torque."""
        for idx, (tau, I) in enumerate(zip(torque, self.inertia)):
            alpha = tau / I
            self.ang_vel[idx] += alpha * dt
            self.attitude[idx] += self.ang_vel[idx] * dt


@dataclass
class Orbit:
    """Heliocentric orbit parameters for STEREO-A."""

    semi_major_axis: float = 0.97  # AU
    eccentricity: float = 0.01
    period_days: float = 347.0
    def mean_motion(self) -> float:
        return 360.0 / self.period_days


def load_errors(path: str) -> List[Tuple[float, float, float]]:
    """Load RA/DEC/Roll error tuples from the given CSV file."""
    errors: List[Tuple[float, float, float]] = []
    with open(path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                errors.append(
                    (
                        float(row["RA_error"]),
                        float(row["DEC_error"]),
                        float(row["Roll_error"]),
                    )
                )
            except (ValueError, KeyError):
                # Skip rows with missing or malformed data
                continue
    return errors


def simulate(
    errors: Sequence[Tuple[float, float, float]],
    kp: float,
    ki: float,
    kd: float,
    dt: float = 1.0,
    step_days: float = 0.02778,
) -> Tuple[List[Tuple[float, float, float]], List[Tuple[float, float, float]], List[float]]:
    """Run PID controllers and propagate spacecraft attitude."""
    pid_ra = PID(kp, ki, kd)
    pid_dec = PID(kp, ki, kd)
    pid_roll = PID(kp, ki, kd)
    sc = Spacecraft()
    orbit = Orbit()

    corrections: List[Tuple[float, float, float]] = []
    attitudes: List[Tuple[float, float, float]] = []
    orbit_angles: List[float] = []
    theta = 0.0

    for e_ra, e_dec, e_roll in errors:
        torque = (
            pid_ra.update(e_ra, dt),
            pid_dec.update(e_dec, dt),
            pid_roll.update(e_roll, dt),
        )
        sc.step(torque, dt)
        theta = (theta + orbit.mean_motion() * step_days) % 360.0

        corrections.append(torque)
        attitudes.append(tuple(sc.attitude))
        orbit_angles.append(theta)

    return corrections, attitudes, orbit_angles


def save_results(
    path: str,
    corr: Sequence[Tuple[float, float, float]],
    attitudes: Sequence[Tuple[float, float, float]],
    orbits: Sequence[float],
) -> None:
    """Write PID corrections and spacecraft state to a CSV file."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "step",
            "RA_correction",
            "DEC_correction",
            "Roll_correction",
            "RA",
            "DEC",
            "Roll",
            "orbit_deg",
        ])
        for i, (c, a, o) in enumerate(zip(corr, attitudes, orbits)):
            writer.writerow([i, c[0], c[1], c[2], a[0], a[1], a[2], o])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PID simulation on star-tracker errors")
    parser.add_argument(
        "--input",
        default="attitude_errors_combined.csv",
        help="CSV file containing RA_error, DEC_error, and Roll_error columns",
    )
    parser.add_argument(
        "--output",
        default="pid_corrections.csv",
        help="CSV file to store the PID correction sequence",
    )
    parser.add_argument("--kp", type=float, default=1.0, help="Proportional gain")
    parser.add_argument("--ki", type=float, default=0.1, help="Integral gain")
    parser.add_argument("--kd", type=float, default=0.05, help="Derivative gain")
    args = parser.parse_args()

    errors = load_errors(args.input)
    corr, attitudes, orbits = simulate(errors, args.kp, args.ki, args.kd)
    save_results(args.output, corr, attitudes, orbits)

    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not available; skipping plot generation")
        return

    t = range(len(corr))
    plt.figure(figsize=(10, 6))
    plt.plot(t, [c[0] for c in corr], label="RA control")
    plt.plot(t, [c[1] for c in corr], label="DEC control")
    plt.plot(t, [c[2] for c in corr], label="Roll control")
    plt.xlabel("Step")
    plt.ylabel("PID output")
    plt.title("PID corrections over time")
    plt.legend()
    plt.tight_layout()
    plt.savefig("pid_corrections.png")


if __name__ == "__main__":
    main()
