from src.database.database_manager import DatabaseManager
from src.extraction.kaggle_extractor import KaggleExtractor
from src.nlp.embedding_engine import EmbeddingEngine
from src.profiling.metadata_profiler import MetadataProfiler
from src.profiling.theme_classifier import ThemeClassifier
from src.extraction.dataset_indexer import DatasetIndexer
from src.search.search_engine import SearchEngine

# ======================================================
# INITIALISATION
# ======================================================

extractor = KaggleExtractor()
embedding_engine = EmbeddingEngine()
database_manager = DatabaseManager()
theme_classifier = ThemeClassifier()
metadata_profiler = MetadataProfiler()

search_engine = SearchEngine()

indexer = DatasetIndexer(
    extractor=extractor,
    embedding_engine=embedding_engine,
    database_manager=database_manager,
    theme_classifier=theme_classifier,
    metadata_profiler=metadata_profiler
)

# ======================================================
# 1. VALIDATION DE LA COUCHE D'ACQUISITION
# ======================================================

print("=" * 60)
print("VALIDATION DE LA COUCHE D'ACQUISITION")
print("=" * 60)

print("\nAuthentification Kaggle...")

extractor.authenticate()

print("Authentification réussie.")

print("\nExtraction des datasets...")

datasets = extractor.search_to_dataframe(
    query="weather",
    limit=20
)

print(f"\nNombre de datasets récupérés : {len(datasets)}")

print("\nColonnes extraites :")
print(datasets.columns.tolist())

print("\nAperçu des métadonnées :")

print(
    datasets[
        [
            "title",
            "description",
            "tags"
        ]
    ].head()
)

# ======================================================
# 2. VALIDATION DU METADATA PROFILER
# ======================================================

print("\n")
print("=" * 60)
print("VALIDATION DU METADATA PROFILER")
print("=" * 60)

datasets = metadata_profiler.profile_dataframe(datasets)

print(
    datasets[
        [
            "title",
            "completeness_score",
            "freshness_score",
            "reusability_score",
            "metadata_score"
        ]
    ]
)

# ======================================================
# 3. VALIDATION DU THEME CLASSIFIER
# ======================================================

print("\n")
print("=" * 60)
print("VALIDATION DU THEME CLASSIFIER")
print("=" * 60)

themes = []

for _, row in datasets.iterrows():

    # Les tags sont stockés sous forme de chaîne "tag1, tag2, ..."
    tags = []

    if row["tags"]:
        tags = [
            tag.strip()
            for tag in row["tags"].split(",")
        ]

    theme = theme_classifier.classify(
        title=row["title"],
        tags=tags,
        description=row["description"]
    )

    themes.append(theme)

datasets["theme"] = themes

print(
    datasets[
        [
            "title",
            "theme"
        ]
    ]
)

# ======================================================
# 4. VALIDATION DE L'EMBEDDING ENGINE
# ======================================================

print("\n")
print("=" * 60)
print("VALIDATION DE L'EMBEDDING ENGINE")
print("=" * 60)

embeddings = indexer.generate_embeddings(datasets)

print("\nNombre d'embeddings générés :", len(embeddings))

print("\nDatasets et embeddings générés :")

print(
    embeddings[["dataset_ref"]].head()
)

# Vérification de la dimension des embeddings
if len(embeddings) > 0:
    first_embedding = embeddings.iloc[0]["embedding"]

    print("\nDimension de l'embedding :", len(first_embedding))

print("\nGénération des embeddings terminée avec succès.")

# ======================================================
# 5. VALIDATION DU STOCKAGE SQLITE
# ======================================================

print("\n")
print("=" * 60)
print("VALIDATION DU STOCKAGE SQLITE")
print("=" * 60)

database_manager.connect()

print("Connexion à SQLite réussie.")

database_manager.create_tables()

print("Tables créées ou déjà existantes.")

database_manager.save_dataframe(datasets)

print(f"{len(datasets)} datasets enregistrés.")

database_manager.save_embeddings(embeddings)

print(f"{len(embeddings)} embeddings enregistrés.")

database_manager.close()

print("Connexion fermée.")

# ============================================================
# 6. VALIDATION DU TRAITEMENT DES REQUÊTES
# ============================================================

print("\n")
print("=" * 60)
print("VALIDATION DU TRAITEMENT DES REQUÊTES")
print("=" * 60)





# ------------------------------------------------------------
# 7. Requête de test
# ------------------------------------------------------------

query = "Je veux une dataset de la météo"

print("\nRequête de test :", query)


# ------------------------------------------------------------
# 8.Recherche sémantique complète
# ------------------------------------------------------------

results = search_engine.search(
    query=query,
    top_k=5
)


# ------------------------------------------------------------
# 9. Résultats finaux
# ------------------------------------------------------------

print("\n")
print("=" * 60)
print("RÉSULTATS FINAUX")
print("=" * 60)

if results.empty:

    print("Aucun résultat trouvé.")

else:

    columns_to_display = [
        "title",
        "search_score"
    ]

    # Ajouter le Recommendation Score s'il existe
    if "recommendation_score" in results.columns:
        columns_to_display.append("recommendation_score")

    print(
        results[columns_to_display].to_string(index=False)
    )

print("\nRecherche terminée avec succès.")
# ======================================================
# FIN
# ======================================================

print("\n")
print("=" * 60)
print("VALIDATION TERMINEE AVEC SUCCES")
print("=" * 60)