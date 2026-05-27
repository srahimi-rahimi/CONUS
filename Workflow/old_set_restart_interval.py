import os
import sys
import glob
import re
from datetime import datetime, date, timedelta

def find_latest_restart(wrf_dir, pattern="wrfrst*0000"):
    files = sorted(glob.glob(os.path.join(wrf_dir, pattern)))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' in {wrf_dir}")
    return files[-1]

def parse_datetime_from_filename(fname):
    # expects …_<YYYY-MM-DD_HH:MM:SS> in the filename
    m = re.search(r'_(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})', fname)
    if not m:
        raise ValueError(f"Could not extract timestamp from '{fname}'")
    return datetime.strptime(m.group(1), "%Y-%m-%d_%H:%M:%S")

def next_seasonal_boundary(dt):
    year = dt.year
    targets = [
        date(year, 4, 1),
        date(year, 8, 1),
        date(year, 12, 1),
    ]
    # if we're past one, schedule it in the next calendar cycle
    future = []
    for d in targets:
        if dt.date() < d:
            future.append(d)
        else:
            future.append(date(year+1, d.month, d.day))
    return min(future)

def update_restart_interval(nml_path, days):
    """Replace the single restart_interval line to use `days` for all domains."""
    with open(nml_path) as f:
        lines = f.readlines()

    out = []
    for L in lines:
        if re.match(r'\s*restart_interval\b', L):
            # count how many comma-separated entries
            nums = re.findall(r'\d+', L)
            count = len(nums)
            # build a comma-separated list of `days` repeated
            body = ", ".join(str(days) for _ in range(count))
            # preserve trailing comma if present
            comma = "," if L.rstrip().endswith(",") else ""
            L = re.sub(
                  r'(restart_interval\s*=\s*).*',
                  lambda m: f"{m.group(1)}{body}{comma}",
                  L
)
        out.append(L)

    with open(nml_path, "w") as f:
        f.writelines(out)

def main(wrf_dir):
    # 1) locate files
    latest = find_latest_restart(wrf_dir)
    dt = parse_datetime_from_filename(latest)

    # 2) compute days until next boundary
    target = next_seasonal_boundary(dt)
    delta = (target - dt.date()).days

    print(f"Latest restart: {os.path.basename(latest)} → {dt.date()}")
    print(f"Next boundary: {target}  (in {delta} days)")

    # 3) only update if within 20 days
    if delta <= 20:
        nml = os.path.join(wrf_dir, "namelist.input")
        if not os.path.isfile(nml):
            sys.exit(f"ERROR: '{nml}' not found")
        update_restart_interval(nml, delta)
        print(f"✔️  restart_interval set to {delta} day(s) in namelist.input")
    else:
        print(f"⚠️  Next boundary is more than 20 days away; leaving restart_interval unchanged.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: set_restart_interval.py /path/to/wrf_directory")
        sys.exit(1)
    main(sys.argv[1])
