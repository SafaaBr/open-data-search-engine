"""
Module de profiling des métadonnées.

Ce module est responsable de l'analyse des métadonnées
des jeux de données Kaggle afin de calculer différents
indicateurs de qualité.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

import pandas as pd
from datetime import datetime, timezone
import math



class MetadataProfiler:
    """
    Classe responsable du profiling des métadonnées.
    """

    def __init__(self):
        """
        Initialise le profiler.
        """

        print("MetadataProfiler initialisé.")
    METADATA_WEIGHTS = {
    "title": 3,
    "description": 3,
    "creator": 3,
    "license": 3,
    "owner": 2,
    "tags": 2,
    "last_updated": 2,
    "subtitle": 1,
    }

    def _is_present(self, value):
        """Vérifie si une métadonnée est renseignée."""
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() != ""
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True


    def calculate_metadata_completeness(self, metadata: dict) -> float:
        """
        Calcule le Metadata Completeness Score (MCS).

        Parameters
        ----------
        metadata : dict
            Métadonnées d'un dataset.

        Returns
        -------
        float
            Score de complétude normalisé entre 0 et 1.
        """
        total_weight = sum(self.METADATA_WEIGHTS.values())
        score = 0

        for field, weight in self.METADATA_WEIGHTS.items():
            if self._is_present(metadata.get(field)):
                score += weight

        return round(score / total_weight, 3)
    

    def calculate_freshness_score(
        self,
        last_updated: str
    ) -> float:
        """
        Calcule le Freshness Score d'un jeu de données.

        Parameters
        ----------
        last_updated : str
            Date de dernière mise à jour (format ISO 8601).

        Returns
        -------
        float
            Score de fraîcheur normalisé entre 0 et 1.
        """

        if not last_updated:
            return 0.0

        try:
            # Conversion de la date ISO 8601
            updated_date = datetime.fromisoformat(
                last_updated.replace("Z", "+00:00")
            )

            current_date = datetime.now(timezone.utc)

            # Âge du dataset en années
            age_years = (current_date - updated_date).days / 365.25

            # Demi-vie de 5 ans
            half_life = 5

            # Calcul automatique du coefficient λ
            decay = math.log(2) / half_life

            # Score exponentiel
            score = math.exp(-decay * age_years)

            return round(score, 3)

        except Exception:
            return 0.0
        

    def calculate_reusability_score(
        self,
        license_name: str,
        description: str,
        creator: str,
        tags: list
    ) -> float:
        """
        Calcule le score de réutilisabilité.

        Parameters
        ----------
        license_name : str
            Licence du jeu de données.
        description : str
            Description du jeu de données.
        creator : str
            Créateur du jeu de données.
        tags : list
            Tags du jeu de données.

        Returns
        -------
        float
            Score de réutilisabilité normalisé entre 0 et 1.
        """

        metadata = {
            "license": license_name,
            "description": description,
            "creator": creator,
            "tags": tags,
        }

        weights = {
            "license": 5,
            "description": 2,
            "creator": 2,
            "tags": 1,
        }

        score = 0

        for field, weight in weights.items():
            if self._is_present(metadata[field]):
                score += weight

        return round(score / sum(weights.values()), 3)


    def calculate_metadata_score(
        self,
        completeness: float,
        popularity: float,
        freshness: float,
        reusability: float
    ) -> float:
        """
        Calcule le Metadata Score.

        Parameters
        ----------
        completeness : float
            Metadata Completeness Score.
        popularity : float
            Popularity Score.
        freshness : float
            Freshness Score.
        reusability : float
            Reusability Score.

        Returns
        -------
        float
            Metadata Score normalisé entre 0 et 1.
        """

        score = (
            completeness +
            popularity +
            freshness +
            reusability
        ) / 4

        return round(score, 3)
    
    def profile_dataframe(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Enrichit le DataFrame avec les indicateurs
        de Metadata Profiling.
        """

        dataframe = dataframe.copy()

        dataframe["completeness_score"] = dataframe.apply(
            lambda row: self.calculate_metadata_completeness_score(
                title=row["title"],
                subtitle=row["subtitle"],
                description=row["description"],
                creator=row["creator"],
                owner=row["owner"],
                license_name=row["license_name"],
                last_updated=row["last_updated"],
                tags=row["tags"],
            ),
            axis=1,
        )

        dataframe["popularity_score"] = dataframe.apply(
            lambda row: self.calculate_popularity_score(
                downloads=row["downloads"],
                votes=row["votes"],
                views=row["views"],
            ),
            axis=1,
        )

        dataframe["freshness_score"] = dataframe.apply(
            lambda row: self.calculate_freshness_score(
                last_updated=row["last_updated"]
            ),
            axis=1,
        )

        dataframe["reusability_score"] = dataframe.apply(
            lambda row: self.calculate_reusability_score(
                license_name=row["license_name"],
                description=row["description"],
                creator=row["creator"],
                tags=row["tags"],
            ),
            axis=1,
        )

        dataframe["metadata_score"] = dataframe.apply(
            lambda row: self.calculate_metadata_score(
                completeness=row["completeness_score"],
                popularity=row["popularity_score"],
                freshness=row["freshness_score"],
                reusability=row["reusability_score"],
            ),
            axis=1,
        )

        return dataframe