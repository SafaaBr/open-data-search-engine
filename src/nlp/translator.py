"""
Module de traduction des mots-clés.

Ce module est responsable de :

- traduire les mots-clés vers l'anglais ;
- conserver les mots déjà en anglais.

Deux moteurs de traduction sont disponibles :

- "local"  : modèle Helsinki-NLP/opus-mt-fr-en (MarianMT), exécuté sur
             la machine. Il ne dépend d'aucun service en ligne et donne
             toujours la même traduction, ce qui rend les résultats
             reproductibles. C'est le moteur par défaut.
- "google" : Google Translate via deep-translator. Ce service web non
             officiel peut refuser les requêtes (« too many requests »).

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import time


class Translator:
    """
    Classe responsable de la traduction des mots-clés.
    """

    LOCAL_MODEL_NAME = "Helsinki-NLP/opus-mt-fr-en"

    def __init__(self, backend: str = "local"):
        """
        Initialise le traducteur.

        Parameters
        ----------
        backend : str
            Moteur de traduction : "local" (par défaut) ou "google".
        """

        if backend not in ["local", "google"]:
            raise ValueError(
                f"Moteur de traduction inconnu : {backend} "
                "(valeurs possibles : 'local', 'google')"
            )

        self.backend = backend

        # Le modèle local est chargé à la première traduction, pour ne
        # pas ralentir le démarrage de l'application.
        self.tokenizer = None
        self.model = None

        # Client Google Translate (créé à la première utilisation)
        self.google_translator = None

        # Cache des traductions déjà obtenues : une même requête
        # n'est traduite qu'une fois.
        self.cache = {}

        # Nombre d'essais si Google Translate refuse temporairement
        # la requête (« too many requests »).
        self.max_attempts = 3

        print(f"Translator initialisé (moteur : {self.backend}).")

    # ------------------------------------------------------------
    # Moteur local (MarianMT)
    # ------------------------------------------------------------

    def _load_local_model(self):
        """
        Charge le modèle de traduction local.

        Le modèle (environ 300 Mo) est téléchargé depuis Hugging Face
        lors de la première utilisation, puis réutilisé depuis le cache.
        """

        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        print(f"Chargement du modèle de traduction {self.LOCAL_MODEL_NAME}...")

        self.tokenizer = AutoTokenizer.from_pretrained(self.LOCAL_MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.LOCAL_MODEL_NAME
        )

        # Mode évaluation : pas d'aléa (dropout désactivé)
        self.model.eval()

        print("Modèle de traduction chargé.")

    def _translate_local(self, text: str) -> str:
        """
        Traduit un texte du français vers l'anglais avec le modèle local.
        """

        import torch

        if self.model is None:
            self._load_local_model()

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)

        # Décodage glouton (num_beams=1, pas d'échantillonnage) :
        # la même entrée donne toujours la même traduction.
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                num_beams=1,
                do_sample=False,
                max_new_tokens=64
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    # ------------------------------------------------------------
    # Moteur Google Translate
    # ------------------------------------------------------------

    def _translate_google(self, text: str) -> str:
        """
        Traduit un texte avec Google Translate, avec plusieurs essais.
        """

        from deep_translator import GoogleTranslator

        if self.google_translator is None:
            self.google_translator = GoogleTranslator(
                source="auto",
                target="en"
            )

        for attempt in range(1, self.max_attempts + 1):
            try:
                return self.google_translator.translate(text)

            except Exception as e:
                print(
                    f"Erreur de traduction (essai {attempt}/"
                    f"{self.max_attempts}) : {e}"
                )

                # Attendre un peu avant de réessayer (1 s, puis 2 s)
                if attempt < self.max_attempts:
                    time.sleep(attempt)
                else:
                    raise

    # ------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------

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

        try:
            if self.backend == "local":
                translated_text = self._translate_local(text)
            else:
                translated_text = self._translate_google(text)

        except Exception as e:
            print(f"Traduction impossible ({self.backend}) : {e}")

            # En cas d'échec, conserver les mots-clés originaux
            return keywords

        # Retourner sous forme de liste, sans ponctuation
        translated_keywords = [
            word.strip(".,;:!?\"'()").lower()
            for word in translated_text.split()
        ]
        translated_keywords = [word for word in translated_keywords if word]

        self.cache[text] = translated_keywords

        return translated_keywords
