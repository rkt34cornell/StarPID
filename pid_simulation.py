#!/usr/bin/env python3
"""PID simulation for star-tracker pointing errors.

This script reads RA, DEC, and Roll error columns from a CSV file and
simulates independent PID controllers for each axis. The resulting
control outputs are written to a CSV file and, if matplotlib is
available, a plot of the corrections over time is generated.
"""

import argparse
import csv
from dataclasses import dataclass
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
) -> List[Tuple[float, float, float]]:
    """Run PID controllers across a sequence of errors."""
    pid_ra = PID(kp, ki, kd)
    pid_dec = PID(kp, ki, kd)
    pid_roll = PID(kp, ki, kd)
    corrections: List[Tuple[float, float, float]] = []
    for e_ra, e_dec, e_roll in errors:
        corrections.append(
            (
                pid_ra.update(e_ra, dt),
                pid_dec.update(e_dec, dt),
                pid_roll.update(e_roll, dt),
            )
        )
    return corrections


def save_corrections(path: str, corr: Iterable[Tuple[float, float, float]]) -> None:
    """Write the PID correction sequence to a CSV file."""
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "RA_correction", "DEC_correction", "Roll_correction"])
        for i, (c_ra, c_dec, c_roll) in enumerate(corr):
            writer.writerow([i, c_ra, c_dec, c_roll])


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
    corrections = simulate(errors, args.kp, args.ki, args.kd)
    save_corrections(args.output, corrections)

    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not available; skipping plot generation")
        return

    t = range(len(corrections))
    plt.figure(figsize=(10, 6))
    plt.plot(t, [c[0] for c in corrections], label="RA control")
    plt.plot(t, [c[1] for c in corrections], label="DEC control")
    plt.plot(t, [c[2] for c in corrections], label="Roll control")
    plt.xlabel("Step")
    plt.ylabel("PID output")
    plt.title("PID corrections over time")
    plt.legend()
    plt.tight_layout()
    plt.savefig("pid_corrections.png")


if __name__ == "__main__":
    main()
