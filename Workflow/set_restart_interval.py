import os
import sys
import glob
import re
from datetime import datetime, date

def find_latest_restart(wrf_dir, pattern="wrfrst*0000"):
    files = sorted(glob.glob(os.path.join(wrf_dir, pattern)))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' in {wrf_dir}")
    return files[-1]

def parse_datetime_from_filename(fname):
    m = re.search(r'_(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})', fname)
    if not m:
        raise ValueError(f"Could not extract timestamp from '{fname}'")
    return datetime.strptime(m.group(1), "%Y-%m-%d_%H:%M:%S")

def next_seasonal_boundary(dt):
    year = dt.year
    boundaries = [date(year, 4, 1), date(year, 8, 1), date(year, 12, 1)]
    future = [d for d in boundaries if dt.date() < d] + [date(year + 1, d.month, d.day) for d in boundaries]
    return min(future)

def update_namelist_times(nml_path, run_days, restart_interval_minutes):
    """Update 'restart_interval' (in minutes) and 'run_days' (in days) in namelist.input."""
    with open(nml_path) as f:
        lines = f.readlines()

    out = []
    for L in lines:
        # Update restart_interval
        if re.match(r'\s*restart_interval\b', L):
            nums = re.findall(r'\d+', L)
            count = len(nums)
            body = ", ".join(str(restart_interval_minutes) for _ in range(count))
            comma = "," if L.rstrip().endswith(",") else ""
            L = re.sub(
                r'(restart_interval\s*=\s*).*',
                lambda m: f"{m.group(1)}{body}{comma}",
                L
            )

        # Update run_days
        if re.match(r'\s*run_days\b', L):
            nums = re.findall(r'\d+', L)
            count = len(nums)
            body = ", ".join(str(run_days) for _ in range(count))
            comma = "," if L.rstrip().endswith(",") else ""
            L = re.sub(
                r'(run_days\s*=\s*).*',
                lambda m: f"{m.group(1)}{body}{comma}",
                L
            )

        out.append(L)

    with open(nml_path, "w") as f:
        f.writelines(out)

def main(wrf_dir):
    latest = find_latest_restart(wrf_dir)
    dt = parse_datetime_from_filename(latest)

    target = next_seasonal_boundary(dt)
    delta = (target - dt.date()).days

    print(f"Latest restart: {os.path.basename(latest)} → {dt.date()}")
    print(f"Next boundary: {target}  (in {delta} days)")

    if delta < 40:
        run_days = delta
        restart_minutes = delta * 1440
        print(f"✔️  Close to boundary: run_days = {run_days}, restart_interval = {restart_minutes} minutes")
    else:
        run_days = 40
        restart_minutes = 28800
        print(f"✔️  Defaulting: run_days = {run_days}, restart_interval = {restart_minutes} minutes")

    nml = os.path.join(wrf_dir, "namelist.input")
    if not os.path.isfile(nml):
        sys.exit(f"ERROR: '{nml}' not found")

    update_namelist_times(nml, run_days=run_days, restart_interval_minutes=restart_minutes)
    print("✔️  namelist.input updated.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_restart_interval.py /path/to/wrf_directory")
        sys.exit(1)
    main(sys.argv[1])
