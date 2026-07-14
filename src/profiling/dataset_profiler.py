"""
Module de profiling des datasets.

Ce module est responsable de l'analyse du contenu des
datasets téléchargés afin de produire différents
indicateurs de qualité.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

from pathlib import Path
import pandas as pd


class DatasetProfiler:
    """
    Classe responsable du profiling des datasets.
    """

    def __init__(self):
        """
        Initialise le profiler.
        """

        print("DatasetProfiler initialisé.")

        
    def list_dataset_files(
        self,
        dataset_folder: Path
    ) -> list[Path]:
        """
        Liste les fichiers d'un dataset.

        Parameters
        ----------
        dataset_folder : pathlib.Path
            Dossier contenant le dataset.

        Returns
        -------
        list[pathlib.Path]
            Liste des fichiers du dataset.
        """

        return [
            file
            for file in dataset_folder.iterdir()
            if file.is_file()
        ]

    def load_dataset(
        self,
        file_path: Path
    ) -> pd.DataFrame:
        """
        Charge un dataset.

        Parameters
        ----------
        file_path : pathlib.Path
            Chemin du fichier à analyser.

        Returns
        -------
        pandas.DataFrame
            Dataset chargé.
        """

        extension = file_path.suffix.lower()

        if extension == ".csv":
            return pd.read_csv(file_path)

        elif extension in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)

        elif extension == ".json":
            return pd.read_json(file_path)

        elif extension == ".parquet":
            return pd.read_parquet(file_path)
        
        elif extension == ".tsv":
            return pd.read_csv(file_path, sep="\t")

        else:
            raise ValueError(
                f"Format non supporté : {extension}"
            )

    def count_rows(
        self,
        dataframe: pd.DataFrame
    ) -> int:
        """
        Calcule le nombre de lignes.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Dataset chargé.

        Returns
        -------
        int
            Nombre de lignes.
        """

        return dataframe.shape[0]

    def count_columns(
        self,
        dataframe: pd.DataFrame
    ) -> int:
        """
        Calcule le nombre de colonnes.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Dataset chargé.

        Returns
        -------
        int
            Nombre de colonnes.
        """

        return dataframe.shape[1]

    def detect_column_types(
        self,
        dataframe: pd.DataFrame
    ) -> dict:
        """
        Détecte les types de colonnes.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Dataset chargé.

        Returns
        -------
        dict
            Répartition des types de données.
        """

        return dataframe.dtypes.astype(str).to_dict()

    def count_missing_values(
        self,
        dataframe: pd.DataFrame
    ) -> dict:
        """
        Calcule les valeurs manquantes.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Dataset chargé.

        Returns
        -------
        dict
            Statistiques sur les valeurs manquantes.
        """

        missing = dataframe.isnull().sum()

        missing_percentage = (
            dataframe.isnull().mean() * 100
        ).round(2)

        return {
            "missing_values_per_column": missing.to_dict(),
            "missing_percentage_per_column": missing_percentage.to_dict(),
            "total_missing": int(missing.sum()),
            "missing_percentage": round(
                (missing.sum() / dataframe.size) * 100,
                2
            )
        }

    def count_duplicates(
        self,
        dataframe: pd.DataFrame
    ) -> int:
        """
        Calcule le nombre de doublons.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Dataset chargé.

        Returns
        -------
        int
            Nombre de lignes dupliquées.
        """

        return int(dataframe.duplicated().sum())

    def calculate_memory_usage(
        self,
        dataframe: pd.DataFrame
    ) -> float:
        """
        Calcule la mémoire utilisée par le dataset.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Dataset chargé.

        Returns
        -------
        float
            Taille mémoire en Mo.
        """

        memory = dataframe.memory_usage(deep=True).sum()

        return round(memory / (1024 * 1024), 2)

    def profile_dataset(
        self,
        dataframe: pd.DataFrame
    ) -> dict:
        """
        Produit un rapport complet sur le dataset.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Dataset chargé.

        Returns
        -------
        dict
            Rapport de profiling.
        """

        report = {
            "rows": self.count_rows(dataframe),
            "columns": self.count_columns(dataframe),
            "column_types": self.detect_column_types(dataframe),
            "missing_values": self.count_missing_values(dataframe),
            "duplicates": self.count_duplicates(dataframe),
            "memory_mb": self.calculate_memory_usage(dataframe)
        }

        return report