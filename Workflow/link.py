#!/usr/bin/env python3
import os, sys, glob, re, json
from datetime import datetime
import argparse

def parse_namelist_start_date(nml_path):
    """
    Scan namelist.input for start_year, start_month, start_day (and hour/minute/second if present).
    Returns a datetime.datetime.
    """
    keys = ("start_year","start_month","start_day",
            "start_hour","start_minute","start_second")
    vals = {}
    with open(nml_path) as f:
        for line in f:
            for key in keys:
                if key in line and "=" in line:
                    # grab all integers on that line, take the first
                    nums = re.findall(r"\d+", line)
                    if nums and key not in vals:
                        vals[key] = int(nums[0])

    missing = [k for k in ("start_year","start_month","start_day") if k not in vals]
    if missing:
        sys.exit(f"Error: {nml_path} is missing {', '.join(missing)}")

    # provide defaults for time if missing
    year  = vals["start_year"]
    month = vals["start_month"]
    day   = vals["start_day"]
    hour   = vals.get("start_hour",   0)
    minute = vals.get("start_minute", 0)
    second = vals.get("start_second", 0)
    try:
        return datetime(year, month, day, hour, minute, second)
    except ValueError as e:
        sys.exit(f"Error parsing start_date from {nml_path}: {e}")

def determine_real_dir(start_dt):
    """
    Map start_dt to (year_dir, real_sub) using your real1/2/3 windows:

      real1: 1 Aug–30 Nov     -> year_dir = dt.year
      real2: 1 Dec–31 Mar     -> year_dir = (Dec: dt.year, Jan–Mar: dt.year-1)
      real3: 1 Apr–31 Jul     -> year_dir = dt.year-1
    """
    m = start_dt.month
    y = start_dt.year

    if 8 <= m <= 11:        # Aug–Nov
        return y, "real1"
    if m == 12:             # Dec
        return y, "real2"
    if 1 <= m <= 3:         # Jan–Mar
        return y-1, "real2"
    if 4 <= m <= 7:         # Apr–Jul
        return y-1, "real3"
    raise ValueError(f"Month {m} not in any realX period")

def infer_letter_and_roots(wrf_dir):
    """
    Expect wrf_dir like .../<Letter>/wrf
    Returns (letter, letter_dir, root_dir)
    """
    letter_dir = os.path.dirname(os.path.abspath(wrf_dir))
    letter = os.path.basename(letter_dir)
    root_dir = os.path.dirname(letter_dir)
    if len(letter) != 1 or not letter.isalpha():
        sys.exit(f"Error: could not infer a single-letter sub-experiment from path: {wrf_dir}")
    return letter.upper(), letter_dir, root_dir

def load_spinup_map(json_path):
    """
    JSON format:
    {
      "G": { "1998": "F", "1999": "F" },
      "I": { "2018": "H", "2019": "H" }
    }
    All letters are case-insensitive; years are coerced to int.
    """
    if not json_path:
        return {}
    try:
        with open(json_path) as f:
            raw = json.load(f)
    except Exception as e:
        sys.exit(f"Error reading spin-up map JSON {json_path}: {e}")

    out = {}
    for let, yearmap in raw.items():
        if yearmap is None:
            continue
        L = str(let).upper()
        out[L] = {}
        for y, dst in yearmap.items():
            try:
                yi = int(y)
            except Exception:
                sys.exit(f"Error: spin-up map year keys must be ints/strings of ints; got {y!r}")
            out[L][yi] = str(dst).upper()
    return out

def candidate_letters(letter, year, spin_map, allow_fallback=True):
    """
    Build a list of letters to try for real/ lookup, in order of preference.
    1) If spin_map dictates a redirect for (letter, year), return [mapped_letter].
    2) Else: [letter] + (optionally) earlier letters in reverse alphabet (G,F,E,...,A).
    """
    if letter in spin_map and year in spin_map[letter]:
        return [spin_map[letter][year]]

    order = [letter]
    if allow_fallback:
        base_ord = ord(letter)
        for o in range(base_ord-1, ord('A')-1, -1):
            order.append(chr(o))
    return order

def find_real_path(root_dir, letters_to_try, year_dir, real_sub):
    """
    Return the first existing real path among:
      <root>/<L>/real/<year_dir>/<real_sub>
    """
    tried = []
    for L in letters_to_try:
        p = os.path.join(root_dir, L, "real", str(year_dir), real_sub)
        if os.path.isdir(p):
            return p, tried
        tried.append(p)
    return None, tried

