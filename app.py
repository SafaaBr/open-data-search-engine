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
# Session State
# -------------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = None

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

# Lancer une nouvelle recherche
if search_button:

    if not query.strip():

        st.warning("Please enter a search query.")

    else:

        with st.spinner("Searching datasets..."):

            st.session_state.results = search_engine.search(
                query=query,
                top_k=top_k
            )
        
        print(st.session_state.results.columns)

# Afficher les derniers résultats
if st.session_state.results is not None:

    results = st.session_state.results

    if results.empty:

        st.warning("No dataset found.")

    else:

        st.success(f"{len(results)} dataset(s) found.")

        for rank, (_, row) in enumerate(results.iterrows(), start=1):
        

            st.markdown("---")

            st.subheader(f"#{rank} {row['title']}")

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

            size_mb = row["size_mb"]

            if size_mb >= 1024:
                size_text = f"{size_mb / 1024:.2f} GB"
            else:
                size_text = f"{size_mb:.2f} MB"

            st.write(f"📦 **Dataset size:** {size_text}")

            if size_mb >= 1000:
                st.warning(
                    "⚠️ Large dataset. Downloading and extracting may take several minutes."
                )

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                st.link_button(
                    "🌐 View on Kaggle",
                    row["url"],
                    use_container_width=True
                )

            with col_btn2:
                if st.button(
                    "📥 Download Dataset",
                    key=f"download_{rank}",
                    use_container_width=True
                ):

                    with st.spinner("Downloading dataset..."):

                        dataset_path = search_engine.download_dataset(
                            row["ref"]
                        )

                    st.success("✅ Dataset downloaded successfully.")
                    st.caption(f"Location: {dataset_path}") 

                    

      