"""
Module d'extraction des métadonnées depuis Kaggle.

Ce module est responsable de toutes les interactions avec l'API Kaggle.
Il permet :

- d'établir une connexion avec l'API ;
- de rechercher des jeux de données ;
- d'extraire leurs métadonnées.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi


class KaggleExtractor:
    """
    Classe responsable des interactions avec l'API Kaggle.
    """

    def __init__(self):
        """
        Initialise l'extracteur Kaggle.
        """

        # Objet API Kaggle (sera créé lors de l'authentification)
        self.api = None

        # Chemin vers le fichier kaggle.json
        self.config_path = (
            Path(__file__).resolve().parents[2]
            / "config"
            / "kaggle.json"
        )

    def authenticate(self):
        """
        Authentifie l'application auprès de l'API Kaggle.

        Returns
        -------
        bool
            True si l'authentification a réussi.
        """

        # Vérifier que le fichier existe
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Fichier introuvable : {self.config_path}"
            )

        # Indiquer à la bibliothèque Kaggle où se trouve le fichier
        import os

        os.environ["KAGGLE_CONFIG_DIR"] = str(self.config_path.parent)

        # Création de l'objet API
        self.api = KaggleApi()

        # Authentification
        self.api.authenticate()

        print(" Connexion à Kaggle réussie.")

        return True