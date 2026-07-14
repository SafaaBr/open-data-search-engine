"""
Module de téléchargement des jeux de données Kaggle.

Ce module est responsable de :

- télécharger un dataset ;
- enregistrer les fichiers localement ;
- retourner le chemin local du dataset téléchargé.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi


class DatasetDownloader:
    """
    Classe responsable du téléchargement des datasets Kaggle.
    """

    def __init__(self, api: KaggleApi):
        """
        Initialise le downloader.

        Parameters
        ----------
        api : KaggleApi
            Instance authentifiée de l'API Kaggle.
        """

        self.api = api

        self.download_path = (
            Path(__file__).resolve().parents[2]
            / "datasets"
            / "downloaded"
        )

        # Création automatique du dossier s'il n'existe pas
        self.download_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def dataset_exists(
        self,
        dataset_ref: str
    ) -> bool:
        """
        Vérifie si un dataset est déjà téléchargé.

        Parameters
        ----------
        dataset_ref : str
            Référence du dataset Kaggle.

        Returns
        -------
        bool
            True si le dataset existe déjà localement.
        """

        return self.get_dataset_path(dataset_ref).exists()

    def download_dataset(
        self,
        dataset_ref: str
    ) -> Path:
        """
        Télécharge un dataset Kaggle.

        Parameters
        ----------
        dataset_ref : str
            Référence du dataset Kaggle.

        Returns
        -------
        pathlib.Path
            Chemin du dossier local contenant le dataset téléchargé.
        """
        if self.api is None:
            raise RuntimeError(
                "Aucune connexion à l'API Kaggle n'est disponible."
            )
        

        dataset_path = self.get_dataset_path(dataset_ref)

        if self.dataset_exists(dataset_ref):

            print(f"Le dataset '{dataset_ref}' est déjà présent.")
            
            return dataset_path

        print(f"Téléchargement du dataset '{dataset_ref}'...")

        self.api.dataset_download_files(
            dataset=dataset_ref,
            path=dataset_path,
            unzip=True
        )

        print(f"Dataset '{dataset_ref}' téléchargé avec succès.")
        
        return dataset_path

    def get_dataset_path(
        self,
        dataset_ref: str
    ) -> Path:
        """
        Retourne le chemin local d'un dataset.

        Parameters
        ----------
        dataset_ref : str
            Référence du dataset Kaggle.

        Returns
        -------
        pathlib.Path
            Chemin local du dataset.
        """

        dataset_name = dataset_ref.split("/")[-1]

        dataset_path = self.download_path / dataset_name

        return dataset_path