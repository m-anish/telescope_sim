#!/usr/bin/env python3
"""
hyg_parser_final.py

Parses HYG star catalog (v4.0–v4.2 and similar variants).
Automatically detects delimiter and RA units (hours vs degrees).

Outputs a clean CSV:
    HIP,Name,RA_deg,Dec_deg,Magnitude

Usage:
    python3 hyg_parser_final.py -i data/hygdata_v41_top.csv
    python3 hyg_parser_final.py -i data/hyg_v42.csv.gz -m 4.5
"""

import csv
import argparse
import gzip
import os

def detect_delimiter(filename, sample_bytes=4096):
    """Detect if file uses ';' or ',' as delimiter."""
    with (gzip.open(filename, "rt", encoding="utf-8", errors="ignore")
          if filename.endswith(".gz")
          else open(filename, "r", encoding="utf-8", errors="ignore")) as f:
        sample = f.read(sample_bytes)
        semis = sample.count(";")
        commas = sample.count(",")
    return ";" if semis > commas else ","

def detect_ra_units(rows, key="RA"):
    """Detect if RA is in hours or degrees. Returns multiplier."""
    vals = []
    for r in rows:
        try:
            ra = float(r[key])
            vals.append(ra)
        except Exception:
            pass
        if len(vals) >= 10:
            break
    if not vals:
        return 1.0
    # if RA values cluster in 0–24 range, assume hours
    avg = sum(vals) / len(vals)
    return 15.0 if avg < 24.1 else 1.0

def parse_hyg(input_file, mag_limit=None, output_file=None):
    """Parse HYG database and write clean CSV."""
    opener = gzip.open if input_file.endswith(".gz") else open
    delimiter = detect_delimiter(input_file)

    if output_file is None:
        base_dir = os.path.dirname(input_file) or "."
        mag_str = "all" if mag_limit is None else str(mag_limit).replace(".", "_")
        output_file = os.path.join(base_dir, f"hyg_bright_{mag_str}mag.csv")

    # Pre-scan a few rows to detect RA units
    with opener(input_file, "rt", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = [next(reader) for _ in range(10)]  # read first 10 rows
        ra_key = "RA" if "RA" in rows[0] else None
        if not ra_key:
            raise KeyError("Cannot find RA column in input file")
        multiplier = detect_ra_units(rows, ra_key)
    print(f"🧭 Detected delimiter '{delimiter}' and RA unit multiplier {multiplier}x")

    # Parse full file
    stars = []
    with opener(input_file, "rt", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            try:
                hip = (row.get("Hipparcos cat. ID")
                       or row.get("HIP")
                       or row.get("hip")
                       or "").strip()
                if not hip:
                    continue
                ra = float(row[ra_key]) * multiplier
                dec = float(row["Dec"])
                mag = float(row["Magnitude"])
                name = row.get("Proper", "").strip()
                if mag_limit is not None and mag > mag_limit:
                    continue
                stars.append((hip, name, ra, dec, mag))
            except Exception:
                continue

    with open(output_file, "w", newline="", encoding="utf-8") as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(["HIP", "Name", "RA_deg", "Dec_deg", "Magnitude"])
        writer.writerows(stars)

    print(f"✅ Wrote {len(stars)} stars to {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Parse HYG star catalog robustly.")
    parser.add_argument("-i", "--input", required=True, help="Input HYG CSV (.csv or .csv.gz)")
    parser.add_argument("-m", "--mag", type=float, default=None, help="Magnitude limit (omit for all stars)")
    parser.add_argument("-o", "--output", help="Output CSV filename")
    args = parser.parse_args()

    parse_hyg(args.input, args.mag, args.output)


if __name__ == "__main__":
    main()

