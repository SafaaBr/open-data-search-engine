"""
Module de gestion de la base de données SQLite.

Ce module est responsable de :

- créer la base de données ;
- ouvrir la connexion ;
- créer les tables ;
- stocker les métadonnées des datasets ;
- mettre à jour les métadonnées ;
- récupérer les datasets pour la recherche ;
- gérer les embeddings des datasets.

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
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

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

                ref TEXT UNIQUE,
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
                theme TEXT,
                topic_count INTEGER,

                usability_rating REAL,

                is_private BOOLEAN,
                is_featured BOOLEAN

            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (

                dataset_ref TEXT PRIMARY KEY,

                embedding BLOB,

                FOREIGN KEY(dataset_ref)
                REFERENCES datasets(ref)

            )
        """)

        self.connection.commit()

        print("Tables 'datasets' et 'embeddings' créées avec succès.")

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
        cursor = self.connection.cursor()

        cursor.execute("DELETE FROM datasets")

        self.connection.commit()
                
        dataframe.to_sql(
            name="datasets",
            con=self.connection,
            if_exists="append", 
            index=False
        )

        self.connection.commit()

        print("Les métadonnées ont été enregistrées avec succès.")
    
    def get_all_datasets(self) -> pd.DataFrame:
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
    
    def get_dataset_by_ref(self, dataset_ref: str) -> pd.DataFrame:
        """
        Retourne un dataset à partir de son identifiant Kaggle.
        """

        query = """
            SELECT *
            FROM datasets
            WHERE ref = ?
        """

        return pd.read_sql(
            query,
            self.connection,
            params=(dataset_ref,)
        )
    
    def save_embeddings(self, dataframe: pd.DataFrame):
        """
        Enregistre les embeddings des datasets.
        """
        if self.connection is None:
            raise RuntimeError(
                "La connexion à la base de données n'est pas ouverte."
            )
        cursor = self.connection.cursor()

        cursor.execute("DELETE FROM embeddings")

        self.connection.commit()

        dataframe.to_sql(
            "embeddings",
            self.connection,
            if_exists="append",
            index=False
        )

        self.connection.commit()

    def load_embeddings(self) -> pd.DataFrame:
        """
        Charge les embeddings des datasets.
        """
        if self.connection is None:
            raise RuntimeError(
                "La connexion à la base de données n'est pas ouverte."
            )

        query = "SELECT * FROM embeddings"

        return pd.read_sql(query, self.connection)
    
    
    def load_search_index(self) -> pd.DataFrame:
        """
        Charge les datasets avec leurs embeddings.

        Returns
        -------
        pandas.DataFrame
            DataFrame contenant les métadonnées
            ainsi que les embeddings associés.
        """

        if self.connection is None:
            raise RuntimeError(
                "La connexion à la base de données n'est pas ouverte."
            )

        query = """
            SELECT
                d.*,
                e.embedding
            FROM datasets d
            INNER JOIN embeddings e
                ON d.ref = e.dataset_ref
        """

        return pd.read_sql(
            query,
            self.connection
        )


    def close(self):
        """
        Ferme la connexion à la base de données.
        """

        if self.connection:

            self.connection.close()
            self.connection = None

            print("Connexion SQLite fermée.")
    
    