# sections/overview.py
import streamlit as st
import pandas as pd

from utils.viz import bar_chart, map_chart, gauge_kpi, fmt_int_fr, fmt_pct_fr



def render(tables, metric):
    st.title("Vue d'ensemble")

    accidents = tables.get("accidents")
    geo = tables.get("geo")

    if accidents is None or accidents.empty:
        st.info("Pas de données d'accidents disponibles.")
        return

    # ------------------------------------------------------------------
    # Totaux France entière (toutes années) = max pour les gauges
    # ------------------------------------------------------------------
    total_accidents_all = accidents["Num_Acc"].nunique()
    total_tues_all = accidents["n_tues"].sum() if "n_tues" in accidents.columns else 0
    total_blesses_all = (
        accidents["n_bless_hosp"].sum() + accidents["n_bless_leg"].sum()
        if {"n_bless_hosp", "n_bless_leg"} <= set(accidents.columns)
        else 0
    )

    # ------------------------------------------------------------------
    # 1) Filtres (en haut de page)
    # ------------------------------------------------------------------
    st.markdown("### Filtres")

    years = sorted(accidents["year"].dropna().unique().tolist())
    year_options = ["Toutes"] + [str(y) for y in years]

    deps = sorted(accidents["dep"].dropna().unique().tolist()) if "dep" in accidents.columns else []
    dep_options = ["France entière"] + deps

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_year_label = st.selectbox("Année", options=year_options, index=0)
    with col_f2:
        selected_dep_label = st.selectbox("Département", options=dep_options, index=0)

    # Sous-ensemble filtré
    df_filtered = accidents.copy()
    if selected_year_label != "Toutes":
        year_value = int(selected_year_label)
        df_filtered = df_filtered[df_filtered["year"] == year_value]
    else:
        year_value = None

    if selected_dep_label != "France entière" and "dep" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["dep"] == selected_dep_label]

    # Valeurs filtrées pour les KPIs
    total_accidents_f = df_filtered["Num_Acc"].nunique()
    total_tues_f = df_filtered["n_tues"].sum() if "n_tues" in df_filtered.columns else 0
    total_blesses_f = (
        df_filtered["n_bless_hosp"].sum() + df_filtered["n_bless_leg"].sum()
        if {"n_bless_hosp", "n_bless_leg"} <= set(df_filtered.columns)
        else 0
    )

    # ------------------------------------------------------------------
    # 2) Indicateurs clés (gauges)
    # ------------------------------------------------------------------
    st.markdown("### Indicateurs clés")

    subtitle = ""
    if year_value is not None and selected_dep_label != "France entière":
        subtitle = f"{year_value} – dép. {selected_dep_label}"
    elif year_value is not None:
        subtitle = f"{year_value}"
    elif selected_dep_label != "France entière":
        subtitle = f"Dép. {selected_dep_label}"

    if subtitle:
        st.caption(f"Filtres appliqués : {subtitle}")
    else:
        st.caption("Filtres appliqués : France entière, toutes années")

    col_k1, col_k2, col_k3 = st.columns(3)

    with col_k1:
        gauge_kpi(
            value=total_accidents_f,
            max_value=total_accidents_all,
            title="Total accidents",
        )
    with col_k2:
        gauge_kpi(
            value=total_tues_f,
            max_value=total_tues_all if total_tues_all > 0 else total_tues_f or 1,
            title="Total décès",
        )
    with col_k3:
        gauge_kpi(
            value=total_blesses_f,
            max_value=total_blesses_all if total_blesses_all > 0 else total_blesses_f or 1,
            title="Total blessés",
        )

    st.markdown("---")

    # ------------------------------------------------------------------
    # 3) Classement + carte
    # ------------------------------------------------------------------
    st.subheader("Classement des territoires et visualisation géographique")

    left_col, right_col = st.columns([3, 2])

    # --------------------- Colonne gauche : Top 10 ---------------------
    with left_col:
        mode = st.radio(
            "Type de classement",
            ["Départements", "Communes"],
            horizontal=True,
        )

        # Classement filtré sur l'année, mais pas sur le département
        rank_df = accidents.copy()
        if year_value is not None:
            rank_df = rank_df[rank_df["year"] == year_value]

        if mode == "Départements":
            if "dep" not in rank_df.columns:
                st.info("La colonne 'dep' n'est pas disponible.")
            else:
                agg_dep = (
                    rank_df.groupby("dep", as_index=False)
                    .agg(n_accidents=("Num_Acc", "nunique"))
                )
                total = agg_dep["n_accidents"].sum()
                agg_dep["pourcentage"] = (
                    agg_dep["n_accidents"] / total * 100 if total > 0 else 0
                )

                top10 = agg_dep.sort_values("n_accidents", ascending=False).head(10)
                top10 = top10.reset_index(drop=True)
                top10["Rang"] = top10.index + 1
                top10["Code"] = top10["dep"]
                top10["Territoire"] = "Département " + top10["dep"].astype(str)

                display_df = top10[["Rang", "Code", "Territoire", "n_accidents", "pourcentage"]]
                display_df = display_df.rename(
                    columns={
                        "n_accidents": "Accidents",
                        "pourcentage": "Pourcentage (%)",
                    }
                )

                st.markdown("### Top 10 des départements")
                st.dataframe(
                    display_df.style.format(
                        {"Accidents": fmt_int_fr, "Pourcentage (%)": fmt_pct_fr}
                    ),
                    use_container_width=True,
                )

        else:  # Communes
            if selected_dep_label == "France entière":
                st.info("Sélectionne un **département** dans les filtres pour voir le Top 10 des communes.")
            else:
                if "com" not in rank_df.columns:
                    st.info("La colonne 'com' (code commune) n'est pas disponible.")
                else:
                    df_dep = rank_df[rank_df["dep"] == selected_dep_label].copy()
                    if df_dep.empty:
                        st.info("Pas d'accidents pour ce département avec le filtre actuel.")
                    else:
                        agg_com = (
                            df_dep.groupby("com", as_index=False)
                            .agg(n_accidents=("Num_Acc", "nunique"))
                        )
                        total_dep = agg_com["n_accidents"].sum()
                        agg_com["pourcentage"] = (
                            agg_com["n_accidents"] / total_dep * 100 if total_dep > 0 else 0
                        )

                        top10 = agg_com.sort_values("n_accidents", ascending=False).head(10)
                        top10 = top10.reset_index(drop=True)
                        top10["Rang"] = top10.index + 1
                        top10["Code"] = top10["com"]
                        top10["Territoire"] = "Commune " + top10["com"].astype(str)

                        display_df = top10[["Rang", "Code", "Territoire", "n_accidents", "pourcentage"]]
                        display_df = display_df.rename(
                            columns={
                                "n_accidents": "Accidents",
                                "pourcentage": "Pourcentage (%)",
                            }
                        )

                        st.markdown(
                            f"### Top 10 des communes du département {selected_dep_label}"
                        )
                        st.dataframe(
                            display_df.style.format(
                                {"Accidents": fmt_int_fr, "Pourcentage (%)": fmt_pct_fr}
                            ),
                            use_container_width=True,
                        )

    # --------------------- Colonne droite : Carte ----------------------
    with right_col:
        if geo is None or geo.empty:
            st.info("Pas de données géolocalisées disponibles.")
        else:
            geo_f = geo.copy()
            if year_value is not None:
                geo_f = geo_f[geo_f["year"] == year_value]
            if selected_dep_label != "France entière":
                geo_f = geo_f[geo_f["dep"] == selected_dep_label]

            map_chart(
                geo_f,
                lat="lat",
                lon="lon",
            )

        st.caption(
            "La carte représente uniquement les accidents pour lesquels des coordonnées sont disponibles. "
            "Les filtres d'année et de département s'appliquent également à cette vue."
        )
