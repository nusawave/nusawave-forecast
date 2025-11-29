import yaml
from pathlib import Path

def load_param_config(path="../configs/params.yaml"):
    if not Path(path).exists():
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f)
