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
import os
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi
import pandas as pd
import streamlit as st

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

    def authenticate(self) -> bool:
        """
        Authentifie l'application auprès de l'API Kaggle.
        Utilise les Secrets Streamlit en environnement Cloud.
        """



        # Récupération des identifiants depuis les Secrets Streamlit
        username = st.secrets["kaggle"]["username"]
        key = st.secrets["kaggle"]["key"]

        # Création temporaire du fichier de configuration Kaggle
        config_dir = Path("/tmp/kaggle")
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "kaggle.json"

        config_file.write_text(
            f'{{"username": "{username}", "key": "{key}"}}'
        )

        # Indiquer à Kaggle où trouver le fichier
        os.environ["KAGGLE_CONFIG_DIR"] = str(config_dir)

        # Création de l'objet API
        self.api = KaggleApi()

        # Authentification
        self.api.authenticate()

        print("Connexion à Kaggle réussie.")

        return True
    

    def search(self, query: str, limit: int = 10) -> list:
    
        """Recherche des jeux de données sur Kaggle.

        Parameters
        ----------
        query : str
            Mot-clé de recherche.
        limit : int
            Nombre maximal de résultats.

        Returns
        -------
        list
                Liste des datasets retournés par l'API Kaggle.
        """

        
        if self.api is None:
            raise RuntimeError(
                "L'API Kaggle n'est pas authentifiée. "
                "Appelez authenticate() avant search()."
            )

        datasets = self.api.dataset_list(
            search=query
            #page_size=limit

        )

        return datasets[:limit]
    
    
    def get_metadata(self, dataset) -> dict:
        """
        Extrait les métadonnées principales d'un dataset Kaggle.

        Parameters
        ----------
        dataset : ApiDataset
            Objet retourné par l'API Kaggle.

        Returns
        -------
        dict
            Métadonnées du dataset.
        """
        last_updated = getattr(
            dataset,
            "last_updated",
            getattr(dataset, "lastUpdated", None)
        )

        if last_updated:
            last_updated = last_updated.strftime("%Y-%m-%d")
        metadata = {

            # Identification
            "id": getattr(dataset, "id", None),
            "ref": getattr(dataset, "ref", None),
            "title": getattr(dataset, "title", ""),
            "subtitle": getattr(dataset, "subtitle", ""),

            # Description
            "description": getattr(dataset, "description", ""),

            # Auteur
            "owner": getattr(dataset, "owner_name",
                            getattr(dataset, "ownerName", "")),

            "creator": getattr(dataset, "creator_name",
                            getattr(dataset, "creatorName", "")),

            # Popularité
            "downloads": getattr(dataset, "download_count",
                                getattr(dataset, "downloadCount", 0)),

            "votes": getattr(dataset, "vote_count",
                            getattr(dataset, "voteCount", 0)),

            "views": getattr(dataset, "view_count",
                            getattr(dataset, "viewCount", 0)),

            # Taille
            "size_bytes": getattr(dataset, "total_bytes",
                                getattr(dataset, "totalBytes", 0)),

            "size_mb": round(
                getattr(dataset, "total_bytes",
                        getattr(dataset, "totalBytes", 0)) / (1024 * 1024),
                2
            ),

            # Informations générales
            "license": getattr(dataset, "license_name",
                            getattr(dataset, "licenseName", "")),

            "url": getattr(dataset, "url", ""),

            "last_updated": last_updated,

            # Classification
            "tags": ", ".join(tag.name for tag in getattr(dataset, "tags", [])),

            "topic_count": getattr(dataset, "topic_count",
                                getattr(dataset, "topicCount", 0)),

            # Qualité
            "usability_rating": getattr(dataset, "usability_rating",
                                        getattr(dataset, "usabilityRating", None)),

            # Statut
            "is_private": getattr(dataset, "is_private",
                                getattr(dataset, "isPrivate", False)),

            "is_featured": getattr(dataset, "is_featured",
                                getattr(dataset, "isFeatured", False))
        }
        return metadata

        #     # Identification
        #     "id": dataset.id,
        #     "ref": dataset.ref,
        #     "title": dataset.title,
        #     "subtitle": dataset.subtitle,

        #     # Description
        #     "description": dataset.description,

        #     # Auteur
        #     "owner": dataset.owner_name,
        #     "creator": dataset.creator_name,

        #     # Popularité
        #     "downloads": dataset.download_count,
        #     "votes": dataset.vote_count,
        #     "views": dataset.view_count,

        #     # Taille
        #     "size_bytes": dataset.total_bytes,
        #     "size_mb": round(dataset.total_bytes / (1024 * 1024), 2),

        #     # Informations générales
        #     "license": dataset.license_name,
        #     "last_updated": dataset.last_updated.strftime("%Y-%m-%d"),
        #     "url": dataset.url,

        #     # Classification
        #     "tags": ", ".join(tag.name for tag in dataset.tags),
        #     "topic_count": dataset.topic_count,

        #     # Qualité
        #     "usability_rating": dataset.usability_rating,

        #     # Statut
        #     "is_private": dataset.is_private,
        #     "is_featured": dataset.is_featured,
        # }

        # return metadata
    def search_to_dataframe(self, query: str, limit: int = 100) -> pd.DataFrame:
        """
        Recherche des jeux de données sur Kaggle et retourne leurs
        métadonnées sous forme de DataFrame.

        Parameters
        ----------
        query : str
            Mot-clé de recherche.

        limit : int
            Nombre maximal de résultats.

        Returns
        -------
        pandas.DataFrame
            DataFrame contenant les métadonnées des datasets.
        """

        # Recherche des datasets
        datasets = self.search(query, limit)

        # Liste qui contiendra les métadonnées
        metadata_list = []

        # Extraction des métadonnées de chaque dataset
        for dataset in datasets:
            metadata = self.get_metadata(dataset)
            metadata_list.append(metadata)

        # Conversion en DataFrame
        df = pd.DataFrame(metadata_list)

        return df
    