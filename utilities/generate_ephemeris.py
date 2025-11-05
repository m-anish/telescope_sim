#!/usr/bin/python3
"""
Generate 5 years of RA/Dec data for Sun, Moon, and planets with variable step sizes.
Output JSON includes start_date, step_days, and body coordinates.

RA is in degrees (0–360), Dec in degrees (-90 to +90).
"""

import json
from datetime import date, timedelta
from skyfield.api import load

# --- Configuration ---
START_YEAR = 2025
YEARS = 5
OUTPUT_FILE = f"ephemeris_{START_YEAR}_{START_YEAR+YEARS}.json"

# --- Load ephemerides ---
eph = load("de440s.bsp")   # NASA JPL DE440 ephemeris
ts = load.timescale()
earth = eph[3]  # Earth barycenter as observer

# --- Bodies and step sizes (days) ---
# Use numeric codes for barycenters to avoid VectorSum issues
bodies = {
    "sun": eph[10],
    "moon": eph[301],
    "mercury": eph[1],
    "venus": eph[2],
    "mars": eph[4],
    "jupiter": eph[5],
    "saturn": eph[6],
    "uranus": eph[7],
    "neptune": eph[8],
    "pluto": eph[9]
}

step_days = {
    "sun": 1,
    "moon": 1,
    "mercury": 1,
    "venus": 1,
    "mars": 2,
    "jupiter": 7,
    "saturn": 10,
    "uranus": 30,
    "neptune": 30,
    "pluto": 30
}

# --- Generate date range ---
start_date = date(START_YEAR, 1, 1)
end_date = date(START_YEAR + YEARS, 1, 1)
total_days = (end_date - start_date).days
print(f"Generating ephemeris {START_YEAR}–{START_YEAR+YEARS} (~{total_days} days)...")

# --- Compute positions ---
data = {
    "start_date": start_date.isoformat(),
    "step_days": step_days
}

for name, body in bodies.items():
    print(f" → {name.capitalize()} (step {step_days[name]}d)")
    coords = []
    i = 0
    while True:
        current_date = start_date + timedelta(days=i)
        if current_date >= end_date:
            break
        t = ts.utc(current_date.year, current_date.month, current_date.day)
        # Fixed: use .at(t).observe(body).apparent() for planets & Sun
        astrometric = earth.at(t).observe(body).apparent()
        ra, dec, _ = astrometric.radec()
        coords.append([round(ra.hours*15,6), round(dec.degrees,6)])  # RA in degrees
        i += step_days[name]
    data[name] = coords

# --- Write JSON ---
with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, separators=(',', ':'))

print(f"✅ Wrote {OUTPUT_FILE} ({len(bodies)} bodies, start_date: {start_date.isoformat()})")

