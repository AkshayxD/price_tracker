import os, json

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}


def save_json(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)