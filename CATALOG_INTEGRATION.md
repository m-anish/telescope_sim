# Star Catalog Integration

This document describes the integration of real astronomical catalog data into the telescope simulator.

## Overview

The telescope simulator now uses real star positions from astronomical catalogs instead of randomly generated stars. This provides a more realistic and educational experience showing actual star positions, constellations, and deep-sky objects.

## Data Sources

### Bright Stars (`data/hyg_stars_4_0mag.csv`)
- Contains bright stars with magnitude ≤ 4.0 from HYG database
- Fields: HIP, Name, RA_deg, Dec_deg, Magnitude
- Source: HYG (Hipparcos-Yale-Gliese) stellar database
- Includes both numbered stars (HIP catalog) and named stars like Sirius, Vega, etc.

### Constellations (`data/constellations.json`)
- Contains 25 major constellations with connecting lines
- Fields: name, abbrev, lines (array of RA/Dec coordinate pairs)
- Shows constellation patterns as traditionally drawn

### Messier Objects (`data/messier.json`)
- Contains 110 Messier objects (M1-M110)
- Fields: id, ra, dec, mag, type, name, ngc, dim_major_deg, dim_minor_deg
- Includes galaxies, nebulae, star clusters, and other deep-sky objects
- Uses abbreviated type codes (gc= Globular Cluster, oc=Open Cluster, etc.)

## Implementation

### New Modules

#### `star_catalog.py`
- Loads and parses catalog data files
- Converts RA/Dec coordinates to Cartesian coordinates
- Provides functions for all three data types

#### `sample_draw_utilities.py` (enhanced)
- Drawing functions for catalog objects
- Integrates with existing camera system
- Handles magnitude-based sizing and brightness

#### `input_handler.py` (enhanced)
- Added toggle functionality for catalog objects
- Keyboard shortcuts: S (stars), C (constellations), M (Messier objects)
- Maintains existing camera controls

### Coordinate System

The system uses Right Ascension (RA) and Declination (Dec) coordinates:
- **RA**: 0-360° measured eastward along the celestial equator
- **Dec**: -90° to +90° measured from celestial equator

These are converted to Cartesian coordinates for the 3D rendering system:
- **X**: Points to RA=0°, Dec=0° (vernal equinox)
- **Y**: Points to Dec=+90° (north celestial pole)
- **Z**: Points to RA=90°, Dec=0°

### Rendering

- **Stars**: Size and brightness based on magnitude (brighter = bigger/brighter)
- **Constellations**: Blue lines connecting stars in traditional patterns
- **Messier Objects**: Orange circles with yellow outlines for visibility

## Usage

### Running the Simulator
```bash
python3 main.py
```

The simulator will:
1. Load catalog data from the `data/` folder
2. Display real star positions instead of random stars
3. Show constellation lines and Messier objects
4. Fall back to random stars if catalog loading fails

### Controls
```
Arrow keys/WASD: Rotate camera
+/-: Zoom in/out
S: Toggle stars (ON/OFF)
C: Toggle constellations (ON/OFF)
M: Toggle Messier objects (ON/OFF)
ESC: Quit
```

### Testing
Run the integration test:
```bash
python3 test_catalog_integration.py
```

This verifies:
- Catalog data loading
- Coordinate conversion accuracy
- Camera projection functionality

## File Structure

```
├── data/
│   ├── hyg_stars_4_0mag.csv        # HYG bright star catalog
│   ├── constellations.json            # Constellation patterns
│   └── messier.json                  # Messier objects
├── star_catalog.py                   # Catalog loading and conversion
├── sample_draw_utilities.py          # Enhanced drawing functions
├── input_handler.py                 # Enhanced input with toggles
├── main.py                         # Updated main application
├── starfield_random.py              # Backup of random star generator
└── test_catalog_integration.py      # Integration tests
```

## Features

### Realistic Star Positions
- Stars appear in their actual celestial positions
- Proper relative brightness based on magnitude
- Accurate constellation patterns
- 518 bright stars from HYG database (magnitude ≤ 4.0)

### Interactive Display Control
- Toggle individual catalog layers on/off
- Focus on specific types of objects
- Customize viewing experience

### Educational Value
- Learn to identify real constellations
- Understand celestial coordinate systems
- Explore deep-sky objects (Messier catalog)
- Recognize bright stars by their proper names

### Performance
- Efficient rendering of catalog data
- Fallback to random stars if needed
- Maintains smooth camera controls
- Toggle functionality to improve performance when needed

## Future Enhancements

Potential improvements:
- Additional star catalogs (fainter stars)
- More constellations and asterisms
- NGC/IC deep-sky object catalogs
- Star labels and information
- Search functionality for specific objects
- Time-based position updates (proper motion)
- Different projection modes
- Object information on hover/click

## Troubleshooting

### Common Issues

1. **Catalog loading fails**: Check that data files exist in `data/` folder
2. **Stars not visible**: Try adjusting camera position (arrow keys)
3. **Performance issues**: Use toggle keys to hide unnecessary objects
4. **Toggle not working**: Make sure to press keys once (not hold)

### Debug Mode

The application prints loading information:
```
Loading star catalog data...
Loaded 518 bright stars
Loaded 25 constellations
Loaded 110 Messier objects
```

Toggle status is printed when keys are pressed:
```
Stars: ON/OFF
Constellations: ON/OFF
Messier objects: ON/OFF
```

If you see error messages, the system will fall back to random stars.
