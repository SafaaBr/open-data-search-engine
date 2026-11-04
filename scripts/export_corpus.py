"""
Export du corpus indexé vers un fichier CSV.

Ce script lit la table « datasets » de la base SQLite locale et
l'enregistre dans data/corpus_v1.csv. Ce fichier est un instantané
figé du corpus : il permet de refaire l'évaluation sur exactement
les mêmes datasets, même si Kaggle évolue entre-temps.

Les embeddings ne sont pas exportés : ils se recalculent à partir
des métadonnées et du modèle SentenceTransformer.

La base SQLite n'est pas modifiée.

Utilisation (depuis la racine du projet) :
    python scripts/export_corpus.py

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import sys
from datetime import date
from pathlib import Path

# Permet d'importer le package src/ quand le script est lancé
# depuis la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database.database_manager import DatabaseManager  # noqa: E402

OUTPUT_PATH = PROJECT_ROOT / "data" / "corpus_v1.csv"


def main():
    database_manager = DatabaseManager()

    if not database_manager.database_path.exists():
        raise FileNotFoundError(
            f"Base introuvable : {database_manager.database_path}. "
            "Lancez d'abord build_database.py."
        )

    database_manager.connect()

    try:
        datasets = database_manager.get_all_datasets()
    finally:
        database_manager.close()

    # Tri par référence : le fichier est identique d'un export à l'autre
    datasets = datasets.sort_values("ref").reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    datasets.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    empty_descriptions = (
        datasets["description"].fillna("").str.strip() == ""
    ).sum()

    print(f"Export terminé : {OUTPUT_PATH}")
    print(f"Date de l'export : {date.today().isoformat()}")
    print(f"Nombre de datasets : {len(datasets)}")
    print(f"Nombre de colonnes : {len(datasets.columns)}")
    print(f"Descriptions vides : {empty_descriptions}")


if __name__ == "__main__":
    main()
