"""
Module de traitement des requêtes utilisateur.

Ce module est responsable de :

- nettoyer les requêtes ;
- détecter la langue ;
- extraire les mots-clés ;
- détecter l'intention de recherche.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import re


class QueryProcessor:
    """
    Classe responsable du traitement des requêtes utilisateur.
    """

    def __init__(self):
        """
        Initialise le processeur de requêtes.
        """

        print("QueryProcessor initialisé.")

    def clean_query(
        self,
        query: str
    ) -> str:
        """
        Nettoie une requête utilisateur.

        Parameters
        ----------
        query : str
            Requête utilisateur.

        Returns
        -------
        str
            Requête nettoyée.
        """

        query = query.lower()

        query = re.sub(
            r"[^\w\s]",
            "",
            query
        )

        query = re.sub(
            r"\s+",
            " ",
            query
        ).strip()

        return query

    def detect_language(
        self,
        query: str
    ) -> str:
        """
        Détecte la langue de la requête.

        Parameters
        ----------
        query : str
            Requête utilisateur.

        Returns
        -------
        str
            Langue détectée.
        """

        french_keywords = {
            "je",
            "cherche",
            "dataset",
            "données",
            "apprendre",
            "classification",
            "régression",
            "sur"
        }

        query_words = set(query.lower().split())

        if french_keywords.intersection(query_words):
            return "fr"

        return "en"

    def extract_keywords(
        self,
        query: str
    ) -> list[str]:
        """
        Extrait les mots-clés d'une requête.

        Parameters
        ----------
        query : str
            Requête utilisateur.

        Returns
        -------
        list[str]
            Liste des mots-clés.
        """

        stopwords = {
            "je",
            "veux",
            "un",
            "une",
            "des",
            "le",
            "la",
            "les",
            "de",
            "du",
            "pour",
            "sur",
            "avec",
            "et",
            "à",
            "apprendre",
            "cherche"
        }

        words = self.clean_query(query).split()

        keywords = [
            word
            for word in words
            if word not in stopwords
        ]

        return keywords

    def detect_intent(
        self,
        query: str
    ) -> str:
        """
        Détecte l'intention de recherche.

        Parameters
        ----------
        query : str
            Requête utilisateur.

        Returns
        -------
        str
            Intention détectée.
        """

        query = query.lower()

        if "apprendre" in query:
            return "learning"

        if "classification" in query:
            return "classification"

        if "régression" in query:
            return "regression"

        if "clustering" in query:
            return "clustering"

        return "general_search"

    def process_query(
        self,
        query: str
    ) -> dict:
        """
        Traite complètement une requête utilisateur.

        Parameters
        ----------
        query : str
            Requête utilisateur.

        Returns
        -------
        dict
            Résultat du traitement.
        """

        cleaned_query = self.clean_query(query)

        return {
            "original_query": query,
            "clean_query": cleaned_query,
            "language": self.detect_language(cleaned_query),
            "keywords": self.extract_keywords(cleaned_query),
            "intent": self.detect_intent(cleaned_query)
        }