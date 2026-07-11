"""
Module de gestion de la base de données SQLite.

Ce module est responsable de :

- créer la base de données ;
- ouvrir la connexion ;
- créer les tables ;
- enregistrer les métadonnées ;
- lire les données.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

from pathlib import Path
import sqlite3
import pandas as pd


class DatabaseManager:
    """
    Classe responsable de la gestion de la base SQLite.
    """
    def __init__(self):
        """
        Initialise le gestionnaire de base de données.
        """

        self.connection = None

        self.database_path = (
            Path(__file__).resolve().parents[2]
            / "database"
            / "datasets.db"
            )
    
    def connect(self):
        """
        Ouvre une connexion à la base SQLite.
        """

        self.connection = sqlite3.connect(self.database_path)

        print("Connexion à SQLite réussie.")

    def create_tables(self):
        """
        Crée la table des métadonnées si elle n'existe pas.
        """

        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (

                id INTEGER PRIMARY KEY,

                ref TEXT,
                title TEXT,
                subtitle TEXT,
                description TEXT,

                owner TEXT,
                creator TEXT,

                downloads INTEGER,
                votes INTEGER,
                views INTEGER,

                size_bytes INTEGER,
                size_mb REAL,

                license TEXT,
                last_updated TEXT,
                url TEXT,

                tags TEXT,
                topic_count INTEGER,

                usability_rating REAL,

                is_private BOOLEAN,
                is_featured BOOLEAN

            )
        """)

        self.connection.commit()

        print("Table 'datasets' créée avec succès.")

    def save_dataframe(self, dataframe: pd.DataFrame):
        """
        Enregistre un DataFrame dans la table 'datasets'.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            DataFrame contenant les métadonnées des datasets.
        """

        if self.connection is None:
            raise RuntimeError(
                "La connexion à la base de données n'est pas ouverte."
            )

        dataframe.to_sql(
            name="datasets",
            con=self.connection,
            if_exists="replace", # si je veux garder l'historique je mets "append" a la place de replace 
            index=False
        )

        self.connection.commit()

        print("Les métadonnées ont été enregistrées avec succès.")
    
    def load_dataframe(self) -> pd.DataFrame:
        """
        Charge la table 'datasets' sous forme de DataFrame.

        Returns
        -------
        pandas.DataFrame
            Contenu de la table datasets.
        """

        if self.connection is None:
            raise RuntimeError(
                "La connexion à la base de données n'est pas ouverte."
            )

        query = "SELECT * FROM datasets"

        return pd.read_sql(query, self.connection)
    
    
    def close(self):
        """
        Ferme la connexion à la base de données.
        """

        if self.connection:

            self.connection.close()

            print("Connexion SQLite fermée.")
    
    