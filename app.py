import streamlit as st

from utils.io import load_data
from utils.prep import make_tables, filter_tables
from sections import intro, overview, deep_dives, conclusions


st.set_page_config(
    page_title="Data Storytelling Dashboard",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def get_data():
    raw_tables = load_data()
    tables = make_tables(raw_tables)
    return raw_tables, tables


def main():

    raw_tables, tables = get_data()


    with st.sidebar:
        st.header("À propos")

        st.markdown("**Projet :** Data Visualization – EFREI 2025")
        st.markdown(
            "**Thème :** Accidents corporels de la circulation en France "
            "(BAAC 2022–2023)"
        )
        st.markdown("**Auteur :** Simon GIRARD ([LinkedIn](https://www.linkedin.com/in/girard-simon/))", unsafe_allow_html=True,)

        st.markdown("---")
        st.header("Navigation")
        section = st.radio(
            "Sections",
            ["Introduction", "Vue d'ensemble", "Analyses détaillées", "Conclusions"],
        )
        

        
    if section == "Introduction":
        intro.render(raw_tables, tables)
    elif section == "Vue d'ensemble":
        overview.render(tables, metric=None)
    elif section == "Analyses détaillées":
        deep_dives.render(tables, metric=None)
    else:
        conclusions.render(raw_tables, tables)


if __name__ == "__main__":
    main()
