#!/usr/bin/env python3
"""
Test script to verify star and messier name functionality.
"""

import star_catalog

def test_star_names():
    """Test that star names are loaded correctly."""
    print("Testing star names loading...")
    
    # Load bright stars
    bright_stars = star_catalog.load_bright_stars()
    print(f"Loaded {len(bright_stars)} stars from CSV")
    
    # Check first few stars
    print("\nFirst 10 stars:")
    for i, star in enumerate(bright_stars[:10]):
        ra, dec, mag, name = star
        print(f"  {i+1}. RA={ra:.2f}, Dec={dec:.2f}, Mag={mag:.2f}, Name='{name}'")
    
    # Count stars with names
    stars_with_names = [s for s in bright_stars if s[3] and s[3].strip()]
    print(f"\nStars with names: {len(stars_with_names)}")
    print(f"Stars without names: {len(bright_stars) - len(stars_with_names)}")
    
    # Count bright stars (mag < 2) with names
    bright_stars_with_names = [s for s in bright_stars if s[2] < 2.0 and s[3] and s[3].strip()]
    print(f"Bright stars (mag < 2) with names: {len(bright_stars_with_names)}")
    
    # Show some bright stars with names
    print("\nBright stars (mag < 2) with names:")
    for i, star in enumerate(bright_stars_with_names[:10]):
        ra, dec, mag, name = star
        print(f"  {i+1}. {name}: Mag={mag:.2f}")
    
    # Convert to Cartesian and test
    cartesian_stars = star_catalog.get_stars_as_cartesian(bright_stars)
    print(f"\nConverted {len(cartesian_stars)} stars to Cartesian coordinates")
    
    # Check first few Cartesian stars
    print("\nFirst 5 Cartesian stars:")
    for i, star in enumerate(cartesian_stars[:5]):
        x, y, z, mag, name = star
        print(f"  {i+1}. ({x:.3f}, {y:.3f}, {z:.3f}), Mag={mag:.2f}, Name='{name}'")

def test_messier_names():
    """Test that Messier object names are loaded correctly."""
    print("\n" + "="*50)
    print("Testing Messier object names loading...")
    
    # Load Messier objects
    messiers = star_catalog.load_messier_objects()
    print(f"Loaded {len(messiers)} Messier objects from JSON")
    
    # Check first few Messier objects
    print("\nFirst 10 Messier objects:")
    for i, messier in enumerate(messiers[:10]):
        m_num, name, ra, dec, mag, obj_type, dim_major, dim_minor = messier
        print(f"  {i+1}. M{m_num}: '{name}', RA={ra:.2f}, Dec={dec:.2f}, Mag={mag:.2f}, Type={obj_type}")
    
    # Count Messier objects with names
    messiers_with_names = [m for m in messiers if m[1] and m[1].strip()]
    print(f"\nMessier objects with names: {len(messiers_with_names)}")
    print(f"Messier objects without names: {len(messiers) - len(messiers_with_names)}")
    
    # Count bright Messier objects (mag < 5) with names
    bright_messiers_with_names = [m for m in messiers if m[4] < 5.0 and m[1] and m[1].strip()]
    print(f"Bright Messier objects (mag < 5) with names: {len(bright_messiers_with_names)}")
    
    # Show some bright Messier objects with names
    print("\nBright Messier objects (mag < 5) with names:")
    for i, messier in enumerate(bright_messiers_with_names[:10]):
        m_num, name, ra, dec, mag, obj_type, dim_major, dim_minor = messier
        print(f"  {i+1}. M{m_num} {name}: Mag={mag:.2f}")
    
    # Convert to Cartesian and test
    cartesian_messiers = star_catalog.get_messier_objects_as_cartesian(messiers)
    print(f"\nConverted {len(cartesian_messiers)} Messier objects to Cartesian coordinates")
    
    # Check first few Cartesian Messier objects
    print("\nFirst 5 Cartesian Messier objects:")
    for i, messier in enumerate(cartesian_messiers[:5]):
        m_num, name, x, y, z, mag, obj_type, dim_major, dim_minor = messier
        print(f"  {i+1}. M{m_num} {name}: ({x:.3f}, {y:.3f}, {z:.3f}), Mag={mag:.2f}")

if __name__ == "__main__":
    test_star_names()
    test_messier_names()
    print("\n" + "="*50)
    print("Test completed successfully!")
