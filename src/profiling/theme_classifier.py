"""
Module de classification des datasets par thème.

Ce module attribue automatiquement un thème
à un dataset à partir de ses métadonnées.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import json
from pathlib import Path


class ThemeClassifier:
    """
    Classe responsable de l'attribution
    d'un thème aux datasets.
    """

    def __init__(self):
        """
        Charge le dictionnaire des thèmes.
        """

        path = (
            Path(__file__).parent.parent
            / "resources"
            / "themes.json"
        )

        with open(path, "r", encoding="utf-8") as file:
            self.themes = json.load(file)

        print("ThemeClassifier initialisé.")

    def classify(
        self,
        title: str,
        tags: list[str],
        description: str
    ) -> str:
        """
        Détermine le thème d'un dataset.

        Parameters
        ----------
        title : str
            Titre du dataset.

        tags : list[str]
            Liste des tags.

        description : str
            Description du dataset.

        Returns
        -------
        str
            Thème attribué.
        """

        title = (title or "").lower()
        description = (description or "").lower()

        tags = [
            tag.lower().strip()
            for tag in tags
        ]

        scores = {}

        for theme, keywords in self.themes.items():

            score = 0

            for keyword in keywords:

                keyword = keyword.lower()

                # Tags (2 points)
                if any(keyword in tag or tag in keyword for tag in tags):
                    score += 2

                # Titre (2 points)
                if keyword in title:
                    score += 2

                # Description (1 point)
                if keyword in description:
                    score += 1

            scores[theme] = score

        best_theme = max(scores, key=scores.get)

        if scores[best_theme] == 0:
            return "Autre"

        return best_theme