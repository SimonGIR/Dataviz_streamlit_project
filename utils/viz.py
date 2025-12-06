# utils/viz.py
import pandas as pd
import streamlit as st
import altair as alt


# Helpers de formatage fr
def fmt_int_fr(x):
    try:
        return f"{x:,.0f}".replace(",", " ")
    except Exception:
        return x


def fmt_pct_fr(x, decimals: int = 1):
    try:
        return f"{x:,.{decimals}f}".replace(",", " ").replace(".", ",")
    except Exception:
        return x


# Thème Altair localisé fr
alt.themes.register(
    "fr",
    lambda: {
        "config": {
            "locale": {
                "number": {
                    "decimal": ",",
                    "thousands": " ",
                }
            }
        }
    },
)
alt.themes.enable("fr")


def line_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = ""):
    if df is None or df.empty:
        st.info("Aucune donnee a afficher pour ce graphique.")
        return

    encodings = {
        "x": alt.X(x, title=x),
        "y": alt.Y(y, title=y, axis=alt.Axis(format=",.0f")),
        "tooltip": list(df.columns),
    }
    if color is not None:
        # couleur toujours traitée comme catégorielle (ex : year)
        encodings["color"] = alt.Color(f"{color}:N", title=color)

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(**encodings)
        .interactive()
        .properties(title=title)
    )
    st.altair_chart(chart, use_container_width=True)


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str = ""):
    if df is None or df.empty:
        st.info("Aucune donnee a afficher pour ce graphique.")
        return

    encodings = {
        "x": alt.X(x, title=x),
        "y": alt.Y(y, title=y, axis=alt.Axis(format=",.0f")),
        "tooltip": list(df.columns),
    }
    if color is not None:
        encodings["color"] = alt.Color(f"{color}:N", title=color)

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(**encodings)
        .properties(title=title)
    )
    st.altair_chart(chart, use_container_width=True)


def map_chart(
    df: pd.DataFrame,
    lat: str = "lat",
    lon: str = "lon",
    title: str = "Carte des accidents",
):
    if df is None or df.empty or lat not in df.columns or lon not in df.columns:
        st.info("Aucune donnee geolocalisee disponible.")
        return

    st.subheader(title)
    st.map(df[[lat, lon]])


def gauge_kpi(value: float, max_value: float, title: str, suffix: str = ""):
    """
    Affiche un indicateur demi-cercle (gauge) avec Plotly.
    - value : valeur filtrée
    - max_value : valeur maximale (par ex. total France entière)
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        st.error("Plotly n'est pas installé. Lance `pip install plotly` puis réessaie.")
        # fallback simple en utilisant le format français texte
        try:
            label_val = fmt_int_fr(value)
        except Exception:
            label_val = f"{value:,.0f}".replace(",", " ")
        st.metric(title, f"{label_val}{suffix}")
        return

    # Sécurisation du max
    if max_value <= 0:
        max_value = max(value, 1)

    # Texte formaté à la française pour l'affichage du nombre
    # (utilise fmt_int_fr si tu l'as défini plus haut dans ce fichier)
    try:
        texte_fr = fmt_int_fr(value)
    except Exception:
        texte_fr = f"{value:,.0f}".replace(",", " ")
    if suffix:
        texte_fr = f"{texte_fr} {suffix}"

    # Gauge sans "number" (on gère le nombre nous-mêmes en annotation)
    fig = go.Figure(
        go.Indicator(
            mode="gauge",
            value=value,
            title={"text": title},
            gauge={
                "axis": {"range": [0, max_value]},
                "shape": "angular",
                "bar": {"thickness": 0.3},
                "bgcolor": "white",
            },
        )
    )

    # Annotation centrée avec le nombre formaté en FR
    fig.add_annotation(
        x=0.5,
        y=0.15,  # tu peux ajuster si tu veux le texte plus haut/bas
        showarrow=False,
        text=texte_fr,
        font=dict(size=20),
        xref="paper",
        yref="paper",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=10),  # marge haute + basse pour éviter que ça soit rogné
        height=260,
    )

    # On affiche directement comme avant
    st.plotly_chart(fig, use_container_width=True)

