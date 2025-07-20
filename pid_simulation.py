import csv
import math

class PID:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_err = 0.0

    def update(self, err, dt=1.0):
        self.integral += err * dt
        derivative = (err - self.prev_err) / dt
        self.prev_err = err
        return self.kp * err + self.ki * self.integral + self.kd * derivative


def load_errors(path):
    ra_err = []
    dec_err = []
    roll_err = []
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                ra_err.append(float(row['RA_error']))
                dec_err.append(float(row['DEC_error']))
                roll_err.append(float(row['Roll_error']))
            except ValueError:
                # Skip rows with missing or non-numeric data
                continue
    return list(zip(ra_err, dec_err, roll_err))


def simulate(errors, kp=1.0, ki=0.1, kd=0.05, dt=1.0):
    pid_ra = PID(kp, ki, kd)
    pid_dec = PID(kp, ki, kd)
    pid_roll = PID(kp, ki, kd)
    corrections = []
    for e_ra, e_dec, e_roll in errors:
        c_ra = pid_ra.update(e_ra, dt)
        c_dec = pid_dec.update(e_dec, dt)
        c_roll = pid_roll.update(e_roll, dt)
        corrections.append((c_ra, c_dec, c_roll))
    return corrections


def main():
    data_file = 'attitude_errors_combined.csv'
    errors = load_errors(data_file)
    corrections = simulate(errors)
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print('matplotlib not available; skipping plot generation')
        return
    t = range(len(corrections))
    ra_ctrl = [c[0] for c in corrections]
    dec_ctrl = [c[1] for c in corrections]
    roll_ctrl = [c[2] for c in corrections]
    plt.figure(figsize=(10, 6))
    plt.plot(t, ra_ctrl, label='RA control')
    plt.plot(t, dec_ctrl, label='DEC control')
    plt.plot(t, roll_ctrl, label='Roll control')
    plt.xlabel('Step')
    plt.ylabel('PID output')
    plt.title('PID corrections over time')
    plt.legend()
    plt.tight_layout()
    plt.savefig('pid_corrections.png')


if __name__ == '__main__':
    main()
