import json
from pathlib import Path

# Fichier de seeds / constantes globales
SEEDS_PATH = Path(__file__).resolve().parents[1] / "seeds.json"

DEFAULT_CONSTANTS = {
    "random_seed": 42,
}

try:
    with SEEDS_PATH.open("r", encoding="utf-8") as f:
        CONSTANTS = json.load(f)
except FileNotFoundError:
    CONSTANTS = DEFAULT_CONSTANTS
