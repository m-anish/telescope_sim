#!/usr/bin/python3
"""
Helper module to load precomputed planetary ephemeris JSON and compute RA/Dec
for any body and UTC datetime using linear interpolation.
"""

import json
from datetime import datetime, timedelta

# --- Load ephemeris JSON ---
def load_ephemeris(json_file):
    """
    Load the precomputed ephemeris JSON file.
    
    Returns:
        dict: contains 'start_date', 'step_days', and body coordinates.
    """
    with open(json_file, "r") as f:
        data = json.load(f)
    
    # Convert start_date to datetime
    data["start_date"] = datetime.strptime(data["start_date"], "%Y-%m-%d")
    return data

def load_ephemeris_bodies(data):
    """
    Load the list of ephemeris bodies from a json formatted data object.

    Returns:
        List of body names (str) present in the ephemeris
    """
 
    # Bodies are all keys except 'start_date' and 'step_days'
    bodies = [key for key in data.keys() if key not in ("start_date", "step_days")]
    return bodies

# --- Helper function ---
def get_body_ra_dec(ephem_data, body_name, utc_datetime):
    """
    Get RA/Dec of a given body at a specific UTC datetime using linear interpolation.

    Args:
        ephem_data (dict): loaded ephemeris data from load_ephemeris().
        body_name (str): name of the body ('moon', 'mars', etc.).
        utc_datetime (datetime): UTC datetime.

    Returns:
        tuple: (ra_deg, dec_deg)
    """
    if body_name not in ephem_data:
        raise ValueError(f"Body '{body_name}' not found in ephemeris.")
    
    start = ephem_data["start_date"]
    step = ephem_data["step_days"][body_name]
    coords = ephem_data[body_name]

    delta_days = (utc_datetime - start).total_seconds() / 86400.0
    if delta_days < 0 or delta_days > (len(coords)-1)*step:
        raise ValueError("UTC datetime out of ephemeris range.")

    # Find indices for linear interpolation
    idx_lower = int(delta_days // step)
    idx_upper = min(idx_lower + 1, len(coords)-1)
    fraction = (delta_days - idx_lower*step) / step

    ra_lower, dec_lower = coords[idx_lower]
    ra_upper, dec_upper = coords[idx_upper]

    # Linear interpolation
    ra_interp = ra_lower + fraction * (ra_upper - ra_lower)
    dec_interp = dec_lower + fraction * (dec_upper - dec_lower)

    # Normalize RA to 0-360
    ra_interp = ra_interp % 360

    return ra_interp, dec_interp

# --- Example usage ---
if __name__ == "__main__":
    ephem_file = "./data/ephemeris_2025_2030.json"  # adjust path as needed
    ephem = load_ephemeris(ephem_file)
    bodies = load_ephemeris_bodies(ephem)
    print("Loaded ephemeris for bodies:", bodies)

    now_utc = datetime.utcnow()

    for body in bodies:
        ra, dec = get_body_ra_dec(ephem, body, now_utc)
        print(f"{body.capitalize()} RA: {ra:.6f}°, Dec: {dec:.6f}° (UTC {now_utc})")
