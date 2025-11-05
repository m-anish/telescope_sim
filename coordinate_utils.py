#!/usr/bin/python3
"""
Helper function to convert RA/Dec (degrees) to Alt/Az given observer location and UTC time.
"""

import math
from datetime import datetime, timezone

# --- Helper functions ---
def ra_dec_to_alt_az(ra_deg, dec_deg, observer_lat_deg, observer_lon_deg, utc_datetime):
    """
    Convert RA/Dec in degrees to Altitude/Azimuth for a given observer location and UTC datetime.

    Args:
        ra_deg (float): Right Ascension in degrees (0-360)
        dec_deg (float): Declination in degrees (-90 to +90)
        observer_lat_deg (float): Observer latitude in degrees (+N)
        observer_lon_deg (float): Observer longitude in degrees (+E)
        utc_datetime (datetime): UTC datetime

    Returns:
        tuple: (alt_deg, az_deg) in degrees
            - alt_deg: Altitude (0° = horizon, +90° = zenith)
            - az_deg: Azimuth (0° = North, 90° = East, 180° = South, 270° = West)
    """
    # --- Convert to radians ---
    ra = math.radians(ra_deg)
    dec = math.radians(dec_deg)
    lat = math.radians(observer_lat_deg)
    lon = math.radians(observer_lon_deg)

    # --- Compute Julian Date ---
    jd = julian_date(utc_datetime)

    # --- Greenwich Sidereal Time (in radians) ---
    gst = greenwich_sidereal_time(jd)

    # Local Sidereal Time
    lst = (gst + lon) % (2 * math.pi)

    # Hour angle
    ha = (lst - ra) % (2 * math.pi)

    # Altitude
    sin_alt = math.sin(dec) * math.sin(lat) + math.cos(dec) * math.cos(lat) * math.cos(ha)
    alt = math.asin(sin_alt)

    # Azimuth
    cos_az = (math.sin(dec) - math.sin(alt) * math.sin(lat)) / (math.cos(alt) * math.cos(lat))
    # clamp to [-1,1] to avoid rounding errors
    cos_az = max(min(cos_az, 1.0), -1.0)
    az = math.acos(cos_az)

    # Determine correct quadrant for azimuth
    if math.sin(ha) > 0:
        az = 2 * math.pi - az

    return math.degrees(alt), math.degrees(az)


# --- Julian Date ---
def julian_date(dt):
    """Compute Julian Date from UTC datetime"""
    dt = dt.replace(tzinfo=timezone.utc)
    year = dt.year
    month = dt.month
    day = dt.day + dt.hour / 24 + dt.minute / 1440 + dt.second / 86400
    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    return jd

# --- Greenwich Sidereal Time ---
def greenwich_sidereal_time(jd):
    """
    Compute Greenwich Sidereal Time in radians for given Julian Date.
    Formula approximate, sufficient for telescope pointing.
    """
    T = (jd - 2451545.0) / 36525
    # GST in degrees
    gst_deg = 280.46061837 + 360.98564736629 * (jd - 2451545.0) \
              + 0.000387933 * T**2 - T**3 / 38710000
    gst_deg = gst_deg % 360
    return math.radians(gst_deg)


# --- Example usage ---
if __name__ == "__main__":
    # Example: RA/Dec of Moon at some date
    ra_deg = 134.6885
    dec_deg = 13.7684
    lat = 37.7749   # San Francisco
    lon = -122.4194

    utc_now = datetime.utcnow()
    alt, az = ra_dec_to_alt_az(ra_deg, dec_deg, lat, lon, utc_now)
    print(f"Alt: {alt:.2f}°, Az: {az:.2f}° (UTC {utc_now})")

