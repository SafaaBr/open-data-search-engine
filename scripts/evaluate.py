"""
Évaluation du moteur de recherche.

Ce script compare plusieurs versions du moteur sur les requêtes de
evaluation/queries.csv, à partir du corpus figé (data/corpus_v1.csv)
et des descriptions (data/descriptions.csv).

Systèmes comparés :

- bm25           : recherche par mots-clés (BM25), avec descriptions ;
- embeddings_v1  : similarité cosinus, texte titre + tags (comme au PFE) ;
- embeddings_v2  : similarité cosinus, texte titre + sous-titre + tags
                   + description ;
- combined_v2    : moteur complet de l'application (seuil, filtre
                   lexical, score 0.5 recherche + 0.3 qualité
                   + 0.2 popularité), avec descriptions.

Tous les systèmes utilisent le même traitement de la requête
(mots-clés, traduction locale, synonymes).

Deux étapes :

1. python scripts/evaluate.py run
   Calcule le top 5 de chaque système pour chaque requête
   (evaluation/runs.csv) et prépare le fichier à annoter
   (evaluation/to_annotate.xlsx). Les résultats des différents
   systèmes sont regroupés, mélangés et anonymes : l'annotateur ne
   sait pas quel système a trouvé quel dataset.

2. Annoter evaluation/to_annotate.xlsx : colonne « relevance »,
   2 = pertinent, 1 = partiellement pertinent, 0 = non pertinent.

3. python scripts/evaluate.py score
   Enregistre les annotations (evaluation/qrels.csv) et calcule les
   métriques (evaluation/results.csv).

Métriques (sur les 5 premiers résultats) :

- P@5    : proportion de résultats pertinents (note >= 1) ;
- MRR@5  : 1 / rang du premier résultat pertinent (note >= 1) ;
- nDCG@5 : qualité de l'ordre, avec les notes 0 / 1 / 2.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import argparse
import hashlib
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Permet d'importer le package src/ quand le script est lancé
# depuis la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
EVAL_DIR = PROJECT_ROOT / "evaluation"
CACHE_DIR = EVAL_DIR / "cache"

CORPUS_PATH = DATA_DIR / "corpus_v1.csv"
DESCRIPTIONS_PATH = DATA_DIR / "descriptions.csv"
QUERIES_PATH = EVAL_DIR / "queries.csv"
RUNS_PATH = EVAL_DIR / "runs.csv"
ANNOTATION_PATH = EVAL_DIR / "to_annotate.xlsx"
QRELS_PATH = EVAL_DIR / "qrels.csv"
RESULTS_PATH = EVAL_DIR / "results.csv"

K = 5
SYSTEMS = ["bm25", "embeddings_v1", "embeddings_v2", "combined_v2"]

# Graine fixe : le mélange du fichier à annoter est toujours le même
SHUFFLE_SEED = 42


# ------------------------------------------------------------
# Chargement des données
# ------------------------------------------------------------

def load_corpus() -> pd.DataFrame:
    """
    Charge le corpus figé et y ajoute les descriptions.
    """

    corpus = pd.read_csv(CORPUS_PATH)

    for column in ["title", "subtitle", "tags", "owner", "creator",
                   "license", "last_updated", "url"]:
        corpus[column] = corpus[column].fillna("").astype(str)

    descriptions = pd.read_csv(DESCRIPTIONS_PATH, keep_default_na=False)
    descriptions = descriptions.loc[
        descriptions["error"] == "", ["ref", "description"]
    ]

    corpus = corpus.drop(columns="description").merge(
        descriptions, on="ref", how="left"
    )
    corpus["description"] = corpus["description"].fillna("")

    return corpus.sort_values("ref").reset_index(drop=True)


def split_tags(tags: str) -> list[str]:
    return [tag.strip() for tag in tags.split(",") if tag.strip()]


def dataset_texts(corpus: pd.DataFrame, engine, version: str) -> list[str]:
    """
    Construit le texte encodé de chaque dataset.

    v1 : titre + tags (le texte réellement encodé au PFE, puisque les
         descriptions étaient vides) ;
    v2 : titre + sous-titre + tags + description.
    """

    texts = []

    for _, row in corpus.iterrows():
        tags = split_tags(row["tags"])

        if version == "v1":
            texts.append(engine.prepare_dataset(row["title"], "", tags))
        else:
            texts.append(
                engine.prepare_dataset(
                    row["title"], row["description"], tags, row["subtitle"]
                )
            )

    return texts


def encode_corpus(texts: list[str], engine, name: str) -> np.ndarray:
    """
    Encode les textes du corpus, avec un cache sur disque.
    """

    digest = hashlib.sha1("\n".join(texts).encode("utf-8")).hexdigest()[:12]
    cache_path = CACHE_DIR / f"{name}_{digest}.npy"

    if cache_path.exists():
        return np.load(cache_path)

    print(f"Encodage du corpus ({name}, {len(texts)} datasets)...")

    embeddings = engine.model.encode(
        texts,
        batch_size=64,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype(np.float32)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(cache_path, embeddings)

    return embeddings


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


# ------------------------------------------------------------
# Étape 1 : classements et fichier à annoter
# ------------------------------------------------------------

def run():
    from rank_bm25 import BM25Okapi

    from src.profiling.metadata_profiler import MetadataProfiler
    from src.search.search_engine import SearchEngine

    corpus = load_corpus()
    queries = pd.read_csv(QUERIES_PATH)

    print(f"Corpus : {len(corpus)} datasets "
          f"({(corpus['description'].str.strip() != '').sum()} avec description)")
    print(f"Requêtes : {len(queries)}")

    search_engine = SearchEngine()
    engine = search_engine.embedding_engine

    embeddings = {
        "v1": encode_corpus(dataset_texts(corpus, engine, "v1"), engine, "v1"),
        "v2": encode_corpus(dataset_texts(corpus, engine, "v2"), engine, "v2"),
    }

    texts_v2 = dataset_texts(corpus, engine, "v2")
    bm25 = BM25Okapi([tokenize(text) for text in texts_v2])

    # Corpus prêt pour le moteur complet : scores de qualité recalculés
    # et embeddings v2 au format de la base SQLite
    combined_corpus = MetadataProfiler().profile_dataframe(corpus)
    combined_corpus["embedding"] = [vector.tobytes() for vector in embeddings["v2"]]

    runs = []

    for _, query_row in queries.iterrows():
        keywords, query_embedding = search_engine.prepare_query(query_row["query"])

        rankings = {}

        # BM25 sur les mots-clés traduits et enrichis
        scores = bm25.get_scores(tokenize(" ".join(keywords)))
        order = np.argsort(-scores, kind="stable")
        rankings["bm25"] = [corpus.at[i, "ref"] for i in order[:K] if scores[i] > 0]

        # Embeddings seuls
        for version in ["v1", "v2"]:
            similarities = embeddings[version] @ query_embedding
            order = np.argsort(-similarities, kind="stable")
            rankings[f"embeddings_{version}"] = [corpus.at[i, "ref"] for i in order[:K]]

        # Moteur complet de l'application
        results = search_engine.rank_candidates(
            combined_corpus.copy(), keywords, query_embedding, top_k=K
        )
        rankings["combined_v2"] = results["ref"].tolist() if not results.empty else []

        for system, refs in rankings.items():
            for rank, ref in enumerate(refs, start=1):
                runs.append({
                    "query_id": query_row["query_id"],
                    "system": system,
                    "rank": rank,
                    "ref": ref,
                })

    runs = pd.DataFrame(runs)
    runs.to_csv(RUNS_PATH, index=False, encoding="utf-8")

    write_annotation_file(runs, queries, corpus)


def summarize(row: pd.Series, max_length: int = 300) -> str:
    """
    Résumé affiché à l'annotateur : sous-titre et début de la description.
    """

    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", row["description"])
    text = re.sub(r"https?://\S+|<[^>]+>|[#*_>`|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > max_length:
        text = text[:max_length].rsplit(" ", 1)[0] + "…"

    parts = [row["subtitle"].strip(), text]

    return " | ".join(part for part in parts if part)


def write_annotation_file(runs: pd.DataFrame, queries: pd.DataFrame,
                          corpus: pd.DataFrame) -> None:
    """
    Prépare le fichier à annoter : une ligne par couple
    (requête, dataset), tous systèmes confondus, sans doublon.

    Les annotations déjà faites sont conservées si le fichier existe.
    """

    pool = runs[["query_id", "ref"]].drop_duplicates()
    pool = pool.merge(queries[["query_id", "query"]], on="query_id")
    pool = pool.merge(
        corpus[["ref", "title", "subtitle", "description", "url"]], on="ref"
    )
    pool["summary"] = pool.apply(summarize, axis=1)
    pool["relevance"] = ""

    if ANNOTATION_PATH.exists():
        previous = pd.read_excel(ANNOTATION_PATH, dtype={"relevance": str})
        previous = previous[["query_id", "ref", "relevance"]].fillna("")
        pool = pool.drop(columns="relevance").merge(
            previous, on=["query_id", "ref"], how="left"
        )
        pool["relevance"] = pool["relevance"].fillna("")

    # Mélange à l'intérieur de chaque requête : l'ordre ne révèle
    # ni le système ni le rang
    pool = (
        pool.sample(frac=1, random_state=SHUFFLE_SEED)
        .sort_values("query_id", kind="stable")
        .reset_index(drop=True)
    )

    pool = pool[["query_id", "query", "title", "summary", "url", "ref", "relevance"]]

    with pd.ExcelWriter(ANNOTATION_PATH, engine="openpyxl") as writer:
        pool.to_excel(writer, index=False, sheet_name="annotation")
        sheet = writer.sheets["annotation"]

        widths = {"A": 9, "B": 30, "C": 40, "D": 90, "E": 30, "F": 30, "G": 11}
        for column, width in widths.items():
            sheet.column_dimensions[column].width = width

        sheet.freeze_panes = "A2"

    to_do = (pool["relevance"].astype(str).str.strip() == "").sum()

    print(f"\nRésultats : {RUNS_PATH}")
    print(f"Fichier à annoter : {ANNOTATION_PATH}")
    print(f"Couples à juger : {len(pool)} (dont {to_do} sans note)")


# ------------------------------------------------------------
# Étape 2 : métriques
# ------------------------------------------------------------

def precision_at_k(grades: list[int], k: int = K) -> float:
    return sum(1 for grade in grades[:k] if grade >= 1) / k


def reciprocal_rank(grades: list[int], k: int = K) -> float:
    for rank, grade in enumerate(grades[:k], start=1):
        if grade >= 1:
            return 1 / rank
    return 0.0


def dcg(grades: list[int], k: int = K) -> float:
    return sum(
        (2 ** grade - 1) / math.log2(rank + 1)
        for rank, grade in enumerate(grades[:k], start=1)
    )


def ndcg_at_k(grades: list[int], all_grades: list[int], k: int = K) -> float:
    ideal = dcg(sorted(all_grades, reverse=True), k)
    return dcg(grades, k) / ideal if ideal > 0 else 0.0


def score():
    annotations = pd.read_excel(ANNOTATION_PATH, dtype={"relevance": str})
    annotations["relevance"] = (
        annotations["relevance"].fillna("").str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )

    missing = annotations[annotations["relevance"] == ""]
    invalid = annotations[~annotations["relevance"].isin(["", "0", "1", "2"])]

    if not invalid.empty:
        raise ValueError(
            "Notes invalides (attendu : 0, 1 ou 2) :\n"
            + invalid[["query_id", "title", "relevance"]].to_string(index=False)
        )

    if not missing.empty:
        raise ValueError(
            f"{len(missing)} couples ne sont pas encore notés, par exemple :\n"
            + missing[["query_id", "title"]].head().to_string(index=False)
        )

    qrels = annotations[["query_id", "ref", "relevance"]].copy()
    qrels["relevance"] = qrels["relevance"].astype(int)
    qrels.sort_values(["query_id", "ref"]).to_csv(
        QRELS_PATH, index=False, encoding="utf-8"
    )

    runs = pd.read_csv(RUNS_PATH)
    queries = pd.read_csv(QUERIES_PATH)

    grade_of = {
        (row.query_id, row.ref): row.relevance for row in qrels.itertuples()
    }

    rows = []

    for _, query_row in queries.iterrows():
        query_id = query_row["query_id"]
        all_grades = qrels.loc[qrels["query_id"] == query_id, "relevance"].tolist()

        for system in SYSTEMS:
            refs = (
                runs[(runs["query_id"] == query_id) & (runs["system"] == system)]
                .sort_values("rank")["ref"]
                .tolist()
            )
            grades = [grade_of.get((query_id, ref), 0) for ref in refs]

            rows.append({
                "query_id": query_id,
                "language": query_row["language"],
                "system": system,
                "results": len(refs),
                "P@5": precision_at_k(grades),
                "MRR@5": reciprocal_rank(grades),
                "nDCG@5": ndcg_at_k(grades, all_grades),
            })

    per_query = pd.DataFrame(rows)
    per_query.to_csv(RESULTS_PATH, index=False, encoding="utf-8")

    metrics = ["P@5", "MRR@5", "nDCG@5"]

    print(f"\nAnnotations : {len(qrels)} couples "
          f"(2 : {(qrels['relevance'] == 2).sum()}, "
          f"1 : {(qrels['relevance'] == 1).sum()}, "
          f"0 : {(qrels['relevance'] == 0).sum()})")
    print(f"Résultats par requête : {RESULTS_PATH}\n")

    print(f"Toutes les requêtes ({len(queries)}) :")
    print(
        to_markdown(per_query.groupby("system")[metrics].mean().reindex(SYSTEMS))
    )

    for language in ["en", "fr"]:
        subset = per_query[per_query["language"] == language]
        print(f"\nRequêtes « {language} » ({subset['query_id'].nunique()}) :")
        print(
            to_markdown(subset.groupby("system")[metrics].mean().reindex(SYSTEMS))
        )


def to_markdown(table: pd.DataFrame) -> str:
    """
    Convertit un tableau de métriques en tableau Markdown (pour le README).
    """

    header = "| system | " + " | ".join(table.columns) + " |"
    separator = "|---|" + "---|" * len(table.columns)
    lines = [header, separator]

    for system, values in table.iterrows():
        cells = " | ".join(f"{value:.3f}" for value in values)
        lines.append(f"| {system} | {cells} |")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Évaluation du moteur de recherche.")
    parser.add_argument("step", choices=["run", "score"])
    args = parser.parse_args()

    if args.step == "run":
        run()
    else:
        score()


if __name__ == "__main__":
    main()
