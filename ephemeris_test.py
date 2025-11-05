import json

def load_ephemeris_bodies(json_path="data/ephemeris_2025_2030.json"):
    """
    Load the list of ephemeris bodies from a JSON file.

    Returns:
        List of body names (str) present in the ephemeris
    """
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    # Bodies are all keys except 'start_date' and 'step_days'
    bodies = [key for key in data.keys() if key not in ("start_date", "step_days")]
    return bodies