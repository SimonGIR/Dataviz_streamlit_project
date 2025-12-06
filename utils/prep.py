# utils/prep.py
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from utils.constants import CONSTANTS

np.random.seed(CONSTANTS.get("random_seed", 42))


# ---------------------------------------------------------------------
# Harmonisation bas niveau (appelée depuis utils.io)
# ---------------------------------------------------------------------

def harmonize_chunk(name: str, year: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise un morceau de table lu depuis CSV (une rubrique pour une année).

    - Renomme Accident_Id -> Num_Acc pour caract 2022
    - Force Num_Acc en string
    - Ajoute la colonne year
    """
    df = df.copy()

    if name == "caract" and year == "2022" and "Accident_Id" in df.columns:
        df = df.rename(columns={"Accident_Id": "Num_Acc"})

    if "Num_Acc" in df.columns:
        df["Num_Acc"] = df["Num_Acc"].astype("string")

    df["year"] = int(year)
    return df


# ---------------------------------------------------------------------
# Construction des tables analytiques
# ---------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def make_tables(raw_tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    À partir des tables brutes harmonisées (usagers, caract, vehicules, lieux),
    construit les tables analytiques utilisées par le dashboard.
    """

    caract = raw_tables.get("caract", pd.DataFrame()).copy()
    usagers = raw_tables.get("usagers", pd.DataFrame()).copy()
    lieux = raw_tables.get("lieux", pd.DataFrame()).copy()
    vehicules = raw_tables.get("vehicules", pd.DataFrame()).copy()  # pas encore exploité

    # --- Si pas de caract, on abandonne proprement ---
    if caract.empty:
        return {
            "accidents": caract,
            "timeseries": caract,
            "by_region": caract,
            "geo": caract,
        }

    # -----------------------------------------------------------------
    # 1) Nettoyage / enrichissement de CARACT : date, dep, lat/lon
    # -----------------------------------------------------------------
    for col in ["jour", "mois", "an"]:
        if col in caract.columns:
            caract[col] = caract[col].astype(str).str.zfill(2)

    if {"an", "mois", "jour"} <= set(caract.columns):
        caract["date"] = pd.to_datetime(
            caract["an"] + "-" + caract["mois"] + "-" + caract["jour"],
            errors="coerce",
            format="%Y-%m-%d",
        )

    if "dep" in caract.columns:
        caract["dep"] = caract["dep"].astype(str).str.zfill(2)

    if "long" in caract.columns and "lon" not in caract.columns:
        caract = caract.rename(columns={"long": "lon"})

    # -----------------------------------------------------------------
    # 2) Agrégats au niveau de l'usager (gravité, âge...)
    # -----------------------------------------------------------------
    if not usagers.empty:
        u = usagers.copy()

        if "grav" in u.columns:
            u["grav"] = pd.to_numeric(u["grav"], errors="coerce")

        if "an_nais" in u.columns:
            u["an_nais"] = pd.to_numeric(u["an_nais"], errors="coerce")
            if "year" in u.columns:
                u["age"] = u["year"] - u["an_nais"]
            else:
                u["age"] = np.nan
        else:
            u["age"] = np.nan

        u["is_tue"] = u["grav"] == 2
        u["is_bless_hosp"] = u["grav"] == 3
        u["is_bless_leg"] = u["grav"] == 4

        usagers_agg = (
            u.groupby(["Num_Acc", "year"], as_index=False)
            .agg(
                n_usagers=("id_usager", "count"),
                n_tues=("is_tue", "sum"),
                n_bless_hosp=("is_bless_hosp", "sum"),
                n_bless_leg=("is_bless_leg", "sum"),
                age_moyen=("age", "mean"),
            )
        )
    else:
        usagers_agg = pd.DataFrame(
            columns=[
                "Num_Acc",
                "year",
                "n_usagers",
                "n_tues",
                "n_bless_hosp",
                "n_bless_leg",
                "age_moyen",
            ]
        )

    # -----------------------------------------------------------------
    # 3) Table accidents = CARACT + agrégats USAGERS + infos LIEUX
    # -----------------------------------------------------------------
    accidents = caract.merge(
        usagers_agg,
        on=["Num_Acc", "year"],
        how="left",
        validate="1:m",
    )

    if not lieux.empty:
        cols_lieux = ["Num_Acc", "year", "catr", "surf", "circ", "nbv", "vma"]
        cols_lieux = [c for c in cols_lieux if c in lieux.columns]

        if {"Num_Acc", "year"} <= set(cols_lieux):
            lieux_sub = (
                lieux[cols_lieux]
                .drop_duplicates(subset=["Num_Acc", "year"])
            )

            accidents = accidents.merge(
                lieux_sub,
                on=["Num_Acc", "year"],
                how="left",
                validate="1:1",
            )

    for col in ["n_usagers", "n_tues", "n_bless_hosp", "n_bless_leg"]:
        if col in accidents.columns:
            accidents[col] = accidents[col].fillna(0).astype(int)

    # -----------------------------------------------------------------
    # 4) Table timeseries : n_accidents par date/dep/year
    # -----------------------------------------------------------------
    if "date" in accidents.columns:
        group_cols = ["date"]
        if "year" in accidents.columns:
            group_cols.append("year")
        if "dep" in accidents.columns:
            group_cols.append("dep")

        timeseries = (
            accidents.dropna(subset=["date"])
            .groupby(group_cols, as_index=False)
            .agg(
                n_accidents=("Num_Acc", "nunique"),
                n_tues=("n_tues", "sum"),
                n_blesses=("n_bless_hosp", "sum"),
            )
        )
    else:
        timeseries = pd.DataFrame()

    # -----------------------------------------------------------------
    # 5) Table by_region : n_accidents par dep/year
    # -----------------------------------------------------------------
    if "dep" in accidents.columns:
        by_region = (
            accidents.groupby(["dep", "year"], as_index=False)
            .agg(
                n_accidents=("Num_Acc", "nunique"),
                n_tues=("n_tues", "sum"),
                n_blesses=("n_bless_hosp", "sum"),
            )
        )
        by_region["pct_mortels"] = np.where(
            by_region["n_accidents"] > 0,
            by_region["n_tues"] / by_region["n_accidents"] * 100,
            np.nan,
        )
    else:
        by_region = pd.DataFrame()

    # -----------------------------------------------------------------
    # 6) Table geo : pour la carte
    # -----------------------------------------------------------------
    geo_cols = ["Num_Acc", "dep", "date", "lat", "lon", "year", "n_tues", "n_bless_hosp"]
    geo = accidents[[c for c in geo_cols if c in accidents.columns]].copy()

    if not geo.empty:
        geo = geo.dropna(subset=["lat", "lon"])

    return {
        "accidents": accidents,
        "timeseries": timeseries,
        "by_region": by_region,
        "geo": geo,
    }


# ---------------------------------------------------------------------
# Filtrage des tables (utilisé éventuellement par les pages)
# ---------------------------------------------------------------------

def filter_tables(
    tables: dict[str, pd.DataFrame],
    regions,
    date_range,
    metric,  # conservé pour compatibilité
) -> dict[str, pd.DataFrame]:
    """
    Applique les filtres (départements + plage de dates) aux tables analytiques.
    """
    filtered: dict[str, pd.DataFrame] = {}

    for name, df in tables.items():
        df_f = df.copy()

        # Filtre par département
        if regions and "dep" in df_f.columns:
            df_f = df_f[df_f["dep"].isin(regions)]

        # Filtre par date
        if date_range and len(date_range) == 2 and "date" in df_f.columns:
            start, end = date_range
            df_f["date"] = pd.to_datetime(df_f["date"])
            df_f = df_f[
                (df_f["date"] >= pd.to_datetime(start))
                & (df_f["date"] <= pd.to_datetime(end))
            ]

        filtered[name] = df_f

    return filtered
