import csv
import json
import math
from typing import List, Tuple, Dict, Any

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

def load_bright_stars(csv_path="data/bright_stars_mag4p5.csv"):
    """
    Load bright stars from CSV file.
    
    Returns:
        List of tuples (ra_deg, dec_deg, magnitude)
    """
    stars = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ra = float(row['RA_deg'])
            dec = float(row['Dec_deg'])
            mag = float(row['Magnitude'])
            stars.append((ra, dec, mag))
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

def load_messier_objects(csv_path="data/messier.csv"):
    """
    Load Messier objects from CSV file.
    
    Returns:
        List of tuples (messier_num, name, ra_deg, dec_deg, magnitude, type)
    """
    messiers = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            m_num = row['name']
            name = row.get('common_name', '')
            ra = float(row['ra_deg'])
            dec = float(row['dec_deg'])
            mag = float(row['mag'])
            obj_type = row['type']
            messiers.append((m_num, name, ra, dec, mag, obj_type))
    return messiers

def get_stars_as_cartesian(stars):
    """
    Convert star list to Cartesian coordinates.
    
    Args:
        stars: List of (ra_deg, dec_deg, magnitude)
    
    Returns:
        List of (x, y, z, magnitude) tuples
    """
    cartesian_stars = []
    for ra, dec, mag in stars:
        x, y, z = ra_dec_to_cartesian(ra, dec)
        cartesian_stars.append((x, y, z, mag))
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
        
        cartesian_constellations.append({
            "name": const["name"],
            "abbrev": const["abbrev"],
            "lines": cartesian_lines
        })
    
    return cartesian_constellations

def get_messier_objects_as_cartesian(messiers):
    """
    Convert Messier objects to Cartesian coordinates.
    
    Args:
        messiers: List of (messier_num, name, ra_deg, dec_deg, magnitude, type)
    
    Returns:
        List of (messier_num, name, x, y, z, magnitude, type) tuples
    """
    cartesian_messiers = []
    for m_num, name, ra, dec, mag, obj_type in messiers:
        x, y, z = ra_dec_to_cartesian(ra, dec)
        cartesian_messiers.append((m_num, name, x, y, z, mag, obj_type))
    return cartesian_messiers
