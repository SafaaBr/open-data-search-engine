"""
Programme principal de test.

Ce script permet de :

- construire l'index local des datasets ;
- vérifier le contenu de la base SQLite ;
- tester le moteur de recherche sémantique.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

from src.extraction.kaggle_extractor import KaggleExtractor
from src.extraction.dataset_indexer import DatasetIndexer

from src.profiling.metadata_profiler import MetadataProfiler
from src.profiling.theme_classifier import ThemeClassifier

from src.nlp.embedding_engine import EmbeddingEngine

from src.database.database_manager import DatabaseManager

from src.search.search_engine import SearchEngine


def main():
    """
    Point d'entrée du programme.
    """

    print("=" * 60)
    print("CONSTRUCTION DE L'INDEX")
    print("=" * 60)

    extractor = KaggleExtractor()

    embedding_engine = EmbeddingEngine()

    database_manager = DatabaseManager()

    theme_classifier = ThemeClassifier()

    metadata_profiler = MetadataProfiler()

    indexer = DatasetIndexer(
        extractor=extractor,
        embedding_engine=embedding_engine,
        database_manager=database_manager,
        theme_classifier=theme_classifier,
        metadata_profiler=metadata_profiler
    )

    indexer.build_index(
        query="classification",
        limit=20
    )

    print("\nIndex construit avec succès.\n")

    print("=" * 60)
    print("CONTENU DE LA BASE")
    print("=" * 60)

    database_manager.connect()

    try:

        datasets = database_manager.get_all_datasets()

        print(
            datasets[
                [
                    "title",
                    "theme",
                    "metadata_score"
                ]
            ].head(10)
        )

    finally:

        database_manager.close()

    print("\n")

    print("=" * 60)
    print("TEST DU MOTEUR DE RECHERCHE")
    print("=" * 60)

    search_engine = SearchEngine()

    results = search_engine.search(
        query="heart disease",
        theme="Santé",
        top_k=5
    )

    print(
        results[
            [
                "title",
                "theme",
                "search_score",
                "metadata_score",
                "recommendation_score"
            ]
        ]
    )


if __name__ == "__main__":
    main()