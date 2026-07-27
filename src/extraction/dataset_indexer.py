"""
Module de construction de l'index des datasets.

Ce module est responsable de :

- extraire les métadonnées des datasets depuis Kaggle ;
- générer les embeddings des métadonnées ;
- enregistrer les métadonnées dans la base SQLite ;
- enregistrer les embeddings associés.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import pandas as pd


class DatasetIndexer:
    """
    Classe responsable de la construction de l'index local
    des datasets, de l'attribution automatique des thèmes
    et de la génération des embeddings.
    """

    def __init__(
        self,
        extractor,
        embedding_engine,
        database_manager, 
        theme_classifier,
        metadata_profiler
    ):
        """
        Initialise le DatasetIndexer.

        Parameters
        ----------
        extractor : KaggleExtractor
            Module d'extraction des métadonnées.

        embedding_engine : EmbeddingEngine
            Module de génération des embeddings.

        database_manager : DatabaseManager
            Gestionnaire de la base SQLite.
        
        theme_classifier : ThemeClassifier
            Module de classification des datasets par thème.
        
        metadata_profiler : MetadataProfiler
            Module d'évaluation de la qualité des métadonnées.
        """

        self.extractor = extractor
        self.embedding_engine = embedding_engine
        self.database_manager = database_manager
        self.theme_classifier = theme_classifier
        self.metadata_profiler = metadata_profiler

        print("DatasetIndexer initialisé.")

    def generate_embeddings(
        self,
        datasets: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Génère les embeddings des datasets.

        Parameters
        ----------
        datasets : pandas.DataFrame
            Métadonnées des datasets.

        Returns
        -------
        pandas.DataFrame
            DataFrame contenant les embeddings.
        """

        embeddings = []
        datasets["theme"] = ""

        for index, dataset in datasets.iterrows():

            tags = []

            if pd.notna(dataset["tags"]):
                tags = dataset["tags"].split(", ")


            theme = self.theme_classifier.classify(
                title=dataset["title"],
                tags=tags,
                description=dataset["description"]
            )

            datasets.at[index, "theme"] = theme

            embedding = self.embedding_engine.encode_dataset(
                title=dataset["title"],
                description=dataset["description"],
                tags=tags
            )

            embeddings.append(
                {
                    "dataset_ref": dataset["ref"],
                    "embedding": embedding.tobytes()
                }
            )


        return pd.DataFrame(embeddings)

    def build_index(
        self,
        query: str,
        limit: int = 100
    ) -> None:
        """
        Construit l'index local des datasets.

        Parameters
        ----------
        query : str
            Mot-clé utilisé pour récupérer les datasets.

        limit : int
            Nombre maximal de datasets à indexer.
        """

        print("Authentification Kaggle...")

        self.extractor.authenticate()

        print("Extraction des métadonnées...")

        datasets = self.extractor.search_to_dataframe(
            query=query,
            limit=limit
        )

        print("Évaluation de la qualité des métadonnées...")

        datasets = self.metadata_profiler.profile_dataframe(
            datasets
        )

        print("Génération des embeddings...")

        embeddings = self.generate_embeddings(
            datasets
        )

        print("Connexion à SQLite...")

        self.database_manager.connect()

        try:
            self.database_manager.create_tables()

            print("Enregistrement des métadonnées...")

            self.database_manager.save_dataframe(datasets)

            print("Enregistrement des embeddings...")

            self.database_manager.save_embeddings(embeddings)

        finally:
            self.database_manager.close()

        print("Index construit avec succès.")

    