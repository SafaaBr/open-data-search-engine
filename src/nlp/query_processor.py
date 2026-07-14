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

import spacy

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


class QueryProcessor:
    """
    Classe responsable du traitement des requêtes utilisateur.
    """

    def __init__(self):
        """
        Initialise le processeur de requêtes.
         """
        self.nlp_fr = spacy.load("fr_core_news_sm")
        self.nlp_en = spacy.load("en_core_web_sm")
        
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
        cleaned_query = self.clean_query(query)

        if len(cleaned_query.split()) < 2:
            return "unknown"

        try:
            return detect(cleaned_query)

        except LangDetectException:
            return "unknown"


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
        custom_stopwords = {
            "vouloir",
            "veux",
            "chercher",
            "cherche",
            "need",
            "want",
            "looking"
        }
        language = self.detect_language(query)

        if language == "fr":
            doc = self.nlp_fr(query)

        else:
            doc = self.nlp_en(query)

        keywords = [
            token.lemma_.lower()
            for token in doc
            if not token.is_stop
            and not token.is_punct
            and token.is_alpha
            and token.lemma_.lower() not in custom_stopwords
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
        
        if (
            "apprendre" in query
            or "learn" in query
        ):
            return "learning"

        if (
            "classification" in query
        ):
            return "classification"

        if (
            "régression" in query
            or "regression" in query
        ):
            return "regression"

        if (
            "clustering" in query
            or "regroupement" in query
        ):
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