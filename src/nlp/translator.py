"""
Module de traduction des mots-clés.

Ce module est responsable de :

- traduire les mots-clés vers l'anglais ;
- conserver les mots déjà en anglais.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import time

from deep_translator import GoogleTranslator


class Translator:
    """
    Classe responsable de la traduction des mots-clés.
    """

    def __init__(self):
        """
        Initialise le traducteur.
        """

        self.translator = GoogleTranslator(
            source="auto",
            target="en"
        )

        # Cache des traductions déjà obtenues : une même requête
        # n'est envoyée qu'une fois à Google Translate.
        self.cache = {}

        # Nombre d'essais si Google Translate refuse temporairement
        # la requête (« too many requests »).
        self.max_attempts = 3

        print("Translator initialisé.")

    def translate_keywords(
        self,
        keywords: list[str],
        language: str
    ) -> list[str]:
        """
        Traduit une liste de mots-clés vers l'anglais.

        Parameters
        ----------
        keywords : list[str]
            Liste des mots-clés.

        language : str
            Langue détectée.

        Returns
        -------
        list[str]
            Liste des mots-clés traduits.
        """

        if language in ["en", "unknown"] or not keywords:
            return keywords

        # Regrouper les mots-clés en une seule phrase
        text = " ".join(keywords)

        if text in self.cache:
            return self.cache[text]

        for attempt in range(1, self.max_attempts + 1):
            try:
                # Une seule requête de traduction
                translated_text = self.translator.translate(text)

                # Retourner sous forme de liste
                translated_keywords = translated_text.lower().split()
                self.cache[text] = translated_keywords
                return translated_keywords

            except Exception as e:
                print(
                    f"Erreur de traduction (essai {attempt}/"
                    f"{self.max_attempts}) : {e}"
                )

                # Attendre un peu avant de réessayer (1 s, puis 2 s)
                if attempt < self.max_attempts:
                    time.sleep(attempt)

        # En cas d'échec, conserver les mots-clés originaux
        return keywords