def ensure_symlink(src, dst, overwrite=False, dry_run=False):
    """
    Create/verify a symlink from absolute destination to absolute source,
    and print absolute paths in all messages.
    """
    src_abs = os.path.abspath(src)
    dst_abs = os.path.abspath(dst)

    if os.path.lexists(dst_abs):  # includes broken symlinks
        # already correct?
        if os.path.islink(dst_abs) and os.path.realpath(dst_abs) == os.path.realpath(src_abs):
            print(f"OK: already linked {dst_abs} -> {src_abs}")
            return
        if not overwrite:
            print(f"Skip (exists): {dst_abs} (not overwriting) [target would be {src_abs}]")
            return
        if dry_run:
            print(f"Would relink {dst_abs} -> {src_abs}")
            return
        if os.path.isdir(dst_abs) and not os.path.islink(dst_abs):
            sys.exit(f"Refusing to overwrite directory: {dst_abs}")
        os.remove(dst_abs)

    if dry_run:
        print(f"Would link {dst_abs} -> {src_abs}")
        return

    # Use absolute source to avoid ambiguity
    os.symlink(src_abs, dst_abs)
    print(f"Linked {dst_abs} -> {src_abs}")

def link_real_wrf(wrf_dir, pattern="wrf*d01", spin_json=None, no_fallback=False, overwrite=False, dry_run=False):
    # 1) find namelist
    nml = os.path.join(wrf_dir, "namelist.input")
    if not os.path.isfile(nml):
        sys.exit(f"Error: no namelist.input in {wrf_dir}")

    # 2) parse start date
    dt = parse_namelist_start_date(nml)
    year_dir, real_sub = determine_real_dir(dt)

    # 3) infer location and search strategy
    letter, letter_dir, root_dir = infer_letter_and_roots(wrf_dir)
    spin_map = load_spinup_map(spin_json)
    letters_to_try = candidate_letters(letter, year_dir, spin_map, allow_fallback=not no_fallback)

    # 4) locate real path
    real_path, tried = find_real_path(root_dir, letters_to_try, year_dir, real_sub)
    if not real_path:
        msg = ["Error: could not find a matching real/ directory."]
        msg.append(f"  looked for real paths (in order):")
        msg += [f"    - {p}" for p in tried]
        if spin_map:
            msg.append("  (A spin-up map was provided; double-check its entries.)")
        else:
            msg.append("  (Consider providing a spin-up map JSON or allow fallback.)")
        sys.exit("\n".join(msg))

    # 5) glob wrf*d01* files and link
    files = sorted(glob.glob(os.path.join(real_path, pattern)))
    if not files:
        sys.exit(f"No files found with pattern {pattern!r} in {real_path}")

    print(f"Start date: {dt:%Y-%m-%d %H:%M:%S}")
    print(f"real selection: year_dir={year_dir}, sub={real_sub}")
    print(f"sub-experiment letter: {letter}")
    print(f"source real path: {os.path.abspath(real_path)}")
    print(f"linking pattern: {pattern}")
    if dry_run:
        print("DRY-RUN: no changes will be made.\n")

    for src in files:
        dst = os.path.join(wrf_dir, os.path.basename(src))
        ensure_symlink(src, dst, overwrite=overwrite, dry_run=dry_run)

    print(f"\nDone. {'Would link' if dry_run else 'Linked'} {len(files)} file(s) from {os.path.abspath(real_path)}")

def main():
    parser = argparse.ArgumentParser(
        description="Link wrf*d01 files from the appropriate real/<year>/real{1,2,3} folder."
    )
    parser.add_argument("wrf_dir", help="Path to the wrf/ directory (must contain namelist.input)")
    parser.add_argument("--pattern", default="wrf*d01",
                        help="Glob pattern to link (default: wrf*d01)")
    parser.add_argument("--spinup-map", default=None,
                        help="Path to JSON mapping of letter→{year:int→letter} for spin-up overrides")
    parser.add_argument("--no-fallback", action="store_true",
                        help="Do not search earlier letters if local real/ path is missing")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing files/symlinks at the destination")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print actions without creating/removing symlinks")
    args = parser.parse_args()

    link_real_wrf(
        os.path.abspath(args.wrf_dir),
        pattern=args.pattern,
        spin_json=args.spinup_map,
        no_fallback=args.no_fallback,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
    )

if __name__ == "__main__":
    main()
