"""
Module de classement des jeux de données.

Ce module calcule un score de recommandation en combinant
la pertinence de la recherche, la qualité des métadonnées
et la popularité.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import math
import pandas as pd


class Ranking:
    """
    Classe responsable du classement des datasets.
    """

    def __init__(self):
        """
        Initialise le module de classement.
        """
        print("Ranking initialisé.")

    def calculate_popularity_score(
        self,
        downloads: int,
        votes: int,
        views: int
    ) -> float:
        """
        Calcule le Popularity Index d'un jeu de données.

        Le score est basé sur trois indicateurs de popularité :
        - le nombre de téléchargements,
        - le nombre de votes,
        - le nombre de vues.

        Une transformation logarithmique est appliquée afin de réduire
        l'influence des valeurs extrêmes.

        Parameters
        ----------
        downloads : int
            Nombre de téléchargements.
        votes : int
            Nombre de votes.
        views : int
            Nombre de vues.

        Returns
        -------
        float
            Popularity Index.
        """

        downloads_score = math.log1p(downloads)
        votes_score = math.log1p(votes)
        views_score = math.log1p(views)

        popularity_index = (
            3 * downloads_score +
            2 * votes_score +
            1 * views_score
        ) / 6

        return round(popularity_index, 3)
    
    def normalize_popularity_scores(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Normalise les Popularity Index entre 0 et 1.

        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame contenant la colonne 'popularity_index'.

        Returns
        -------
        pd.DataFrame
            DataFrame enrichi avec la colonne 'popularity_score'.
        """

        dataframe = dataframe.copy()

        min_score = dataframe["popularity_index"].min()
        max_score = dataframe["popularity_index"].max()

        if max_score == min_score:
            dataframe["popularity_score"] = 1.0
        else:
            dataframe["popularity_score"] = (
                dataframe["popularity_index"] - min_score
            ) / (max_score - min_score)

        dataframe["popularity_score"] = dataframe["popularity_score"].round(3)

        return dataframe
    
    def calculate_recommendation_score(
        self,
        search_score: float,
        metadata_score: float,
        popularity_score: float
    ) -> float:

        """
        Calcule le Recommendation Score d'un jeu de données.

        Le score de recommandation combine trois critères :
        - la pertinence par rapport à la requête utilisateur,
        - la qualité des métadonnées,
        - la popularité du jeu de données.

        Parameters
        ----------
        search_score : float
            Score de pertinence de la recherche.
        metadata_score : float
            Score de qualité des métadonnées.
        popularity_score : float
            Score de popularité.

        Returns
        -------
        float
            Recommendation Score normalisé entre 0 et 1.
        """

        recommendation_score = (
            0.50 * search_score +
            0.30 * metadata_score +
            0.20 * popularity_score
        )

        return round(recommendation_score, 3)
    def rank_dataframe(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Classe les jeux de données selon leur Recommendation Score.

        Cette méthode calcule successivement :
        - le Popularity Index ;
        - le Popularity Score ;
        - le Recommendation Score.

        Les datasets sont ensuite triés par ordre décroissant de
        Recommendation Score.

        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame contenant les jeux de données enrichis
            avec le Metadata Score et le Search Score.

        Returns
        -------
        pd.DataFrame
            DataFrame classé selon le Recommendation Score.
        """

        dataframe = dataframe.copy()

        # Calcul du Popularity Index
        dataframe["popularity_index"] = dataframe.apply(
            lambda row: self.calculate_popularity_score(
                downloads=row["downloads"],
                votes=row["votes"],
                views=row["views"],
            ),
            axis=1,
        )

        # Normalisation du Popularity Index
        # afin d'obtenir un Popularity Score entre 0 et 1
        dataframe = self.normalize_popularity_scores(dataframe)

        # Calcul du Recommendation Score
        dataframe["recommendation_score"] = dataframe.apply(
            lambda row: self.calculate_recommendation_score(
                search_score=row["search_score"],
                metadata_score=row["metadata_score"],
                popularity_score=row["popularity_score"],
            ),
            axis=1,
        )

        # Classement décroissant
        dataframe = dataframe.sort_values(
            by="recommendation_score",
            ascending=False
        ).reset_index(drop=True)

        return dataframe
    
    def get_top_k(
        self,
        dataframe: pd.DataFrame,
        k: int = 5
    ) -> pd.DataFrame:
        """
        Retourne les k jeux de données les mieux classés.

        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame trié selon le Recommendation Score.
        k : int, optional
            Nombre de jeux de données à retourner (par défaut : 5).

        Returns
        -------
        pd.DataFrame
            DataFrame contenant les k meilleurs jeux de données.
        """

        return dataframe.head(k).reset_index(drop=True)