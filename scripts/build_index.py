"""
Reconstruction de l'index de recherche à partir du corpus figé.

Ce script reconstruit la base SQLite utilisée par l'application à
partir de :

- data/corpus_v1.csv : le corpus figé (métadonnées des datasets) ;
- data/descriptions.csv : les descriptions récupérées par
  scripts/fetch_descriptions.py (optionnel).

Pour chaque dataset, il :

1. ajoute la description, si elle a été récupérée ;
2. recalcule les scores de qualité des métadonnées ;
3. attribue un thème (à partir du titre et des tags) ;
4. génère l'embedding (titre, sous-titre, tags, puis description).

Avant d'écraser la base, une copie de sauvegarde est faite dans
database/datasets_backup_<date>.db.

Contrairement à build_database.py, ce script n'interroge pas Kaggle :
il utilise toujours les mêmes datasets, ce qui rend les résultats
reproductibles.

Utilisation (depuis la racine du projet) :
    python scripts/build_index.py                     # avec descriptions
    python scripts/build_index.py --no-descriptions   # comme au PFE

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Permet d'importer le package src/ quand le script est lancé
# depuis la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.database_manager import DatabaseManager  # noqa: E402
from src.extraction.dataset_indexer import DatasetIndexer  # noqa: E402
from src.nlp.embedding_engine import EmbeddingEngine  # noqa: E402
from src.profiling.metadata_profiler import MetadataProfiler  # noqa: E402
from src.profiling.theme_classifier import ThemeClassifier  # noqa: E402

CORPUS_PATH = PROJECT_ROOT / "data" / "corpus_v1.csv"
DESCRIPTIONS_PATH = PROJECT_ROOT / "data" / "descriptions.csv"

TEXT_COLUMNS = [
    "title", "subtitle", "description", "owner", "creator",
    "license", "last_updated", "url", "tags",
]

# Colonnes recalculées par ce script
COMPUTED_COLUMNS = [
    "theme", "completeness_score", "freshness_score",
    "reusability_score", "metadata_score",
]


def load_corpus(use_descriptions: bool) -> pd.DataFrame:
    """
    Charge le corpus figé et y ajoute les descriptions.
    """

    if not CORPUS_PATH.exists():
        raise FileNotFoundError(
            f"Corpus introuvable : {CORPUS_PATH}. "
            "Lancez d'abord scripts/export_corpus.py."
        )

    corpus = pd.read_csv(CORPUS_PATH)

    for column in TEXT_COLUMNS:
        corpus[column] = corpus[column].fillna("").astype(str)

    # Les scores et le thème sont recalculés
    corpus = corpus.drop(columns=COMPUTED_COLUMNS, errors="ignore")

    if not use_descriptions:
        return corpus

    if not DESCRIPTIONS_PATH.exists():
        raise FileNotFoundError(
            f"Descriptions introuvables : {DESCRIPTIONS_PATH}. "
            "Lancez d'abord scripts/fetch_descriptions.py, "
            "ou utilisez --no-descriptions."
        )

    descriptions = pd.read_csv(DESCRIPTIONS_PATH, keep_default_na=False)
    descriptions = descriptions.loc[
        descriptions["error"] == "", ["ref", "description"]
    ]

    corpus = corpus.drop(columns="description").merge(
        descriptions, on="ref", how="left"
    )
    corpus["description"] = corpus["description"].fillna("")

    return corpus


def backup_database(database_path: Path) -> None:
    """
    Copie la base existante avant de l'écraser.
    """

    if not database_path.exists():
        return

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = database_path.with_name(f"datasets_backup_{stamp}.db")

    shutil.copy2(database_path, backup_path)

    print(f"Sauvegarde de l'ancienne base : {backup_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Reconstruit l'index de recherche à partir du corpus figé."
    )
    parser.add_argument(
        "--no-descriptions",
        action="store_true",
        help="ne pas utiliser data/descriptions.csv (index comme au PFE)",
    )
    args = parser.parse_args()

    use_descriptions = not args.no_descriptions

    corpus = load_corpus(use_descriptions)

    with_description = (corpus["description"].str.strip() != "").sum()

    print(f"Datasets : {len(corpus)}")
    print(f"Avec description : {with_description}")

    print("\nCalcul des scores de qualité...")
    metadata_profiler = MetadataProfiler()
    corpus = metadata_profiler.profile_dataframe(corpus)

    print("Attribution des thèmes et génération des embeddings...")
    embedding_engine = EmbeddingEngine()
    indexer = DatasetIndexer(
        extractor=None,
        embedding_engine=embedding_engine,
        database_manager=None,
        theme_classifier=ThemeClassifier(),
        metadata_profiler=metadata_profiler,
    )
    embeddings = indexer.generate_embeddings(corpus)

    database_manager = DatabaseManager()
    backup_database(database_manager.database_path)

    print("Enregistrement dans SQLite...")
    database_manager.connect()

    try:
        database_manager.create_tables()
        database_manager.save_dataframe(corpus)
        database_manager.save_embeddings(embeddings)
    finally:
        database_manager.close()

    print("\nIndex reconstruit.")
    print(f"Datasets indexés : {len(corpus)}")
    print(f"Embeddings : {len(embeddings)}")
    print(
        "Score de complétude moyen : "
        f"{corpus['completeness_score'].mean():.3f}"
    )
    print(
        "Metadata Score moyen : "
        f"{corpus['metadata_score'].mean():.3f}"
    )
    print("Répartition des thèmes :")
    print(corpus["theme"].value_counts().to_string())


if __name__ == "__main__":
    main()
