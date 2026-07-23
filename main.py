"""
Test de la construction de l'index.
"""

from src.extraction.kaggle_extractor import KaggleExtractor
from src.nlp.embedding_engine import EmbeddingEngine
from src.database.database_manager import DatabaseManager
from src.profiling.theme_classifier import ThemeClassifier
from src.extraction.dataset_indexer import DatasetIndexer


def main():
    """
    Point d'entrée du programme de test.
    """

    extractor = KaggleExtractor()

    embedding_engine = EmbeddingEngine()

    database_manager = DatabaseManager()

    theme_classifier = ThemeClassifier()

    indexer = DatasetIndexer(
        extractor=extractor,
        embedding_engine=embedding_engine,
        database_manager=database_manager,
        theme_classifier=theme_classifier
    )

    indexer.build_index(
        query="health",
        limit=20
    )
    database_manager.connect()

    datasets = database_manager.get_all_datasets()

    print(datasets[["title", "tags", "theme"]].head(10))

    database_manager.close()


if __name__ == "__main__":
    main()