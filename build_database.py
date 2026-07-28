import pandas as pd

from src.database.database_manager import DatabaseManager
from src.extraction.kaggle_extractor import KaggleExtractor
from src.extraction.dataset_indexer import DatasetIndexer
from src.nlp.embedding_engine import EmbeddingEngine
from src.profiling.metadata_profiler import MetadataProfiler
from src.profiling.theme_classifier import ThemeClassifier


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

queries = [
    "health",
    "sports",
    "finance",
    "education",
    "environment",
    "business",
    "transport",
    "energy",
    "agriculture",
    "climate"
]

limit = 50

print("Authentification Kaggle...")
extractor.authenticate()


all_datasets = []

for query in queries:
    print(f"\nExtraction des datasets : {query}")

    df = extractor.search_to_dataframe(
        query=query,
        limit=limit
    )

    print(f"{len(df)} datasets récupérés.")

    all_datasets.append(df)

# Fusion des résultats
datasets = pd.concat(all_datasets, ignore_index=True)

print(f"\nNombre total avant suppression des doublons : {len(datasets)}")

# Suppression des doublons
datasets = datasets.drop_duplicates(subset="ref")

print(f"Nombre total après suppression des doublons : {len(datasets)}")

# Calcul des scores de qualité
print("\nCalcul des scores de qualité...")
datasets = metadata_profiler.profile_dataframe(datasets)

# Génération des embeddings
print("Génération des embeddings...")
embeddings = indexer.generate_embeddings(datasets)

# Sauvegarde dans SQLite
print("Sauvegarde dans SQLite...")

database_manager.connect()
database_manager.create_tables()

database_manager.save_dataframe(datasets)
database_manager.save_embeddings(embeddings)

database_manager.close()

print("\nBase de données construite avec succès !")