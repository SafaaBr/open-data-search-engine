"""
Récupération des descriptions des datasets du corpus.

L'API Kaggle utilisée pour la recherche (dataset_list) ne renvoie pas
la description des datasets : le champ « description » du corpus est
donc vide. Ce script appelle, pour chaque dataset de
data/corpus_v1.csv, l'API qui renvoie sa fiche complète
(dataset_metadata), et enregistre la description dans
data/descriptions.csv.

Le script :

- fait une courte pause entre deux appels, pour ne pas surcharger Kaggle ;
- enregistre chaque résultat dès qu'il est obtenu ;
- reprend là où il s'est arrêté s'il est relancé (les datasets déjà
  traités sont ignorés) ;
- note les erreurs dans la colonne « error » au lieu de s'arrêter.

Ni la base SQLite ni corpus_v1.csv ne sont modifiés.

Utilisation (depuis la racine du projet) :
    python scripts/fetch_descriptions.py

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import csv
import json
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# Permet d'importer le package src/ quand le script est lancé
# depuis la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.kaggle_extractor import KaggleExtractor  # noqa: E402

CORPUS_PATH = PROJECT_ROOT / "data" / "corpus_v1.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "descriptions.csv"

FIELDS = ["ref", "description", "fetched_at", "error"]

# Pause entre deux appels à l'API (en secondes)
PAUSE_SECONDS = 0.5


def load_done_refs() -> set:
    """
    Retourne les références déjà traitées avec succès.

    Les datasets en erreur ne sont pas considérés comme traités :
    ils seront réessayés au prochain lancement.
    """

    if not OUTPUT_PATH.exists():
        return set()

    done = pd.read_csv(OUTPUT_PATH, keep_default_na=False)

    return set(done.loc[done["error"] == "", "ref"])


def fetch_description(api, ref: str) -> str:
    """
    Télécharge la fiche d'un dataset et retourne sa description.
    """

    with tempfile.TemporaryDirectory() as folder:
        api.dataset_metadata(ref, path=folder)

        metadata_file = Path(folder) / "dataset-metadata.json"

        with open(metadata_file, encoding="utf-8") as file:
            metadata = json.load(file)

    # Selon les versions, le fichier contient du JSON encodé deux fois
    if isinstance(metadata, str):
        metadata = json.loads(metadata)

    return metadata.get("description") or ""


def compact_output():
    """
    Garde une seule ligne par dataset dans le fichier de résultats.

    Quand un dataset en erreur est réessayé avec succès, il apparaît
    deux fois : on garde la ligne réussie (ou, à défaut, la dernière).
    """

    results = pd.read_csv(OUTPUT_PATH, keep_default_na=False)
    results["success"] = results["error"] == ""

    results = (
        results.sort_values(["ref", "success", "fetched_at"])
        .drop_duplicates(subset="ref", keep="last")
        .drop(columns="success")
        .sort_values("ref")
    )

    results.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")


def main():
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(
            f"Corpus introuvable : {CORPUS_PATH}. "
            "Lancez d'abord scripts/export_corpus.py."
        )

    refs = pd.read_csv(CORPUS_PATH)["ref"].tolist()
    done_refs = load_done_refs()
    todo = [ref for ref in refs if ref not in done_refs]

    print(f"Datasets dans le corpus : {len(refs)}")
    print(f"Déjà traités : {len(done_refs)}")
    print(f"À traiter : {len(todo)}")

    if not todo:
        print("Rien à faire.")
        return

    extractor = KaggleExtractor()
    extractor.authenticate()

    # Si le fichier existe déjà, on ajoute à la suite
    write_header = not OUTPUT_PATH.exists()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    errors = 0

    with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)

        if write_header:
            writer.writeheader()

        for position, ref in enumerate(todo, start=1):
            row = {
                "ref": ref,
                "description": "",
                "fetched_at": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "error": "",
            }

            try:
                row["description"] = fetch_description(extractor.api, ref)
            except Exception as error:
                row["error"] = str(error)[:200] or type(error).__name__
                errors += 1

            writer.writerow(row)

            # Écriture immédiate sur le disque : rien n'est perdu
            # si le script est interrompu.
            file.flush()

            if position % 50 == 0 or position == len(todo):
                print(f"{position}/{len(todo)} traités ({errors} erreurs)")

            time.sleep(PAUSE_SECONDS)

    compact_output()

    print(f"Terminé. Résultats dans {OUTPUT_PATH}")

    if errors:
        print(
            f"{errors} erreurs : relancez le script pour réessayer "
            "uniquement ces datasets."
        )


if __name__ == "__main__":
    main()
