import random
import math

def random_sphere_points(n):
    """Generates n random points on the surface of a unit sphere."""
    pts = []
    for _ in range(n):
        # Using spherical coordinates to generate points uniformly on a sphere
        # Generate random altitude (y-coordinate)
        z = random.uniform(-1.0, 1.0)
        # Generate random azimuth (angle around the y-axis)
        az = random.uniform(0.0, 2.0 * math.pi)
        # Calculate radius in the x-z plane
        r = math.sqrt(1.0 - z * z)
        # Convert spherical to Cartesian coordinates
        x = r * math.cos(az)
        y = r * math.sin(az)
        pts.append((x, y, z))
    return pts

def generate_star_sizes(n):
    """Generates random sizes for n stars, with some larger ones."""
    # A simple distribution: most stars are size 1, some are size 2.
    return [random.choice((1, 1, 1, 2)) for _ in range(n)]
