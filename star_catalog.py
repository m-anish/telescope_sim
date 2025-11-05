import csv
import json
import math
from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta

def deg2rad(d):
    """Converts degrees to radians."""
    return d * math.pi / 180.0

def rad2deg(r):
    """Converts radians to degrees."""
    return r * 180.0 / math.pi

def ra_dec_to_cartesian(ra_deg, dec_deg):
    """
    Convert Right Ascension/Declination to Cartesian coordinates.
    
    Args:
        ra_deg: Right Ascension in degrees (0-360)
        dec_deg: Declination in degrees (-90 to +90)
    
    Returns:
        Tuple (x, y, z) representing unit vector on sphere
    """
    ra = deg2rad(ra_deg)
    dec = deg2rad(dec_deg)
    
    # Convert to Cartesian coordinates
    # Using standard astronomical convention:
    # X points to RA=0, Dec=0 (vernal equinox)
    # Y points to Dec=+90 (north celestial pole)  
    # Z points to RA=90, Dec=0
    x = math.cos(dec) * math.cos(ra)
    y = math.sin(dec)
    z = math.cos(dec) * math.sin(ra)
    
    return (x, y, z)


# --- Load ephemeris JSON ---
def load_ephemeris(json_path='data/ephemeris_2025_2030.json'):
    """
    Load the precomputed ephemeris JSON file.
    
    Returns:
        dict: contains 'start_date', 'step_days', and body coordinates.
    """
    with open(json_path, "r") as f:
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

# --- Helper function for computing ephemeris body position---
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


def load_bright_stars(csv_path="data/hyg_stars_4_0mag.csv"):
    """
    Load bright stars from CSV file.
    
    Returns:
        List of tuples (ra_deg, dec_deg, magnitude, name)
    """
    stars = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ra = float(row['RA_deg'])
            dec = float(row['Dec_deg'])
            mag = float(row['Magnitude'])
            name = row['Name'].strip() if row['Name'] else None
            stars.append((ra, dec, mag, name))
    return stars

def load_constellations(json_path="data/constellations.json"):
    """
    Load constellation data from JSON file.
    
    Returns:
        List of constellation dictionaries with name and lines
    """
    with open(json_path, 'r') as file:
        constellations = json.load(file)
    return constellations

def load_ephemeris_objects(json_path="data/ephemeris_2025_2030.json"):
    """
    Returns properly positioned ephemeris objects after loading JSON file
    and computing their RA/Dec for the current date.

    Returns:
        List of tuples (body_name, ra_deg, dec_deg)
    """
    ephem_data = load_ephemeris(json_path)
    bodies = load_ephemeris_bodies(ephem_data)
    now_utc = datetime.utcnow()
    ephem_objects = []
    for body in bodies:
        ra, dec = get_body_ra_dec(ephem_data, body, now_utc)
        ephem_objects.append((body, ra, dec))
    return ephem_objects

def load_messier_objects(json_path="data/messier.json"):
    """
    Load Messier objects from JSON file.
    
    Returns:
        List of tuples (messier_num, name, ra_deg, dec_deg, magnitude, type, dim_major_deg, dim_minor_deg)
    """
    # Type mapping from JSON abbreviations to full type names
    type_mapping = {
        "gc": "Globular Cluster",
        "oc": "Open Cluster", 
        "snr": "Supernova Remnant",
        "sfr": "Nebula",
        "pn": "Planetary Nebula",
        "s": "Spiral Galaxy",
        "e": "Elliptical Galaxy",
        "i": "Irregular Galaxy",
        "rn": "Reflection Nebula",
        "pos": "Asterism"
    }
    
    messiers = []
    with open(json_path, 'r') as file:
        data = json.load(file)
        for obj in data:
            m_num = obj['id']
            name = obj.get('name', '')  # Can be null in JSON
            ra = float(obj['ra'])
            dec = float(obj['dec'])
            mag = float(obj['mag'])
            obj_type = type_mapping.get(obj['type'], obj['type'])  # Map abbreviation to full name
            dim_major = obj.get('dim_major_deg')  # Can be null
            dim_minor = obj.get('dim_minor_deg')  # Can be null
            messiers.append((m_num, name, ra, dec, mag, obj_type, dim_major, dim_minor))
    return messiers

def get_stars_as_cartesian(stars):
    """
    Convert star list to Cartesian coordinates.
    
    Args:
        stars: List of (ra_deg, dec_deg, magnitude, name)
    
    Returns:
        List of (x, y, z, magnitude, name) tuples
    """
    cartesian_stars = []
    for ra, dec, mag, name in stars:
        x, y, z = ra_dec_to_cartesian(ra, dec)
        cartesian_stars.append((x, y, z, mag, name))
    return cartesian_stars

def get_constellation_lines_as_cartesian(constellations):
    """
    Convert constellation lines to Cartesian coordinates.
    
    Args:
        constellations: List of constellation dictionaries
    
    Returns:
        List of constellation dictionaries with Cartesian coordinates
    """
    cartesian_constellations = []
    for const in constellations:
        cartesian_lines = []
        for line in const["lines"]:
            (ra1, dec1), (ra2, dec2) = line
            x1, y1, z1 = ra_dec_to_cartesian(ra1, dec1)
            x2, y2, z2 = ra_dec_to_cartesian(ra2, dec2)
            cartesian_lines.append([(x1, y1, z1), (x2, y2, z2)])
        
        # Preserve the label field if it exists
        constellation_data = {
            "name": const["name"],
            "lines": cartesian_lines
        }
        if "label" in const:
            constellation_data["label"] = const["label"]
        
        cartesian_constellations.append(constellation_data)
    
    return cartesian_constellations

def get_ephemeris_objects_as_cartesian(ephem_objects):
    """
    Convert ephemeris objects to Cartesian coordinates.
    
    Args:
        ephem_objects: List of (body_name, ra_deg, dec_deg)
    
    Returns:
        List of (body_name, x, y, z) tuples
    """
    cartesian_ephem = []
    for body_name, ra, dec in ephem_objects:
        x, y, z = ra_dec_to_cartesian(ra, dec)
        cartesian_ephem.append((body_name, x, y, z))
    return cartesian_ephem

def get_messier_objects_as_cartesian(messiers):
    """
    Convert Messier objects to Cartesian coordinates.
    
    Args:
        messiers: List of (messier_num, name, ra_deg, dec_deg, magnitude, type, dim_major_deg, dim_minor_deg)
    
    Returns:
        List of (messier_num, name, x, y, z, magnitude, type, dim_major_deg, dim_minor_deg) tuples
    """
    cartesian_messiers = []
    for m_num, name, ra, dec, mag, obj_type, dim_major, dim_minor in messiers:
        x, y, z = ra_dec_to_cartesian(ra, dec)
        cartesian_messiers.append((m_num, name, x, y, z, mag, obj_type, dim_major, dim_minor))
    return cartesian_messiers
