from src.database.database_manager import DatabaseManager
from src.extraction.kaggle_extractor import KaggleExtractor
from src.nlp.embedding_engine import EmbeddingEngine
from src.profiling.metadata_profiler import MetadataProfiler
from src.profiling.theme_classifier import ThemeClassifier
from src.extraction.dataset_indexer import DatasetIndexer

# Initialisation
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

print("===================================")
print("Authentification Kaggle...")
print("===================================")

extractor.authenticate()

print("\n===================================")
print("Recherche de datasets...")
print("===================================")

datasets = extractor.search_to_dataframe(
    query="sports",
    limit=5
)

print("\nNombre de datasets :", len(datasets))

print("\nColonnes :")
print(datasets.columns.tolist())

print("\nAperçu :")
print(
    datasets[
        ["title", "description", "tags"]
    ].head()
)

print("\n===================================")
print("Test MetadataProfiler...")
print("===================================")

datasets = metadata_profiler.profile_dataframe(datasets)

print(
    datasets[
        [
            "title",
            "metadata_score",
            "completeness_score",
            "freshness_score",
            "reusability_score",
        ]
    ]
)

print("\n===================================")
print("Test Embeddings...")
print("===================================")

embeddings = indexer.generate_embeddings(datasets)

print(embeddings.head())

print("\n===================================")
print("Tout fonctionne correctement.")
print("===================================")