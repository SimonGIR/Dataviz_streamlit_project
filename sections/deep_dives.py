# sections/deep_dives.py
import json
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt

from utils.viz import bar_chart, line_chart, fmt_int_fr, fmt_pct_fr  # line_chart pas forcément utilisé mais gardé


# ---------- Dictionnaires code -> libellé (BAAC) ---------- #

CODE_LABELS = {
    "lum": {
        "-1": "Non renseigné",
        "1": "Plein jour",
        "2": "Crépuscule ou aube",
        "3": "Nuit sans éclairage public",
        "4": "Nuit, éclairage non allumé",
        "5": "Nuit, éclairage allumé",
    },
    "agg": {
        "-1": "Non renseigné",
        "1": "Hors agglomération",
        "2": "En agglomération",
    },
    "atm": {
        "-1": "Non renseigné",
        "1": "Normale",
        "2": "Pluie légère",
        "3": "Pluie forte",
        "4": "Neige / grêle",
        "5": "Brouillard / fumée",
        "6": "Vent fort / tempête",
        "7": "Temps éblouissant",
        "8": "Temps couvert",
        "9": "Autre",
    },
    "col": {
        "-1": "Non renseigné",
        "1": "Deux véhicules - frontale",
        "2": "Deux véhicules - par l’arrière",
        "3": "Deux véhicules - par le côté",
        "4": "≥3 véhicules - en chaîne",
        "5": "≥3 véhicules - collisions multiples",
        "6": "Autre collision",
        "7": "Sans collision",
    },
    "surf": {
        "-1": "Non renseigné",
        "1": "Normale",
        "2": "Mouillée",
        "3": "Flaques",
        "4": "Inondée",
        "5": "Enneigée",
        "6": "Boue",
        "7": "Verglacée",
        "8": "Corps gras / huile",
        "9": "Autre",
    },
    "catr": {
        "-1": "Non renseigné",
        "1": "Autoroute",
        "2": "Route nationale",
        "3": "Route départementale",
        "4": "Voie communale",
        "5": "Hors réseau public",
        "6": "Parking ouvert à la circulation",
        "7": "Route de métropole urbaine",
        "9": "Autre",
    },
}

VARIABLES_DISPO = {
    "Type de collision": "col",
    "Type de lumière": "lum",
    "Conditions atmosphériques": "atm",
    "État de la surface": "surf",
    "Agglomération / hors agglo": "agg",
}

# Emplacement éventuel du GeoJSON des départements
DEPT_GEOJSON_PATH = Path("data/departements.geojson")
DEPT_GEOJSON_CODE_PROP = "code"  # à adapter selon ton fichier (properties.code / properties.code_insee, etc.)


def apply_code_labels(df: pd.DataFrame, col: str) -> tuple[pd.DataFrame, str]:
    """Mappe les codes BAAC vers des libellés lisibles si possible."""
    if col not in df.columns:
        return df, col

    mapping = CODE_LABELS.get(col)
    if not mapping:
        return df, col

    df = df.copy()
    df[col] = df[col].astype(str)
    label_col = f"{col}_label"
    df[label_col] = df[col].map(mapping).fillna(df[col])
    return df, label_col


def _add_gravity_category(accidents: pd.DataFrame) -> pd.DataFrame:
    df = accidents.copy()
    for c in ["n_tues", "n_bless_hosp", "n_bless_leg"]:
        if c not in df.columns:
            df[c] = 0

    df["gravite_accident"] = "Indemne / non renseigné"
    df.loc[df["n_bless_leg"] > 0, "gravite_accident"] = "Blessé léger"
    df.loc[df["n_bless_hosp"] > 0, "gravite_accident"] = "Blessé hospitalisé"
    df.loc[df["n_tues"] > 0, "gravite_accident"] = "Tué"
    return df


