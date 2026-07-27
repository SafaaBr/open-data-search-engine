"""
Application Streamlit du moteur de recherche intelligent.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import streamlit as st

from src.search.search_engine import SearchEngine

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="Intelligent Kaggle Dataset Search",
    page_icon="🔍",
    layout="wide"
)

# -------------------------------------------------------
# Initialisation
# -------------------------------------------------------

@st.cache_resource
def load_search_engine():
    return SearchEngine()


search_engine = load_search_engine()

# -------------------------------------------------------
# Header
# -------------------------------------------------------

st.title("🔍 Intelligent Kaggle Dataset Search")

st.markdown(
    """
Search Kaggle datasets using semantic search powered by
Sentence Transformers, metadata quality assessment and
dataset popularity.
"""
)

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.header("⚙ Search Options")


top_k = st.sidebar.slider(
    "Number of results",
    min_value=1,
    max_value=20,
    value=5
)

# -------------------------------------------------------
# Search
# -------------------------------------------------------

query = st.text_input(
    "Search query",
    placeholder="Example: heart disease dataset"
)

search_button = st.button(
    "🔍 Search",
    use_container_width=True
)

# -------------------------------------------------------
# Results
# -------------------------------------------------------

if search_button:

    if not query.strip():

        st.warning("Please enter a search query.")

    else:


        with st.spinner("Searching datasets..."):

            results = search_engine.search(
                query=query,
                top_k=top_k
            )

        if results.empty:

            st.warning("No dataset found.")

        else:

            st.success(f"{len(results)} dataset(s) found.")

            for rank, (_, row) in enumerate(results.iterrows(), start=1):

                st.markdown("---")

                st.subheader(f"#{rank}  {row['title']}")

                score = row["recommendation_score"]

                if score >= 0.80:
                    badge = "🟢 Excellent Match"
                elif score >= 0.60:
                    badge = "🟢 Highly Relevant"
                elif score >= 0.40:
                    badge = "🟡 Relevant"
                elif score >= 0.20:
                    badge = "🟠 Moderate Match"
                else:
                    badge = "🔴 Low Match"

                st.info(badge)


                if row["description"]:
                    st.write(row["description"])

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Downloads",
                        f"{int(row['downloads']):,}"
                    )

                with col2:
                    st.metric(
                        "Votes",
                        f"{int(row['votes']):,}"
                    )

                with col3:
                    st.metric(
                        "Views",
                        f"{int(row['views']):,}"
                    )

                    st.link_button(
                        "📥 Download Dataset",
                        row["url"],
                        use_container_width=False
                    )
