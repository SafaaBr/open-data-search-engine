"""
Module de recherche des jeux de données.

Ce module orchestre l'ensemble du pipeline de recherche :
- recherche des datasets sur Kaggle ;
- évaluation de la qualité des métadonnées ;
- classement des résultats ;
- retour des meilleurs datasets.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import pandas as pd

from kaggle_extractor import KaggleExtractor
from metadata_profiler import MetadataProfiler
from ranking import Ranking


class SearchEngine:
    """
    Classe responsable de l'orchestration du moteur de recherche.
    """

    def __init__(self):
        """
        Initialise le moteur de recherche et ses composants.
        """

        self.extractor = KaggleExtractor()
        self.metadata_profiler = MetadataProfiler()
        self.ranking = Ranking()

    def search(
        self,
        query: str,
        max_results: int = 50
    ) -> pd.DataFrame:
        """
        Recherche des datasets correspondant à une requête.

        Parameters
        ----------
        query : str
            Requête de recherche.
        max_results : int, optional
            Nombre maximal de datasets à récupérer.

        Returns
        -------
        pd.DataFrame
            DataFrame contenant les datasets trouvés.
        """

        return self.extractor.search_datasets(
            query=query,
            max_results=max_results
        )

    def evaluate_metadata(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Évalue la qualité des métadonnées.

        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame contenant les métadonnées des datasets.

        Returns
        -------
        pd.DataFrame
            DataFrame enrichi avec les scores de qualité.
        """

        return self.metadata_profiler.profile_dataframe(dataframe)

    def rank_results(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Classe les datasets selon leur Recommendation Score.

        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame enrichi avec les scores de qualité.

        Returns
        -------
        pd.DataFrame
            DataFrame classé.
        """

        return self.ranking.rank_dataframe(dataframe)

    def get_top_results(
        self,
        dataframe: pd.DataFrame,
        top_k: int = 5
    ) -> pd.DataFrame:
        """
        Retourne les meilleurs datasets.

        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame classé.
        top_k : int, optional
            Nombre de résultats à retourner.

        Returns
        -------
        pd.DataFrame
            Les meilleurs datasets.
        """

        return self.ranking.get_top_k(
            dataframe=dataframe,
            k=top_k
        )

    def run(
        self,
        query: str,
        max_results: int = 50,
        top_k: int = 5
    ) -> pd.DataFrame:
        """
        Exécute l'ensemble du pipeline de recherche.

        Parameters
        ----------
        query : str
            Requête utilisateur.
        max_results : int, optional
            Nombre maximal de datasets récupérés.
        top_k : int, optional
            Nombre de résultats finaux.

        Returns
        -------
        pd.DataFrame
            Les meilleurs datasets recommandés.
        """

        # Recherche des datasets
        dataframe = self.search(
            query=query,
            max_results=max_results
        )

        # Évaluation de la qualité des métadonnées
        dataframe = self.evaluate_metadata(dataframe)

        # Classement des datasets
        dataframe = self.rank_results(dataframe)

        # Sélection des meilleurs résultats
        dataframe = self.get_top_results(
            dataframe=dataframe,
            top_k=top_k
        )

        return dataframe