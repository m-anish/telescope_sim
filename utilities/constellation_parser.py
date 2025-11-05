#!/usr/bin/env python3
"""
constellation_parser_fixed2.py

Parse constellation line data (with headers that start with '*') and output JSON with coordinates and label positions.

Usage:
  python3 constellation_parser_fixed2.py \
    -s data/hyg_all_stars.csv \
    -i data/constellation_lines_simplified.dat \
    -o data/constellations.json
"""

import csv
import json
import argparse
import math
import re

# ---------------- helpers ----------------
def load_star_positions(hyg_csv):
    """
    Load HIP -> (RA_deg, Dec_deg) mapping from a HYG-style CSV.
    Accepts header HIP or hip, and RA_deg/Dec_deg (or ra/dec).
    Keys in returned dict are integers.
    """
    stars = {}
    with open(hyg_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # make header lowercase map for robust lookup
        headers = [h for h in reader.fieldnames] if reader.fieldnames else []
        for row in reader:
            # find hip field (case-insensitive)
            hip_val = None
            for possible in ("HIP","hip","hipnr","hip_num","hipparcos","hipparcos_id"):
                if possible in row and row[possible] not in (None, ""):
                    hip_val = row[possible]
                    break
            # fallback: try common header names
            if hip_val is None:
                for k in row.keys():
                    if k.lower().startswith("hip"):
                        hip_val = row[k]
                        break
            if not hip_val:
                # try first column
                continue
            try:
                hip = int(float(str(hip_val).strip()))
            except Exception:
                continue

            # find RA/Dec
            ra = None; dec = None
            for rk in ("RA_deg","ra_deg","RA","ra","raJ2000","raj2000","ra_hours"):
                if rk in row and row[rk] not in (None, ""):
                    try:
                        ra = float(row[rk])
                        break
                    except Exception:
                        pass
            for dk in ("Dec_deg","dec_deg","Dec","dec","decJ2000","decj2000"):
                if dk in row and row[dk] not in (None, ""):
                    try:
                        dec = float(row[dk])
                        break
                    except Exception:
                        pass

            if ra is None or dec is None:
                # try columns named 'x','y','z' are not used here
                continue

            stars[hip] = (ra, dec)
    return stars

def spherical_centroid(points):
    """
    Given list of (RA_deg, Dec_deg), compute centroid on unit sphere,
    return (RA_deg, Dec_deg). RA normalized to [0,360).
    """
    if not points:
        return (0.0, 0.0)
    x = y = z = 0.0
    for ra, dec in points:
        ra_r = math.radians(ra)
        dec_r = math.radians(dec)
        x += math.cos(dec_r) * math.cos(ra_r)
        y += math.cos(dec_r) * math.sin(ra_r)
        z += math.sin(dec_r)
    n = len(points)
    x /= n; y /= n; z /= n
    ra = math.degrees(math.atan2(y, x)) % 360.0
    dec = math.degrees(math.atan2(z, math.sqrt(x*x + y*y)))
    return (ra, dec)

def parse_hip_list_from_line(line):
    """
    Robustly extract integers (HIPs) from a line.
    Accepts: "12345 23456", "12345,23456,34567", '["12345","23456"]', etc.
    Returns list of ints (may be empty).
    """
    line = line.strip()
    if not line:
        return []
    # Try ast-like JSON list first (fast simple check for [ and ])
    if line.startswith("[") and line.endswith("]"):
        # extract numbers inside using regex
        nums = re.findall(r'\d+', line)
        return [int(n) for n in nums] if nums else []

    # Otherwise extract all integer tokens
    nums = re.findall(r'\d+', line)
    return [int(n) for n in nums] if nums else []

# ---------------- main parse ----------------
def parse_constellations(dat_file, star_map, verbose=False):
    """
    Parse constellation file that uses headers beginning with '*' (or plain names),
    followed by lines containing HIP numbers (pairs/chains/arrays).
    Returns list of {"name": "...", "lines":[[ [ra,dec], [ra,dec] ... ]], "label":[ra,dec]}
    """
    constellations = []
    current = None
    current_points = []

    with open(dat_file, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            # skip comments
            if line.startswith("#") or line.lower().startswith("!"):
                continue

            # Header lines in your source begin with '*'
            if line.startswith("*"):
                # flush previous
                if current:
                    # compute centroid label from collected points
                    if current_points:
                        current["label"] = list(spherical_centroid(current_points))
                    else:
                        current["label"] = [None, None]
                    constellations.append(current)
                # clean header name
                name = line.lstrip("*").strip()
                # sometimes header may contain additional tokens; keep until first ':' or similar
                name = re.sub(r'\s*[:;].*$', '', name).strip()
                current = {"name": name, "lines": []}
                current_points = []
                continue

            # Also allow plain-alpha headers (if file uses them)
            # A line is a header if it contains letters and few or no digits
            letters = re.findall(r'[A-Za-z]', line)
            digits = re.findall(r'\d+', line)
            if letters and len(digits) < 2 and not line.startswith("["):
                # treat as header (covers some alternate formats)
                if current:
                    if current_points:
                        current["label"] = list(spherical_centroid(current_points))
                    else:
                        current["label"] = [None, None]
                    constellations.append(current)
                name = line.strip().lstrip("*").strip()
                name = re.sub(r'\s*[:;].*$', '', name).strip()
                current = {"name": name, "lines": []}
                current_points = []
                continue

            # otherwise parse HIP numbers and create segments
            hips = parse_hip_list_from_line(line)
            if not hips or not current:
                continue

            # If exactly two hips -> one segment
            if len(hips) == 2:
                a, b = hips[0], hips[1]
                if a in star_map and b in star_map:
                    p1 = star_map[a]; p2 = star_map[b]
                    current["lines"].append([list(p1), list(p2)])
                    current_points.extend([p1, p2])
                elif verbose:
                    missing = []
                    if a not in star_map: missing.append(a)
                    if b not in star_map: missing.append(b)
                    print(f"WARNING: missing HIP(s) {missing} for segment in {current['name']}")
            else:
                # chain of 3+ hips -> add consecutive segments
                for i in range(len(hips)-1):
                    a, b = hips[i], hips[i+1]
                    if a in star_map and b in star_map:
                        p1 = star_map[a]; p2 = star_map[b]
                        current["lines"].append([list(p1), list(p2)])
                        current_points.extend([p1, p2])
                    elif verbose:
                        missing = []
                        if a not in star_map: missing.append(a)
                        if b not in star_map: missing.append(b)
                        print(f"WARNING: missing HIP(s) {missing} in chain for {current['name']}")

    # flush last
    if current:
        if current_points:
            current["label"] = list(spherical_centroid(current_points))
        else:
            current["label"] = [None, None]
        constellations.append(current)

    # filter out constellations with no lines
    constellations = [c for c in constellations if c.get("lines")]
    return constellations

# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser(description="Parse constellation lines (HIP lists) to JSON with coordinates and label positions.")
    ap.add_argument("-s", "--stars", default="data/hyg_all_stars.csv", help="HYG CSV with HIP,RA_deg,Dec_deg")
    ap.add_argument("-i", "--input", default="data/constellation_lines_simplified.dat", help="Input constellation lines file")
    ap.add_argument("-o", "--output", default="data/constellations_with_labels.json", help="Output JSON file")
    ap.add_argument("-v", "--verbose", action="store_true", help="Verbose; warn about missing HIPs")
    args = ap.parse_args()

    print("Loading star map from:", args.stars)
    star_map = load_star_positions(args.stars)
    print("Loaded star positions:", len(star_map))

    print("Parsing constellation lines from:", args.input)
    consts = parse_constellations(args.input, star_map, verbose=args.verbose)
    print("Parsed constellations (with lines):", len(consts))

    with open(args.output, "w", encoding="utf-8") as out:
        json.dump(consts, out, indent=2)

    print("Wrote:", args.output)

if __name__ == "__main__":
    main()

