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

        # Quelques mots français très fréquents
        french_words = {
            "je", "cherche", "veux", "sur", "avec",
            "données", "santé", "diabète",
             "régression"
        }

        words = set(cleaned_query.split())

        if french_words.intersection(words):
            return "fr"

        try:
            language = detect(cleaned_query)

            if language in ["fr", "en"]:
                return language

            return "unknown"

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
            "apprendre",
            "learn",
            "want",
            "looking"
        }
        language = self.detect_language(query)

        if language == "fr":
            doc = self.nlp_fr(query)

        else:
            doc = self.nlp_en(query)

        keywords = []

        for token in doc:

            if (
                token.is_stop
                or token.is_punct
                or not token.is_alpha
            ):
                continue

            keyword = token.lemma_.lower()

            if keyword in custom_stopwords:
                continue

            # Si le lemme est vide ou bizarre,
            # on garde le mot original.
            if len(keyword) < 3:
                keyword = token.text.lower()

            keywords.append(keyword)

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