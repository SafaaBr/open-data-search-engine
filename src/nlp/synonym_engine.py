"""
Module d'enrichissement des mots-clés.

Ce module est responsable de :

- charger le dictionnaire de synonymes ;
- rechercher les synonymes d'un mot-clé ;
- enrichir une liste de mots-clés.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import json
from pathlib import Path


class SynonymEngine:
    """
    Classe responsable de l'enrichissement des mots-clés.
    """

    def __init__(self):
        """
        Initialise le moteur de synonymes.
        """

        dictionary_path = (
            Path(__file__).resolve().parents[1]
            / "resources"
            / "synonym_dictionary.json"
        )

        with open(
            dictionary_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.synonym_dictionary = json.load(file)

        print("SynonymEngine initialisé.")

    def get_synonyms(
        self,
        keyword: str
    ) -> list[str]:
        """
        Retourne les synonymes d'un mot-clé.

        Parameters
        ----------
        keyword : str
            Mot-clé.

        Returns
        -------
        list[str]
            Liste des synonymes.
        """

        synonyms = self.synonym_dictionary.get(
            keyword.lower(),
            []
        )

        return sorted(set(synonyms))

    def enrich_keywords(
        self,
        keywords: list[str]
    ) -> list[str]:
        """
        Enrichit une liste de mots-clés.

        Parameters
        ----------
        keywords : list[str]
            Liste des mots-clés.

        Returns
        -------
        list[str]
            Liste enrichie.
        """

        enriched_keywords = set()

        for keyword in keywords:

            enriched_keywords.add(
                keyword.lower()
            )

            enriched_keywords.update(
                self.get_synonyms(keyword)
            )

        return sorted(enriched_keywords)