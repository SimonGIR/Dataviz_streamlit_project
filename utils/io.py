# utils/io.py
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import requests
import streamlit as st

from utils.prep import harmonize_chunk

# ---------------------------------------------------------------------
# Paramètres généraux
# ---------------------------------------------------------------------

BASE_URL_STABLE = "https://www.data.gouv.fr/api/1/datasets/r/"

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# Meta-données des ressources BAAC
RESOURCES: Dict[str, Dict[str, dict]] = {
    "usagers": {
        "2023": {
            "id": "68848e2a-28dd-4efc-9d5f-d512f7dbe66f",
            "filename": "usagers-2023.csv",
            "sep": ";",
        },
        "2022": {
            "id": "62c20524-d442-46f5-bfd8-982c59763ec8",
            "filename": "usagers-2022.csv",
            "sep": ";",
        },
    },
    "caract": {
        "2023": {
            "id": "104dbb32-704f-4e99-a71e-43563cb604f2",
            "filename": "caract-2023.csv",
            "sep": ";",
            "decimal": ",",
        },
        "2022": {
            "id": "5fc299c0-4598-4c29-b74c-6a67b0cc27e7",
            "filename": "caract-2022.csv",
            "sep": ";",
            "decimal": ",",
        },
    },
    "vehicules": {
        "2023": {
            "id": "146a42f5-19f0-4b3e-a887-5cd8fbef057b",
            "filename": "vehicules-2023.csv",
            "sep": ";",
        },
        "2022": {
            "id": "c9742921-4427-41e5-81bc-f13af8bc31a0",
            "filename": "vehicules-2022.csv",
            "sep": ";",
        },
    },
    "lieux": {
        "2023": {
            "id": "8bef19bf-a5e4-46b3-b5f9-a145da4686bc",
            "filename": "lieux-2023.csv",
            "sep": ";",
            "decimal": ",",
        },
        "2022": {
            "id": "a6ef711a-1f03-44cb-921a-0ce8ec975995",
            "filename": "lieux-2022.csv",
            "sep": ";",
            "decimal": ",",
        },
    },
}


# ---------------------------------------------------------------------
# 1) DOWNLOAD : utilisé par scripts/download_data.py / make data
# ---------------------------------------------------------------------

def get_local_path(name: str, year: str) -> Path:
    """Chemin complet vers le CSV local pour une ressource donnée."""
    meta = RESOURCES[name][year]
    return DATA_DIR / meta["filename"]


def download_resource(name: str, year: str, overwrite: bool = False) -> Path:
    """
    Télécharge UN fichier (ex: usagers 2023) et le stocke dans data/.

    - Si le fichier existe et overwrite=False, on ne retélécharge pas.
    - Renvoie le chemin local du fichier.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    meta = RESOURCES[name][year]
    local_path = get_local_path(name, year)

    if local_path.exists() and not overwrite:
        return local_path

    url = BASE_URL_STABLE + meta["id"]
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    local_path.write_bytes(resp.content)
    return local_path


def download_all(overwrite: bool = False) -> None:
    """
    Télécharge toutes les ressources BAAC (usagers, caract, vehicules, lieux)
    pour toutes les années listées dans RESOURCES.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, years in RESOURCES.items():
        for year in years:
            path = download_resource(name, year, overwrite=overwrite)
            print(f"✔ Downloaded {name} {year} -> {path}")


# ---------------------------------------------------------------------
# 2) LOAD : utilisé par l'app Streamlit (aucun appel réseau ici)
# ---------------------------------------------------------------------

@st.cache_data(show_spinner=True)
def load_data() -> dict[str, pd.DataFrame]:
    """
    Charge les données BAAC depuis data/ et les renvoie sous la forme :

    {
        "usagers":   df_usagers_2022_2023,
        "caract":    df_caract_2022_2023,
        "vehicules": df_vehicules_2022_2023,
        "lieux":     df_lieux_2022_2023,
    }

    - Lit chaque année définie dans RESOURCES.
    - Appelle harmonize_chunk(...) (dans prep.py) pour normaliser :
        * noms de colonnes (ex: Accident_Id -> Num_Acc),
        * types (Num_Acc string),
        * ajout de 'year'.
    - Concatène toutes les années pour chaque rubrique.
    """
    tables: dict[str, pd.DataFrame] = {}

    for name, years in RESOURCES.items():
        frames: list[pd.DataFrame] = []

        for year, meta in years.items():
            local_path = get_local_path(name, year)

            if not local_path.exists():
                raise FileNotFoundError(
                    f"Fichier manquant : {local_path}. "
                    "Lance d'abord `make data` ou `python scripts/download_data.py`."
                )

            sep = meta.get("sep", ";")
            decimal = meta.get("decimal", None)

            if decimal:
                df = pd.read_csv(local_path, sep=sep, decimal=decimal)
            else:
                df = pd.read_csv(local_path, sep=sep)

            df = harmonize_chunk(name=name, year=year, df=df)

            frames.append(df)

        tables[name] = pd.concat(frames, ignore_index=True)

    return tables
