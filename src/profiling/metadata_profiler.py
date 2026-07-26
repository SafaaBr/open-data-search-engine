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

        score = 0
        total_weight = sum(self.METADATA_WEIGHTS.values())

        # Title
        title = metadata.get("title", "")
        if self._is_present(title):
            if len(title) >= 20:
                score += self.METADATA_WEIGHTS["title"]
            elif len(title) >= 10:
                score += self.METADATA_WEIGHTS["title"] * 0.7
            else:
                score += self.METADATA_WEIGHTS["title"] * 0.4

        # Description
        description = metadata.get("description", "")
        if self._is_present(description):
            if len(description) >= 500:
                score += self.METADATA_WEIGHTS["description"]
            elif len(description) >= 150:
                score += self.METADATA_WEIGHTS["description"] * 0.7
            else:
                score += self.METADATA_WEIGHTS["description"] * 0.4

        # Tags
        tags = metadata.get("tags", [])
        if self._is_present(tags):
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]

            if len(tags) >= 5:
                score += self.METADATA_WEIGHTS["tags"]
            elif len(tags) >= 2:
                score += self.METADATA_WEIGHTS["tags"] * 0.7
            else:
                score += self.METADATA_WEIGHTS["tags"] * 0.4

        # Les autres champs restent binaires
        for field in ["creator", "owner", "license", "last_updated", "subtitle"]:
            if self._is_present(metadata.get(field)):
                score += self.METADATA_WEIGHTS[field]

        return round(score / total_weight, 3)
    
    def calculate_freshness_score(
        self,
        last_updated: str
    ) -> float:
        """
        Calcule le Freshness Score d'un jeu de données.
        """

        if not last_updated:
            return 0.0

        try:
            # Conversion de la date
            updated_date = datetime.fromisoformat(
                last_updated.replace("Z", "+00:00")
            )

            # Si la date n'a pas de fuseau horaire, on la considère en UTC
            if updated_date.tzinfo is None:
                updated_date = updated_date.replace(tzinfo=timezone.utc)

            current_date = datetime.now(timezone.utc)

            age_years = (current_date - updated_date).days / 365.25

            half_life = 5
            decay = math.log(2) / half_life

            score = math.exp(-decay * age_years)

            return round(score, 3)

        except Exception as e:
            print(f"Erreur Freshness : {e}")
            return 0.0
            
    def _license_score(self, license_name: str) -> float:

        if not license_name:
            return 0.2

        license_name = license_name.lower()

        if "cc0" in license_name or "public domain" in license_name:
            return 1.0

        if "mit" in license_name:
            return 1.0

        if "apache" in license_name:
            return 1.0

        if "bsd" in license_name:
            return 1.0

        if "cc by-sa" in license_name:
            return 0.8

        if "cc by" in license_name:
            return 0.8

        if "other" in license_name:
            return 0.5

        return 0.5
    

    def calculate_reusability_score(
        self,
        license: str,
        description: str,
        creator: str,
        tags: list
    ) -> float:

        weights = {
            "license": 5,
            "description": 2,
            "creator": 2,
            "tags": 1,
        }

        score = 0

        # Licence (qualité de la licence)
        score += self._license_score(license) * weights["license"]

        # Description
        if self._is_present(description):
            score += weights["description"]

        # Créateur
        if self._is_present(creator):
            score += weights["creator"]

        # Tags
        if self._is_present(tags):
            score += weights["tags"]

        return round(score / sum(weights.values()), 3)

    def calculate_metadata_score(
        self,
        completeness: float,
        freshness: float,
        reusability: float
    ) -> float:
        """
        Calcule le Metadata Score global.

        Parameters
        ----------
        completeness : float
            Score de complétude.
        freshness : float
            Score de fraîcheur.
        reusability : float
            Score de réutilisabilité.

        Returns
        -------
        float
            Metadata Score normalisé entre 0 et 1.
        """

        score = (
            0.40 * completeness +
            0.30 * freshness +
            0.30 * reusability
        )

        return round(score, 3)
    
    def profile_dataframe(
        self,
        dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Enrichit un DataFrame avec les scores de qualité des métadonnées.
        """

        dataframe = dataframe.copy()



        dataframe["completeness_score"] = dataframe.apply(
            lambda row: self.calculate_metadata_completeness({
                "title": row["title"],
                "subtitle": row["subtitle"],
                "description": row["description"],
                "creator": row["creator"],
                "owner": row["owner"],
                "license": row["license"],
                "last_updated": row["last_updated"],
                "tags": row["tags"],
            }),
            axis=1
        )


        dataframe["freshness_score"] = dataframe["last_updated"].apply(
            self.calculate_freshness_score
        )

        dataframe["reusability_score"] = dataframe.apply(
            lambda row: self.calculate_reusability_score(
                license=row["license"],
                description=row["description"],
                creator=row["creator"],
                tags=row["tags"],
            ),
            axis=1
        )

        dataframe["metadata_score"] = dataframe.apply(
            lambda row: self.calculate_metadata_score(
                completeness=row["completeness_score"],
                freshness=row["freshness_score"],
                reusability=row["reusability_score"],
            ),
            axis=1
        )

        return dataframe