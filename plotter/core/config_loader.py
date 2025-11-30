import yaml
from pathlib import Path

def load_param_config():
    
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"[ERROR] config.yaml not found at: {config_path}")
    
    with open(config_path, "r") as f:
        print(f"[INFO] Loading config file: {config_path}")
        return yaml.safe_load(f)
