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

        if language in ["en", "unknown"] or not keywords:
            return keywords

        try:
            # Regrouper les mots-clés en une seule phrase
            text = " ".join(keywords)

            # Une seule requête de traduction
            translated_text = self.translator.translate(text)

            # Retourner sous forme de liste
            return translated_text.lower().split()

        except Exception as e:
            print(f"Erreur de traduction : {e}")

            # En cas d'erreur, conserver les mots-clés originaux
        return keywords