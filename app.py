"""
Application Streamlit du moteur de recherche intelligent.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import streamlit as st
import pandas as pd

from src.search.search_engine import SearchEngine
from pathlib import Path
from src.profiling.dataset_profiler import DatasetProfiler

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
dataset_profiler = DatasetProfiler()
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

theme = st.sidebar.selectbox(
    "Dataset Theme",
    [
        "All",
        "Weather",
        "Health",
        "Finance",
        "Education",
        "Environment",
        "Sports",
        "Technology",
        "Other"
    ]
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

            selected_theme = None if theme == "All" else theme

            st.session_state.results = search_engine.search(
                query=query,
                theme=selected_theme,
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

            # -------------------------------------------------------
            # Bouton View on Kaggle
            # -------------------------------------------------------

            with col_btn1:
                st.link_button(
                    "🌐 View on Kaggle",
                    row["url"],
                    use_container_width=True
                )

            # -------------------------------------------------------
            # Bouton Download Dataset
            # -------------------------------------------------------

            with col_btn2:
                if st.button(
                    "📥 Download Dataset",
                    key=f"download_{row['ref']}",
                    use_container_width=True
                ):
                    try:
                        dataset_path = search_engine.download_dataset(row["ref"])

                        st.success("✅ Dataset downloaded successfully.")
                        st.caption(f"Location: {dataset_path}")

                        # Sauvegarder le chemin
                        st.session_state[
                            f"downloaded_path_{row['ref']}"
                        ] = str(dataset_path)

                    except Exception as e:
                        st.error(f"❌ Download failed: {e}")

            # -------------------------------------------------------
            # Dataset Profiling - EN DEHORS DES COLONNES
            # -------------------------------------------------------

            downloaded_path = st.session_state.get(
                f"downloaded_path_{row['ref']}"
            )

            if downloaded_path:

                st.markdown("---")
                st.subheader("📊 Dataset Profiling")

                try:
                    dataset_path = Path(downloaded_path)

                    if dataset_path.is_dir():

                        files = dataset_profiler.list_dataset_files(dataset_path)

                        supported_extensions = {
                            ".csv",
                            ".xlsx",
                            ".xls",
                            ".json",
                            ".parquet",
                            ".tsv"
                        }

                        supported_files = [
                            file
                            for file in files
                            if file.suffix.lower() in supported_extensions
                        ]

                        if not supported_files:

                            st.warning(
                                "⚠️ No supported data file found in the downloaded dataset."
                            )

                            # Important : ne pas continuer si aucun fichier
                            continue

                        selected_file = st.selectbox(
                            "📄 Select a file to profile",
                            supported_files,
                            format_func=lambda file: file.name,
                            key=f"file_select_{row['ref']}"
                        )

                        dataframe = dataset_profiler.load_dataset(selected_file)

                    else:

                        dataframe = dataset_profiler.load_dataset(dataset_path)

                    # Exécuter le profiling
                    profiling_report = dataset_profiler.profile_dataset(dataframe)

                    # -------------------------------------------------------
                    # Résumé du profiling
                    # -------------------------------------------------------

                    st.markdown("### 📈 Dataset Summary")

                    profile_col1, profile_col2, profile_col3, profile_col4 = st.columns(4)

                    with profile_col1:
                        st.metric(
                            "Rows",
                            profiling_report["rows"]
                        )

                    with profile_col2:
                        st.metric(
                            "Columns",
                            profiling_report["columns"]
                        )

                    with profile_col3:
                        st.metric(
                            "Duplicates",
                            profiling_report["duplicates"]
                        )

                    with profile_col4:
                        st.metric(
                            "Missing values",
                            profiling_report["missing_values"]["total_missing"]
                        )

                    st.metric(
                        "Memory usage",
                        f'{profiling_report["memory_mb"]} MB'
                    )

                    # -------------------------------------------------------
                    # Types des colonnes
                    # -------------------------------------------------------

                    st.markdown("### 🔠 Column Types")

                    column_types_df = pd.DataFrame(
                        list(
                            profiling_report["column_types"].items()
                        ),
                        columns=["Column", "Type"]
                    )

                    st.dataframe(
                        column_types_df,
                        use_container_width=True
                    )

                    # -------------------------------------------------------
                    # Valeurs manquantes
                    # -------------------------------------------------------

                    st.markdown("### 🧩 Missing Values")

                    missing_values = profiling_report["missing_values"]

                    missing_df = pd.DataFrame({
                        "Column": list(
                            missing_values["missing_values_per_column"].keys()
                        ),
                        "Missing values": list(
                            missing_values["missing_values_per_column"].values()
                        ),
                        "Percentage (%)": list(
                            missing_values["missing_percentage_per_column"].values()
                        )
                    })

                    st.dataframe(
                        missing_df,
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"❌ Profiling failed: {e}")