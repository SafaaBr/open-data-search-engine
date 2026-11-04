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
import pandas as pd

# Remarque : la bibliothèque Kaggle est importée dans authenticate(),
# et non ici. Selon les versions, « import kaggle » tente de
# s'authentifier immédiatement ; il faut donc d'abord indiquer
# où se trouvent les identifiants.


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

    def _configure_credentials(self) -> str:
        """
        Indique à la bibliothèque Kaggle où trouver les identifiants.

        Les sources sont essayées dans cet ordre :

        1. le fichier config/kaggle.json du projet (usage local) ;
        2. les variables d'environnement KAGGLE_USERNAME et KAGGLE_KEY,
           ou KAGGLE_API_TOKEN (nouveau format de token Kaggle) ;
        3. les Secrets Streamlit, section [kaggle] (déploiement cloud) ;
        4. sinon, le fichier ~/.kaggle/kaggle.json lu par Kaggle lui-même.

        Returns
        -------
        str
            Source des identifiants utilisée (pour l'affichage).
        """

        # 1. Fichier du projet
        if self.config_path.exists():
            os.environ["KAGGLE_CONFIG_DIR"] = str(self.config_path.parent)
            return "config/kaggle.json"

        # 2. Variables d'environnement
        if os.environ.get("KAGGLE_API_TOKEN") or (
            os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY")
        ):
            return "variables d'environnement"

        # 3. Secrets Streamlit (import local : Streamlit n'est pas
        #    nécessaire pour les scripts lancés hors de l'application)
        try:
            import streamlit as st

            kaggle_secrets = st.secrets["kaggle"]
            os.environ["KAGGLE_USERNAME"] = kaggle_secrets["username"]
            os.environ["KAGGLE_KEY"] = kaggle_secrets["key"]
            return "Secrets Streamlit"
        except Exception:
            pass

        # 4. Emplacement par défaut de Kaggle
        return "~/.kaggle/kaggle.json"

    def authenticate(self) -> bool:
        """
        Authentifie l'application auprès de l'API Kaggle.

        Returns
        -------
        bool
            True si l'authentification a réussi.
        """

        source = self._configure_credentials()

        try:
            from kaggle.api.kaggle_api_extended import KaggleApi

            # Création de l'objet API, puis authentification
            self.api = KaggleApi()
            self.api.authenticate()
        except (Exception, SystemExit) as error:
            # Certaines versions de Kaggle appellent sys.exit() en cas
            # d'échec : on intercepte aussi SystemExit pour afficher
            # un message clair au lieu de fermer le programme.
            self.api = None
            raise RuntimeError(
                "Authentification Kaggle impossible. Vérifiez vos "
                "identifiants : fichier config/kaggle.json du projet, ou "
                "variable d'environnement KAGGLE_API_TOKEN (voir le README)."
            ) from error

        print(f"Connexion à Kaggle réussie ({source}).")

        return True
    

    def search(self, query: str, limit: int = 10) -> list:
        """
        Recherche des jeux de données sur Kaggle avec pagination.
        """

        if self.api is None:
            raise RuntimeError(
                "L'API Kaggle n'est pas authentifiée. "
                "Appelez authenticate() avant search()."
            )

        all_datasets = []
        page = 1

        while len(all_datasets) < limit:

            datasets = self.api.dataset_list(
                search=query,
                page=page
            )

            if not datasets:
                break

            all_datasets.extend(datasets)

            # Si Kaggle retourne moins de 20 résultats,
            # cela signifie probablement qu'il n'y en a plus
            if len(datasets) < 20:
                break

            page += 1

        return all_datasets[:limit]
    
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

        # Selon la version de la bibliothèque Kaggle, les attributs
        # sont nommés en camelCase (downloadCount) ou en snake_case
        # (download_count) : on accepte les deux.
        def attr(camel: str, snake: str, default=None):
            return getattr(dataset, camel, getattr(dataset, snake, default))

        total_bytes = attr("totalBytes", "total_bytes", 0) or 0
        last_updated = attr("lastUpdated", "last_updated")

        metadata = {

            # Identification
            "id": getattr(dataset, "id", None),
            "ref": getattr(dataset, "ref", None),
            "title": getattr(dataset, "title", ""),
            "subtitle": getattr(dataset, "subtitle", ""),

            # Description
            "description": getattr(dataset, "description", ""),

            # Auteur
            "owner": attr("ownerName", "owner_name", ""),
            "creator": attr("creatorName", "creator_name", ""),

            # Popularité
            "downloads": attr("downloadCount", "download_count", 0),
            "votes": attr("voteCount", "vote_count", 0),
            "views": attr("viewCount", "view_count", 0),

            # Taille
            "size_bytes": total_bytes,
            "size_mb": round(total_bytes / (1024 * 1024), 2),

            # Informations générales
            "license": attr("licenseName", "license_name", ""),
            "last_updated": (
                last_updated.strftime("%Y-%m-%d") if last_updated else None
            ),
            "url": getattr(dataset, "url", ""),

            # Classification
            "tags": ", ".join(tag.name for tag in getattr(dataset, "tags", [])),
            "topic_count": attr("topicCount", "topic_count", 0),

            # Qualité
            "usability_rating": attr("usabilityRating", "usability_rating"),

            # Statut
            "is_private": attr("isPrivate", "is_private", False),
            "is_featured": attr("isFeatured", "is_featured", False),
        }

        return metadata
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
    