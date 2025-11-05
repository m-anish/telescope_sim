#!/usr/bin/python3
import json
import argparse
import os

def parse_dim_to_deg(dim_str):
    """Parse dimension like '6x4' or '190x60' arcmin → degrees."""
    if not dim_str:
        return None, None
    parts = str(dim_str).lower().replace("′", "").replace("'", "").split("x")
    try:
        if len(parts) == 2:
            major = float(parts[0]) / 60.0
            minor = float(parts[1]) / 60.0
        elif len(parts) == 1:
            major = minor = float(parts[0]) / 60.0
        else:
            return None, None
        return major, minor
    except ValueError:
        return None, None


def parse_messier_geojson(input_file, output_file=None):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    results = []

    for feat in features:
        prop = feat.get("properties", {})
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [None, None])

        ra = coords[0]
        dec = coords[1]
        id_ = prop.get("id")
        ngc = prop.get("desig")
        name = prop.get("alt")
        obj_type = prop.get("type")
        mag = prop.get("mag")
        dim_str = prop.get("dim")

        dim_major, dim_minor = parse_dim_to_deg(dim_str)

        results.append({
            "id": id_,
            "ngc": ngc,
            "name": name,
            "type": obj_type,
            "ra": ra,
            "dec": dec,
            "mag": mag,
            "dim_major_deg": dim_major,
            "dim_minor_deg": dim_minor
        })

    # Determine output file path
    if not output_file:
        base_dir = os.path.dirname(input_file)
        output_file = os.path.join(base_dir, "messier.json")

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(results, out, indent=2)

    print(f"✅ Wrote {len(results)} objects to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Parse Messier GeoJSON file and output simplified JSON with RA/Dec and angular size in degrees."
    )
    parser.add_argument(
        "-i", "--input",
        default="data/messier.geojson",
        help="Input Messier GeoJSON file (default: data/messier.geojson)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output JSON file (default: messier.json in same directory)"
    )

    args = parser.parse_args()
    parse_messier_geojson(args.input, args.output)


if __name__ == "__main__":
    main()