def _add_season(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "date" not in df.columns:
        df["saison"] = "Inconnue"
        return df

    mois = df["date"].dt.month
    conditions = [
        mois.isin([12, 1, 2]),
        mois.isin([3, 4, 5]),
        mois.isin([6, 7, 8]),
        mois.isin([9, 10, 11]),
    ]
    choix = ["Hiver", "Printemps", "Été", "Automne"]

    df["saison"] = "Inconnue"
    for cond, label in zip(conditions, choix):
        df.loc[cond, "saison"] = label
    return df


# ------------------------- Page principale ------------------------- #

def render(tables, metric):
    st.title("Analyses détaillées")

    accidents = tables.get("accidents")
    geo = tables.get("geo")

    if accidents is None or accidents.empty:
        st.info("Pas de données d'accidents disponibles pour les analyses détaillées.")
        return

    accidents = _add_gravity_category(accidents)

    # On prépare juste les listes globales, mais les filtres seront dans chaque onglet
    years = sorted(accidents["year"].dropna().unique().tolist())
    year_options = ["Toutes"] + [str(y) for y in years]

    deps = (
        sorted(accidents["dep"].dropna().unique().tolist())
        if "dep" in accidents.columns
        else []
    )
    dep_options = ["France entière"] + deps

    tab_contextes, tab_saison, tab_voie, tab_territoire = st.tabs(
        [
            "Contextes & facteurs de gravité",
            "Saisonnalité & temporalité",
            "Infrastructure & type de voie",
            "Disparités territoriales",
        ]
    )

    # ------------------------------------------------------------------
    # 1) Contextes & facteurs de gravité
    # ------------------------------------------------------------------
    with tab_contextes:
        

        # Filtres locaux à l'onglet
        st.markdown("#### Filtres")
        c1, c2, c3 = st.columns(3)
        with c1:
            year_label_ctx = st.selectbox(
                "Année",
                options=year_options,
                index=0,
                key="ctx_year",
            )
        with c2:
            dep_ctx = st.selectbox(
                "Département",
                options=dep_options,
                index=0,
                key="ctx_dep",
            )
        with c3:
            var_label = st.selectbox(
                "Contexte analysé",
                options=list(VARIABLES_DISPO.keys()),
                index=0,
                key="ctx_var",
            )


        var_col = VARIABLES_DISPO[var_label]
        year_value_ctx = None if year_label_ctx == "Toutes" else int(year_label_ctx)

        df_ctx = accidents.copy()
        if year_value_ctx is not None:
            df_ctx = df_ctx[df_ctx["year"] == year_value_ctx]
        if dep_ctx != "France entière" and "dep" in df_ctx.columns:
            df_ctx = df_ctx[df_ctx["dep"] == dep_ctx]

        st.markdown("---")

        if var_col not in df_ctx.columns:
            st.warning(
                f"La colonne associée au contexte '{var_label}' ({var_col}) "
                "n'est pas disponible dans la table des accidents."
            )
        else:
            df_ctx = df_ctx.dropna(subset=[var_col])
            if df_ctx.empty:
                st.info("Aucune donnée disponible pour ce contexte avec les filtres actuels.")
            else:
                df_ctx, label_col = apply_code_labels(df_ctx, var_col)

                # agrégat pour le camembert
                agg_factor = (
                    df_ctx.groupby(label_col, as_index=False)
                    .agg(n_accidents=("Num_Acc", "nunique"))
                )
                total = agg_factor["n_accidents"].sum()
                agg_factor["pourcentage"] = (
                    agg_factor["n_accidents"] / total * 100 if total > 0 else 0
                )

                # gravité x modalité
                grav = (
                    df_ctx.groupby([label_col, "gravite_accident"], as_index=False)
                    .agg(n_accidents=("Num_Acc", "nunique"))
                )
                grav["total_cat"] = grav.groupby(label_col)["n_accidents"].transform("sum")
                grav["pourcentage"] = grav["n_accidents"] / grav["total_cat"] * 100

                col_left, col_right = st.columns(2)

                with col_left:
                    sous_titre = f"#### Répartition de **{var_label.lower()}**"
                    contexte_txt = []

                    if dep_ctx != "France entière":
                        contexte_txt.append(f"dép. {dep_ctx}")
                    if year_value_ctx is not None:
                        contexte_txt.append(f"année {year_value_ctx}")

                    if contexte_txt:
                        sous_titre += " – " + " / ".join(contexte_txt)

                    st.markdown(sous_titre)

                    fig_pie = px.pie(
                        agg_factor,
                        names=label_col,
                        values="n_accidents",
                        title="Part des accidents par modalité",
                        hole=0.0,
                    )
                    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                    fig_pie.update_layout(
                        height=400,
                        margin=dict(l=40, r=40, t=60, b=40),
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col_right:
                    st.markdown("#### Gravité des accidents selon le contexte")
                    fig_bar = px.bar(
                        grav,
                        x=label_col,
                        y="pourcentage",
                        color="gravite_accident",
                        labels={
                            label_col: "Catégorie",
                            "pourcentage": "Pourcentage d'accidents (%)",
                            "gravite_accident": "Gravité",
                        },
                        title="Répartition de la gravité par modalité",
                    )
                    fig_bar.update_layout(
                        barmode="stack",
                        yaxis=dict(range=[0, 100]),
                        height=400,
                        margin=dict(l=40, r=40, t=60, b=40),
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                st.markdown("#### Détail numérique")
                table = agg_factor[[label_col, "n_accidents", "pourcentage"]].rename(
                    columns={
                        label_col: "Catégorie",
                        "n_accidents": "Accidents",
                        "pourcentage": "Pourcentage (%)",
                    }
                )
                st.dataframe(
                    table.sort_values("Accidents", ascending=False)
                    .style.format({"Accidents": fmt_int_fr, "Pourcentage (%)": fmt_pct_fr}),
                    use_container_width=True,
                )

    # ------------------------------------------------------------------
    # 2) Saisonnalité & temporalité
    # ------------------------------------------------------------------
    with tab_saison:

        if "date" not in accidents.columns:
            st.info("Les dates d'accident ne sont pas disponibles.")
        else:
            # Filtres locaux à l'onglet
            st.markdown("#### Filtres")
            c1, c2 = st.columns(2)
            with c1:
                year_label_sais = st.selectbox(
                    "Année",
                    options=year_options,
                    index=0,
                    key="sais_year",
                )
            with c2:
                dep_sais = st.selectbox(
                    "Département",
                    options=dep_options,
                    index=0,
                    key="sais_dep",
                )

            year_value_sais = None if year_label_sais == "Toutes" else int(year_label_sais)

            # Base filtrée pour les calculs saisonniers
            df_base_sais = accidents.copy()
            if year_value_sais is not None:
                df_base_sais = df_base_sais[df_base_sais["year"] == year_value_sais]
            if dep_sais != "France entière" and "dep" in df_base_sais.columns:
                df_base_sais = df_base_sais[df_base_sais["dep"] == dep_sais]

            st.markdown("---")

            # Tableau saison x gravité (filtré sur année + dep)
            df_season = _add_season(df_base_sais)

            saison_agg = (
                df_season.groupby(["saison", "gravite_accident"], as_index=False)
                .agg(n_accidents=("Num_Acc", "nunique"))
            )
            pivot = saison_agg.pivot(
                index="saison",
                columns="gravite_accident",
                values="n_accidents",
            ).fillna(0)

            ordre_saisons = ["Hiver", "Printemps", "Été", "Automne"]
            pivot = pivot.reindex(ordre_saisons)
            pivot["Total"] = pivot.sum(axis=1)

            # Courbe mensuelle par année (on laisse le choix de garder "Toutes" pour comparer les années)
            df_month = accidents.copy()
            if dep_sais != "France entière" and "dep" in df_month.columns:
                df_month = df_month[df_month["dep"] == dep_sais]
            if year_value_sais is not None:
                df_month = df_month[df_month["year"] == year_value_sais]

            df_month = df_month.dropna(subset=["date"])
            df_month["mois"] = df_month["date"].dt.month

            mois_noms = {
                1: "Janvier",
                2: "Février",
                3: "Mars",
                4: "Avril",
                5: "Mai",
                6: "Juin",
                7: "Juillet",
                8: "Août",
                9: "Septembre",
                10: "Octobre",
                11: "Novembre",
                12: "Décembre",
            }
            df_month["mois_label"] = df_month["mois"].map(mois_noms)

            mois_agg = (
                df_month.groupby(["year", "mois", "mois_label"], as_index=False)
                .agg(n_accidents=("Num_Acc", "nunique"))
            )

            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("#### Répartition saisonnière par gravité")
                st.dataframe(pivot.astype(int), use_container_width=True)
                st.caption(
                    "Nombre d'accidents par saison, décomposé selon la gravité "
                    f"{'' if dep_sais == 'France entière' else f'(dép. {dep_sais})'} "
                    f"{'' if year_value_sais is None else f'– année {year_value_sais}'}."
                )

            with col_right:
                st.markdown("#### Évolution mensuelle des accidents (par année)")

                if mois_agg.empty:
                    st.info("Pas de données suffisantes pour tracer la courbe mensuelle.")
                else:
                    chart = (
                        alt.Chart(mois_agg)
                        .mark_line(point=True)
                        .encode(
                            x=alt.X(
                                "mois_label",
                                sort=list(mois_noms.values()),
                                title="Mois",
                            ),
                            y=alt.Y("n_accidents", title="Nombre d'accidents"),
                            color=alt.Color("year:N", title="Année"),
                            tooltip=list(mois_agg.columns),
                        )
                        .interactive()
                        .properties(
                            title="Nombre d'accidents par mois et par année",
                        )
                    )
                    st.altair_chart(chart, use_container_width=True)

                st.caption(
                    "Le graphique compare l'évolution mensuelle pour chaque année "
                    f"({ 'toutes années' if year_value_sais is None else 'année filtrée uniquement' }). "
                    f"Filtre département : {dep_sais}."
                )

    # ------------------------------------------------------------------
    # 3) Infrastructure & type de voie
    # ------------------------------------------------------------------
    with tab_voie:
        st.subheader("Infrastructure & type de voie")

        # Pas de filtres pour cet onglet : on travaille sur l'ensemble du jeu
        df_voie = accidents.copy()

        if "catr" not in df_voie.columns:
            st.info(
                "La variable de type de voie (catr) n'est pas disponible. "
                "Vérifie que la table LIEUX est bien jointe dans make_tables()."
            )
        else:
            voie_agg = (
                df_voie.groupby("catr", as_index=False)
                .agg(
                    n_accidents=("Num_Acc", "nunique"),
                    n_tues=("n_tues", "sum"),
                )
            )
            voie_agg["pct_mortels"] = (
                voie_agg["n_tues"] / voie_agg["n_accidents"] * 100
            )

            voie_agg, label_col = apply_code_labels(voie_agg, "catr")

            st.markdown("#### Accidents selon le type de voie")
            bar_chart(
                voie_agg,
                x=label_col,
                y="n_accidents",
                title="Nombre d'accidents par catégorie de route",
            )

            st.markdown("#### Détail par type de voie")
            table = voie_agg[[label_col, "n_accidents", "n_tues", "pct_mortels"]].rename(
                columns={
                    label_col: "Type de voie",
                    "n_accidents": "Accidents",
                    "n_tues": "Décès",
                    "pct_mortels": "% mortels",
                }
            )
            st.dataframe(
                table.sort_values("Accidents", ascending=False)
                .style.format(
                    {"Accidents": fmt_int_fr, "Décès": fmt_int_fr, "% mortels": fmt_pct_fr}
                ),
                use_container_width=True,
            )

    # ------------------------------------------------------------------
    # 4) Disparités territoriales
    # ------------------------------------------------------------------
    with tab_territoire:

        if "dep" not in accidents.columns:
            st.info("La colonne 'dep' n'est pas disponible.")
            return

        # Filtre local : uniquement l'année
        st.markdown("#### Filtre")
        year_label_dep = st.selectbox(
            "Année",
            options=year_options,
            index=0,
            key="dep_year",
        )
        year_value_dep = None if year_label_dep == "Toutes" else int(year_label_dep)

        st.markdown("---")

        dep_agg_src = accidents if year_value_dep is None else accidents[accidents["year"] == year_value_dep]
        dep_agg = (
            dep_agg_src.groupby("dep", as_index=False)
            .agg(
                n_accidents=("Num_Acc", "nunique"),
                n_tues=("n_tues", "sum"),
            )
        )
        dep_agg["% mortels"] = dep_agg["n_tues"] / dep_agg["n_accidents"] * 100

        # ----- Carte choroplèthe par département si GeoJSON dispo -----
        if DEPT_GEOJSON_PATH.exists():
            try:
                with DEPT_GEOJSON_PATH.open("r", encoding="utf-8") as f:
                    dept_geojson = json.load(f)

                fig = px.choropleth_mapbox(
                    dep_agg,
                    geojson=dept_geojson,
                    locations="dep",
                    featureidkey=f"properties.{DEPT_GEOJSON_CODE_PROP}",
                    color="n_tues",
                    color_continuous_scale="Reds",
                    mapbox_style="carto-positron",
                    zoom=4.7,
                    center={"lat": 46.5, "lon": 2.5},
                    opacity=0.7,
                    hover_name="dep",
                    hover_data={"n_tues": True, "n_accidents": True, "% mortels": True},
                )
                fig.update_layout(
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=500,
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(
                    "Chaque département est coloré en fonction du nombre total de tués. "
                    "Plus la teinte est foncée, plus le nombre de décès est élevé."
                    + ("" if year_value_dep is None else f" (année {year_value_dep}).")
                )
            except Exception as e:
                st.warning(
                    f"Impossible de charger le GeoJSON des départements ({DEPT_GEOJSON_PATH}). "
                    "Fallback vers une carte de points.\n\n"
                    f"Détail technique : {e}"
                )
                _fallback_scatter_map(accidents, year_value_dep)
        else:
            st.info(
                "Pour afficher une carte découpée par départements, ajoute un fichier "
                f"`{DEPT_GEOJSON_PATH}` (GeoJSON des départements français) et adapte le "
                "champ `DEPT_GEOJSON_CODE_PROP` si nécessaire. "
                "Une carte de points est affichée en attendant."
            )
            _fallback_scatter_map(accidents, year_value_dep)

        st.markdown("#### Synthèse par département")
        st.dataframe(
            dep_agg.sort_values("n_tues", ascending=False)
            .rename(
                columns={
                    "n_accidents": "Accidents",
                    "n_tues": "Décès",
                }
            )
            .style.format(
                {"Accidents": fmt_int_fr, "Décès": fmt_int_fr, "% mortels": fmt_pct_fr}
            ),
            use_container_width=True,
        )


def _fallback_scatter_map(accidents: pd.DataFrame, year_value: int | None):
    """Fallback : carte de points (barycentre par département)."""
    if not {"lat", "lon", "dep"}.issubset(accidents.columns):
        st.info(
            "Colonnes 'lat', 'lon' ou 'dep' manquantes : impossible d'afficher la carte."
        )
        return

    df_geo = accidents.dropna(subset=["lat", "lon"]).copy()
    if year_value is not None:
        df_geo = df_geo[df_geo["year"] == year_value]

    dep_geo = (
        df_geo.groupby("dep", as_index=False)
        .agg(
            n_tues=("n_tues", "sum"),
            lat_mean=("lat", "mean"),
            lon_mean=("lon", "mean"),
        )
    )
    if dep_geo.empty:
        st.info("Pas de données géolocalisées pour construire la carte.")
        return

    fig = px.scatter_mapbox(
        dep_geo,
        lat="lat_mean",
        lon="lon_mean",
        size="n_tues",
        color="n_tues",
        color_continuous_scale="Reds",
        size_max=30,
        zoom=4.7,
        hover_name="dep",
        hover_data={"n_tues": True},
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=0, b=0),
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
