import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent / "config"

def load_yaml(name: str):
    path = CONFIG_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {name}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

ENFORCEMENT_CONFIG = load_yaml("enforcement.yaml")
RUNTIME_CONFIG = load_yaml("runtime.yaml")
