import sys
import os
import glob
import re
from datetime import datetime

def find_latest_restart(pattern="wrfrst*0000"):
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' found.")
    return files[-1]

def parse_datetime_from_filename(fname):
    # expects an underscore before YYYY-MM-DD_HH:MM:SS
    m = re.search(r'_(\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2})', fname)
    if not m:
        raise ValueError(f"Could not extract timestamp from '{fname}'")
    return datetime.strptime(m.group(1), "%Y-%m-%d_%H:%M:%S")

def update_namelist(nml_path, dt):
    with open(nml_path) as f:
        lines = f.readlines()

    out = []
    for L in lines:
        # for each of the six start_* parameters, detect and replace
        for key, val in [
            ("start_year",   dt.year),
            ("start_month",  dt.month),
            ("start_day",    dt.day),
            ("start_hour",   dt.hour),
            ("start_minute", dt.minute),
            ("start_second", dt.second),
        ]:
            if re.match(rf"\s*{key}\b", L):
                # split off the RHS, count how many comma-separated entries
                lhs, rhs = L.split("=", 1)
                nums = re.findall(r"\d+", rhs)
                count = len(nums)
                newlist = ", ".join(str(val) for _ in range(count))
                # rebuild line, preserving indentation and trailing comma
                sep = "," if rhs.strip().endswith(",") else ""
                L = f"{lhs}= {newlist}{sep}\n"
                break
        out.append(L)

    # write back
    with open(nml_path, "w") as f:
        f.writelines(out)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update_namelist.py /path/to/namelist.input")
        sys.exit(1)

    namelist = sys.argv[1]
    latest = find_latest_restart()
    dt = parse_datetime_from_filename(latest)

    print(f"Updating '{namelist}' to start at {dt.isoformat(' ')} based on '{latest}'")
    update_namelist(namelist, dt)
    print("Done.")
