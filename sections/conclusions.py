# sections/conclusions.py
from pathlib import Path
import base64

import streamlit as st


def _render_hero():
    """
    Bandeau d'en-tête avec image de fond pour la page de conclusion.
    Même dimensions que l'introduction, mais sans texte par-dessus.
    """
    img_path = Path("assets/safety_banner.jpg")

    if not img_path.exists():
        # Fallback sans image, au cas où le fichier n'existe pas
        st.header("error download image banner")
        return

    # Encode l'image en base64 pour l'injecter dans du CSS
    with img_path.open("rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    st.markdown(
    f"""
    <style>
    .hero-conclu {{
        position: relative;
        min-height: 186.06px;   /* même hauteur que celle que tu as observée */
        padding: 3.5rem 2rem;
        border-radius: 1rem;
        background-image: url("data:image/jpeg;base64,{img_b64}");
        background-size: cover;
        background-position: center;
        margin-bottom: 1.8rem;
    }}

    .hero-conclu::before {{
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 1rem;
        background: linear-gradient(90deg, rgba(0,0,0,0.25), rgba(0,0,0,0.05));
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


    # Div vide : uniquement le bandeau visuel
    st.markdown(
        """
        <div class="hero-conclu"></div>
        """,
        unsafe_allow_html=True,
    )


def render(df_raw, tables):
    # --- Bandeau image plein width ---
    _render_hero()

    # --- Titre de la page sous l'image ---
    st.header("Conclusions, insights et perspectives")

    # --- Corps de la page ---
    st.markdown(
        """
        ### 1. Principaux enseignements tirés des données

        L’analyse des fichiers BAAC 2022–2023 met en évidence plusieurs tendances structurantes
        pour comprendre les accidents corporels de la route en France.  

        D’abord, les données confirment que les accidents corporels ne sont pas répartis de façon
        homogène dans le temps ni dans l’espace. Certaines périodes (saisons, jours de la semaine,
        tranches horaires) et certains territoires concentrent une part plus importante des
        événements.  

        Ensuite, les profils d’usagers ne sont pas exposés de la même manière. On observe des
        différences entre les conducteurs de véhicules légers, les usagers de deux-roues,
        les piétons ou encore certaines tranches d’âge. Ces écarts se traduisent à la fois
        en fréquence d’accidents et en gravité des conséquences.  

        Enfin, le contexte de survenue (type de voie, environnement urbain ou non, luminosité,
        conditions météorologiques, etc.) joue un rôle important : certains types de routes
        et de situations de circulation concentrent davantage d’accidents graves que d’autres.
        Le tableau de bord permet de visualiser ces combinaisons de facteurs et d’identifier
        des configurations à risque.

        ---

        ### 2. Implications et usages possibles

        Ces résultats ne constituent pas des recommandations opérationnelles directes,
        mais ils peuvent alimenter la réflexion de différents acteurs.  

        Pour les acteurs publics (collectivités, services de l’État), le tableau de bord
        peut servir de point de départ pour repérer des zones ou des contextes à surveiller
        plus particulièrement, par exemple dans une logique de diagnostic territorial ou de
        priorisation d’actions de sécurité routière.  

        Pour des analystes ou des chercheurs, l’outil offre un support d’exploration rapide
        des données BAAC récentes, en facilitant la mise en évidence de tendances ou de profils
        d’usagers vulnérables qui mériteraient des analyses complémentaires plus fines
        (modélisation statistique, analyses longitudinales, etc.).  

        Pour un public plus large, le tableau de bord contribue à rendre les données
        plus accessibles et plus lisibles, en dépassant le simple volume d’accidents pour
        mettre en lumière les contextes, les profils impliqués et les niveaux de gravité.

        ---

        ### 3. Limites de l’analyse et pistes d’amélioration

        Ce tableau de bord reste volontairement centré sur quelques axes d’analyse
        (accessibles via les filtres et les visualisations principales). Plusieurs limites
        et pistes d’enrichissement peuvent être mentionnées.

        #### 3.1. Limites actuelles

        Les résultats sont basés uniquement sur les années 2022–2023. Ils donnent une
        photographie récente de la situation, mais ne permettent pas de conclure sur des
        tendances de long terme.  

        Par ailleurs, certaines dimensions des données BAAC ne sont exploitées que partiellement.
        Certaines variables manquantes ou imprécises (géolocalisation, informations sur les
        usagers, etc.) limitent la possibilité de mener des analyses très détaillées
        sur tous les territoires ou sur tous les profils.  

        Enfin, le tableau de bord se concentre sur une logique descriptive et exploratoire :
        il ne cherche pas à établir de relation causale entre les facteurs observés et la
        survenue des accidents, ni à produire des modèles prédictifs.

        #### 3.2. Pistes de travaux futurs et fonctionnalités non implémentées

        Plusieurs prolongements seraient possibles pour aller plus loin que la version
        actuelle du site :

        - **Étendre l’historique** : intégrer des années supplémentaires pour analyser
          des tendances sur une période plus longue et mieux distinguer les effets
          conjoncturels des évolutions structurelles.

        - **Croiser avec d’autres sources** : par exemple, des données de trafic,
          de population ou d’infrastructures (densité de circulation, type
          d’aménagements, présence d’écoles, etc.) afin de mettre davantage en
          perspective les niveaux d’accidents.

        - **Analyses plus avancées** : mettre en place des modèles statistiques
          ou des méthodes de scoring du risque (par type de voie, par créneau
          horaire, par profil d’usager), au-delà des seules représentations
          descriptives proposées dans le tableau de bord.

        - **Améliorations de l’interface** : ajouter des fonctionnalités
          d’export (rapports PDF, fichiers de synthèse), des comparaisons entre
          territoires (par exemple comparer deux départements) ou encore des
          indicateurs personnalisables selon le profil de l’utilisateur.

        - **Focus thématiques** : créer des pages dédiées à certains profils
          d’usagers (piétons, deux-roues, jeunes conducteurs, etc.) avec des
          visualisations adaptées et des indicateurs spécifiques.

        Ces pistes n’ont pas été implémentées dans la version actuelle du
        tableau de bord, mais elles illustrent la manière dont ce travail
        pourrait être prolongé, soit dans une logique de projet pédagogique,
        soit dans une logique de produit analytique plus complet.

        ---

        ### 4. Conclusion générale

        En synthèse, ce tableau de bord a pour ambition de rendre plus lisibles
        les accidents corporels de la route en France sur la période 2022–2023,
        en proposant une exploration interactive des données BAAC.  

        Il met en évidence des configurations à risque, des profils d’usagers
        plus exposés et des différences importantes selon les contextes de
        circulation. Malgré les limites inhérentes aux données et au périmètre
        du projet, les tendances observées constituent un point de départ utile
        pour alimenter la réflexion sur la sécurité routière et envisager des
        analyses plus approfondies à l’avenir.
        """
    )
