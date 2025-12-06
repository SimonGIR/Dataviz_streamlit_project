# sections/intro.py
from pathlib import Path
import base64

import streamlit as st


def _render_hero():
    """
    Affiche le bloc d'en-tête (Introduction + titre + source)
    avec une image de fond si assets/road_safety_banner.jpg existe.
    """
    img_path = Path("assets/road_safety_banner.jpg")

    if not img_path.exists():
        
        st.title("Accidents corporels de la route")
        st.caption("Source : BAAC 2022–2023 — data.gouv.fr — licence ouverte")
        return

    # Encode l'image en base64 pour l'injecter en CSS
    with img_path.open("rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .hero-intro {{
            position: relative;
            padding: 2.5rem 2rem 2rem 2rem;
            border-radius: 1rem;
            background-image: url("data:image/jpeg;base64,{img_b64}");
            background-size: cover;
            background-position: center;
            margin-bottom: 1.8rem;
            color: white;
        }}

        .hero-intro::before {{
            content: "";
            position: absolute;
            inset: 0;
            border-radius: 1rem;
            background: linear-gradient(90deg, rgba(0,0,0,0.7), rgba(0,0,0,0.25));
        }}

        .hero-intro-content {{
            position: relative;
            z-index: 1;
        }}

        .hero-intro h1,
        .hero-intro h2,
        .hero-intro p {{
            color: #ffffff;
            margin: 0;
        }}

        .hero-intro h1 {{
            font-size: 2.4rem;
            margin-bottom: 0.4rem;
        }}

        .hero-intro h2 {{
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }}

        .hero-source {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-intro">
          <div class="hero-intro-content">
            <h1>Accidents corporels de la route</h1>
            <p class="hero-source">
              Source : BAAC 2022–2023 — data.gouv.fr — licence ouverte
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render(raw_tables, tables):
    # --- Bloc hero avec image de fond ---
    _render_hero()

    st.header("Introduction")

    # --- Contexte ---
    st.markdown(
        """
        ### Contexte et enjeux

        Ce tableau de bord s’intéresse aux accidents corporels de la circulation routière en France
        à partir des fichiers BAAC pour les années 2022 et 2023. Il s’agit exclusivement d’accidents
        ayant entraîné au moins un blessé ou un décès, déclarés par les forces de l’ordre.

        Chaque point affiché représente donc une situation où des personnes ont été touchées
        physiquement. L’objectif n’est pas seulement de compter ces événements, mais de mieux
        comprendre les situations dans lesquelles ils se produisent : où les accidents surviennent, à
        quels moments de l’année ou de la journée ils sont les plus fréquents, quels types
        d’usagers sont les plus exposés, et dans quelles conditions (type de route, luminosité,
        météo, contexte de circulation, etc.).
        """
    )

    # --- Objectifs ---
    st.markdown(
        """
        ### Objectifs du tableau de bord

        Ce tableau de bord a plusieurs finalités :

        - Donner une **vue d’ensemble** des accidents corporels récents en France (2022–2023).
        - Mettre en évidence des **tendances générales** : évolution temporelle, saisonnalité, zones les plus touchées.
        - Identifier certains **facteurs de risque** : type de voie, contexte de circulation, gravité.
        - Mettre en lumière des **profils d’usagers vulnérables** (piétons, deux-roues, tranches d’âge, etc.).
        - Permettre une **exploration interactive** via des filtres (département, période, etc.) pour adapter la lecture
          au contexte de l’utilisateur.
        """
    )

    # --- Comment lire ce dashboard ---
    st.markdown(
        """
        ### Comment lire ce tableau de bord

        La navigation est organisée en plusieurs sections qui suivent un fil narratif :

        - Une vue globale qui présente les indicateurs clés et les grandes tendances.
        - Une vue avec des analyses plus détaillées par territoire, type de voie et profils d’usagers,
          pour comprendre plus finement les situations à risque.
        - Une synthèse des principaux enseignements, des limites de l’analyse et des pistes de réflexion ou d’action.
        """
    )

    # --- Limites des données (Data caveats) ---
    st.info(
        """
        ### Qualité des données & précautions d’interprétation
        **Points importants à garder en tête :**

        Les fichiers BAAC décrivent uniquement les accidents corporels signalés aux forces de l’ordre.
        Certains accidents peuvent donc ne pas apparaître dans les données, ce qui signifie que les chiffres
        présentés doivent être interprétés comme un minimum observé, et non comme une mesure exhaustive de la réalité.

        Par ailleurs, un certain nombre de variables peuvent être manquantes ou non pertinentes selon les cas.
        Cela se traduit dans la base par des cellules vides, des valeurs à 0, des points ou des codes spécifiques
        (par exemple -1). La géolocalisation n’est pas toujours précise : pour certains enregistrements, seule la
        commune est connue, et l’adresse ou les coordonnées peuvent être partielles.

        Tous les véhicules impliqués n’ont pas nécessairement un usager renseigné (par exemple en cas de conducteur
        en fuite), ce qui limite certaines analyses fines sur l’âge ou le sexe des conducteurs. Enfin, les résultats
        portent uniquement sur les années 2022 et 2023 : ils offrent un état récent de la situation, mais ne constituent
        pas une étude de long terme sur plusieurs décennies.

        Ces limites ne remettent pas en cause l’intérêt des tendances observées, mais elles doivent être gardées à l’esprit
        pour éviter de surinterpréter les chiffres et pour replacer chaque insight dans son contexte de production des données.
        """
    )

    # --- Petit aperçu des données sources ---
    st.markdown("### Aperçu des données utilisées")

    st.caption(
        "Les tableaux ci-dessous donnent un aperçu des différentes rubriques BAAC "
        "(caractéristiques, lieux, véhicules, usagers)."
    )

    for name, df in raw_tables.items():
        with st.expander(
            f"Table : {name} — {len(df)} lignes, {len(df.columns)} colonnes"
        ):
            st.dataframe(df.head())
