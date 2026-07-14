"""
Module de traduction des mots-clés.

Ce module est responsable de :

- traduire les mots-clés vers l'anglais ;
- conserver les mots déjà en anglais.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

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

        if language in ["en", "unknown"]:
            return keywords

        translated_keywords = []

        for keyword in keywords:

            translated_keyword = self.translator.translate(
                keyword
            )

            translated_keywords.append(
                translated_keyword.lower()
            )

        return translated_keywords