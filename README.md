# Data Storytelling – Accidents corporels BAAC 2022-2023

Tableau de bord Streamlit pour explorer les accidents corporels de la circulation en France (BAAC 2022-2023). Navigation par onglets (Introduction, Vue d’ensemble, Analyses détaillées, Conclusions) avec filtres année/département et cartes, séries temporelles et profils usagers.

## Structure du projet
- `app.py` : point d’entrée Streamlit (barre latérale, routage des sections).
- `sections/` : pages Streamlit (`intro.py`, `overview.py`, `deep_dives.py`, `conclusions.py`).
- `utils/` : chargement/dl des données (`io.py`), préparation (`prep.py`), constantes/viz (`constants.py`, `viz.py`).
- `scripts/download_data.py` : télécharge tous les fichiers BAAC 2022-2023 dans `data/`.
- `data/` : CSV sources téléchargés (non fournis dans le dépôt).
- `assets/` : visuels utilisés par l’interface (optionnels).

## Prérequis
- Python 3.10+ (recommandé : 3.11).
- `pip` et un accès réseau pour télécharger les données.
- (Optionnel) environnement virtuel.

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Récupération des données
1) Téléchargement automatique (nécessite Internet) :
```bash
python -m scripts.download_data
```
2) Ou dépôt manuel des CSV dans `data/` avec les noms attendus :
- `caract-2022.csv`, `caract-2023.csv`
- `usagers-2022.csv`, `usagers-2023.csv`
- `vehicules-2022.csv`, `vehicules-2023.csv`
- `lieux-2022.csv`, `lieux-2023.csv`

## Lancer le tableau de bord
```bash
streamlit run app.py
```
Ouvrir l’URL locale affichée (en général http://localhost:8501).

## Utilisation
- Barre latérale : navigation entre sections, présentation du projet.
- Vue d’ensemble : filtres année/département, KPI (accidents, tués, blessés), carte des accidents, séries temporelles.
- Analyses détaillées : répartitions par type de route, luminosité/météo, profils usagers (âge, gravité, type d’usager/véhicule), comparaisons par département.
- Conclusions : synthèse, limites des données, pistes d’interprétation.
