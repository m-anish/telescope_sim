#!/usr/bin/env python3
"""
constellation_parser_fixed.py

Parse a variety of "constellation lines" file formats (plain HIP pairs,
chains, JSON-like lists, comma-separated lists) and resolve HIP -> RA/Dec
using a HYG CSV (hyg_all_stars.csv). Output JSON with coordinate pairs.

Usage:
    python3 constellation_parser_fixed.py \
      -s data/hyg_all_stars.csv \
      -i data/constellation_lines_simplified.dat \
      -o data/constellations.json
"""

import csv
import json
import argparse
import ast
import re
from collections import OrderedDict

def load_star_coords(hyg_csv):
    """
    Load star RA/Dec by HIP number into dict: {int(hip): (ra_deg, dec_deg)}
    Accepts CSV with header HIP or hip and RA_deg/Dec_deg or ra/dec.
    """
    stars = {}
    with open(hyg_csv, encoding="utf-8", newline='') as f:
        reader = csv.DictReader(f)
        # normalize possible header names
        for row in reader:
            # find hip key
            hip_key = None
            for k in ("HIP","hip","hipparcos","hip_nr","hipnum"):
                if k in row and row[k] not in (None, ""):
                    hip_key = k
                    break
            if not hip_key:
                # try first numeric column name that looks like hip
                keys = list(row.keys())
                if keys:
                    hip_key = keys[0]
            try:
                hip_val = row.get(hip_key, "").strip()
                if hip_val == "":
                    continue
                hip = int(float(hip_val))
            except Exception:
                continue

            # ra/dec column possibilities
            ra = None; dec = None
            for rk in ("RA_deg","ra_deg","ra","RA"):
                if rk in row and row[rk] not in ("", None):
                    try:
                        ra = float(row[rk])
                        break
                    except Exception:
                        pass
            for dk in ("Dec_deg","dec_deg","dec","DEC","Dec"):
                if dk in row and row[dk] not in ("", None):
                    try:
                        dec = float(row[dk])
                        break
                    except Exception:
                        pass
            # fallback to columns named 'x','y','z' are not used here
            if ra is None or dec is None:
                continue
            stars[hip] = (ra, dec)
    return stars

def parse_line_to_hips(line):
    """
    Accept many formats and return a list of HIP ints (possibly empty):
    - "12345 23456" -> [12345, 23456]
    - "12345,23456,34567" -> [12345,23456,34567]
    - '["12345","23456"]' -> [12345,23456] (via ast.literal_eval)
    - may contain quotes, extra punctuation -> extract ints via regex as fallback
    """
    line = line.strip()
    if not line:
        return []
    # try ast literal eval for JSON-like lists
    if line.startswith("[") and line.endswith("]"):
        try:
            arr = ast.literal_eval(line)
            hip_list = []
            for v in arr:
                try:
                    hip_list.append(int(float(v)))
                except Exception:
                    # maybe it's "HIP:12345" or similar; try regex fallback later
                    pass
            if hip_list:
                return hip_list
        except Exception:
            pass

    # try splitting by commas or whitespace
    # first replace commas with spaces, then split
    cleaned = line.replace(",", " ").replace(";", " ")
    parts = cleaned.split()
    hips = []
    for p in parts:
        # strip surrounding quotes or punctuation
        pstr = p.strip("[]\"'(){}<>")
        # accept only numeric-looking tokens
        if re.fullmatch(r'\d+(\.\d+)?', pstr):
            try:
                hips.append(int(float(pstr)))
            except Exception:
                pass
    if hips:
        return hips

    # final fallback: extract all integers by regex
    ints = re.findall(r'\d+', line)
    return [int(x) for x in ints]

def parse_constellations(lines_file, star_coords):
    """
    Parse an input file where constellation sections are separated by a header line
    and subsequent lines contain HIP pairs, chains, or lists. The function produces
    a list of dicts: {"name": "Orion", "lines": [ [ [ra,dec],[ra,dec] ], ... ] }
    """
    constellations = []
    current = None

    with open(lines_file, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#") or line.lower().startswith("!"):
                continue

            # If a header-like line (contains letters and not many digits), treat as new constellation
            # also treat lines starting with '*' or '//' or alphabetic tokens as headers
            header_like = False
            # Consider it header when it contains letters and few or no digits
            digits = re.findall(r'\d+', line)
            letters = re.findall(r'[A-Za-z]', line)
            if len(letters) > 0 and len(digits) < 2:
                header_like = True

            if header_like:
                # finish previous
                if current:
                    constellations.append(current)
                # clean name: remove leading '*' or punctuation, trailing comments
                name = line.strip().lstrip("*").strip()
                # if name contains extra tokens, keep first token sequence of letters and spaces
                name = re.sub(r'\s{2,}', ' ', name)
                current = {"name": name, "lines": []}
                continue

            # otherwise try to parse HIP ints from the line
            hips = parse_line_to_hips(line)
            if not hips:
                # nothing numeric; skip
                continue

            # If exactly two -> add one segment
            if len(hips) == 2:
                a, b = hips[0], hips[1]
                if a in star_coords and b in star_coords:
                    p1 = star_coords[a]; p2 = star_coords[b]
                    current["lines"].append([list(p1), list(p2)])
                else:
                    # skip but optionally log missing hips
                    pass
            elif len(hips) >= 3:
                # chain: connect consecutive hips
                for i in range(len(hips) - 1):
                    a, b = hips[i], hips[i+1]
                    if a in star_coords and b in star_coords:
                        current["lines"].append([list(star_coords[a]), list(star_coords[b])])
                    else:
                        # skip if coordinate missing
                        pass
            else:
                # single HIP only -> nothing to draw
                pass

    if current:
        constellations.append(current)
    return constellations

def main():
    parser = argparse.ArgumentParser(description="Parse constellation lines file into JSON coords")
    parser.add_argument("-s","--stars", default="data/hyg_stars_all.csv", help="HYG CSV with HIP, RA_deg, Dec_deg")
    parser.add_argument("-i","--input", default="data/constellation_lines_simplified.dat", help="Input lines file")
    parser.add_argument("-o","--output", default="data/constellations.json", help="Output JSON file")
    args = parser.parse_args()

    print("Loading star coords from:", args.stars)
    star_coords = load_star_coords(args.stars)
    print("Loaded", len(star_coords), "stars")

    print("Parsing constellations from:", args.input)
    consts = parse_constellations(args.input, star_coords)
    print("Parsed", len(consts), "constellations")

    # Remove any constellations that have no lines
    consts = [c for c in consts if c.get("lines")]

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(consts, f, indent=2)

    print("Wrote", args.output)

if __name__ == "__main__":
    main()

