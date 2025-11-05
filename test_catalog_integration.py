#!/usr/bin/env python3
"""
Test script to verify catalog integration and coordinate conversion.
"""

import star_catalog
import tracker

def test_coordinate_conversion():
    """Test that RA/Dec coordinates are properly converted."""
    print("Testing coordinate conversion...")
    
    # Test some well-known stars
    test_stars = [
        ("Sirius", 101.287, -16.716, -1.46),
        ("Polaris", 37.954, 89.264, 1.98),
        ("Vega", 279.234, 38.7837, 0.03),
    ]
    
    for name, ra, dec, mag in test_stars:
        # Convert to Cartesian
        x, y, z = star_catalog.ra_dec_to_cartesian(ra, dec)
        
        # Verify it's a unit vector
        length = (x*x + y*y + z*z) ** 0.5
        print(f"{name}: RA={ra:.1f}°, Dec={dec:.1f}°")
        print(f"  Cartesian: ({x:.3f}, {y:.3f}, {z:.3f})")
        print(f"  Length: {length:.6f} (should be ~1.0)")
        
        # Test camera transformation
        camera = tracker.Camera(60, 800, 600)
        vc = camera.world_to_camera((x, y, z))
        p = camera.project(vc)
        
        if p:
            print(f"  Screen projection: ({p[0]:.1f}, {p[1]:.1f}) at depth {p[2]:.2f}")
        else:
            print(f"  Behind camera")
        print()

def test_catalog_loading():
    """Test that catalog data loads correctly."""
    print("Testing catalog loading...")
    
    try:
        # Load stars
        stars = star_catalog.load_bright_stars()
        print(f"Loaded {len(stars)} stars")
        
        # Load constellations
        constellations = star_catalog.load_constellations()
        print(f"Loaded {len(constellations)} constellations")
        
        # Load Messier objects
        messiers = star_catalog.load_messier_objects()
        print(f"Loaded {len(messiers)} Messier objects")
        
        # Test conversion to Cartesian
        stars_cartesian = star_catalog.get_stars_as_cartesian(stars)
        print(f"Converted {len(stars_cartesian)} stars to Cartesian")
        
        constellations_cartesian = star_catalog.get_constellation_lines_as_cartesian(constellations)
        total_lines = sum(len(const["lines"]) for const in constellations_cartesian)
        print(f"Converted {total_lines} constellation lines to Cartesian")
        
        messiers_cartesian = star_catalog.get_messier_objects_as_cartesian(messiers)
        print(f"Converted {len(messiers_cartesian)} Messier objects to Cartesian")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Catalog Integration Test ===\n")
    
    # Test catalog loading
    if test_catalog_loading():
        print("\n=== Coordinate Conversion Test ===\n")
        test_coordinate_conversion()
    else:
        print("Catalog loading failed - skipping coordinate tests")
