"""
Point d'entrée principal du projet.
"""

from src.extraction.kaggle_extractor import KaggleExtractor
from src.database.database_manager import DatabaseManager
from src.profiling.profiler import MetadataProfiler


def main():

    # -----------------------------
    # 1. Extraction des métadonnées
    # -----------------------------

    extractor = KaggleExtractor()

    extractor.authenticate()

    df = extractor.search_to_dataframe(
        query="finance",
        limit=5
    )

    print("\nMétadonnées extraites :")
    print(df.head())

    # -----------------------------
    # 2. Stockage SQLite
    # -----------------------------

    db = DatabaseManager()

    db.connect()

    db.create_tables()

    db.save_dataframe(df)

    dataframe = db.load_dataframe()

    db.close()

    # -----------------------------
    # 3. Metadata Profiler
    # -----------------------------

    profiler = MetadataProfiler()

    print("\nLe DataFrame est prêt pour le Metadata Profiler.")

    print(dataframe.head())


if __name__ == "__main__":
    main()