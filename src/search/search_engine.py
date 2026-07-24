"""
Module de recherche sémantique des jeux de données.

Ce module orchestre l'ensemble du pipeline de recherche :

- traitement de la requête utilisateur ;
- traduction des mots-clés ;
- enrichissement par synonymes ;
- génération de l'embedding de la requête ;
- chargement des datasets indexés ;
- calcul des similarités ;
- classement des résultats.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import pandas as pd

from src.nlp.query_processor import QueryProcessor
from src.nlp.translator import Translator
from src.nlp.synonym_engine import SynonymEngine
from src.nlp.embedding_engine import EmbeddingEngine

from src.database.database_manager import DatabaseManager

from src.ranking.ranking import Ranking


class SearchEngine:
    """
    Classe responsable du moteur de recherche sémantique.
    """

    def __init__(self):
        """
        Initialise les différents modules du moteur.
        """

        self.query_processor = QueryProcessor()
        self.translator = Translator()
        self.synonym_engine = SynonymEngine()
        self.embedding_engine = EmbeddingEngine()
        self.database_manager = DatabaseManager()
        self.ranking = Ranking()

        print("SearchEngine initialisé.")


    def search(
        self,
        query: str,
        theme: str | None = None,
        top_k: int = 10
    ) -> pd.DataFrame:
        """
        Exécute une recherche sémantique.

        Parameters
        ----------
        query : str
            Requête utilisateur.

        theme : str, optional
            Thème à filtrer.

        top_k : int
            Nombre de résultats.

        Returns
        -------
        pandas.DataFrame
            Résultats classés.
        """

        # Traitement de la requête
        processed_query = self.query_processor.process_query(query)

        keywords = processed_query["keywords"]

        # Traduction
        keywords = self.translator.translate_keywords(
            keywords,
            processed_query["language"]
        )

        # Enrichissement
        keywords = self.synonym_engine.enrich_keywords(
            keywords
        )

        # Embedding de la requête
        query_embedding = self.embedding_engine.encode_keywords(
            keywords
        )

        # Chargement des datasets indexés
        self.database_manager.connect()

        try:

            dataframe = self.database_manager.load_search_index()

        finally:

            self.database_manager.close()

        #
        # Ici viendra le calcul des similarités

        #filtrer par domaine
        if theme is not None:
            dataframe = dataframe[
                dataframe["theme"].str.lower() == theme.lower()
            ].reset_index(drop=True)

        if dataframe.empty:
            return dataframe
        
        # Conversion des embeddings SQLite
        dataset_embeddings = self.embedding_engine.decode_embeddings(
            dataframe["embedding"]
        )

        # Calcul des similarités
        similarities = self.embedding_engine.compute_similarity(
            query_embedding,
            dataset_embeddings
        )

        # Ajout du Search Score
        dataframe["search_score"] = similarities.round(3)


        # Classement
        dataframe = self.ranking.rank_dataframe(dataframe)

        # Retour des meilleurs résultats
        return self.ranking.get_top_k(
            dataframe,
            k=top_k
        )