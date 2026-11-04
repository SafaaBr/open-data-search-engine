"""
Module de génération des embeddings.

Ce module est responsable de :

- charger le modèle SentenceTransformer ;
- générer les embeddings des requêtes utilisateur ;
- générer les embeddings des métadonnées des datasets ;
- calculer la similarité sémantique entre une requête et les datasets.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class EmbeddingEngine:
    """
    Classe responsable de la génération des embeddings.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialise le modèle SentenceTransformer.

        Parameters
        ----------
        model_name : str
            Nom du modèle SentenceTransformer.
        """

        self.model = SentenceTransformer(model_name)

        print("EmbeddingEngine initialisé.")

    def prepare_query(
        self,
        keywords: list[str]
    ) -> str:
        """
        Concatène les mots-clés enrichis en une seule chaîne.

        Parameters
        ----------
        keywords : list[str]
            Liste des mots-clés enrichis.

        Returns
        -------
        str
            Texte prêt à être vectorisé.
        """

        return " ".join(keywords) if keywords else ""
    
    def prepare_dataset(
        self,
        title: str,
        description: str,
        tags: list[str],
        subtitle: str = ""
    ) -> str:
        """
        Prépare le texte d'un dataset avant la génération
        de son embedding.

        Le texte est construit dans cet ordre : titre, sous-titre,
        tags, puis description. Le modèle all-MiniLM-L6-v2 ne lit que
        les 256 premiers tokens environ : la description, souvent
        longue, est placée en dernier pour que ce soit elle qui soit
        coupée, et non le titre ou les tags.

        Parameters
        ----------
        title : str
            Titre du dataset.

        description : str
            Description du dataset.

        tags : list[str]
            Liste des tags associés au dataset.

        subtitle : str, optional
            Sous-titre du dataset.

        Returns
        -------
        str
            Texte concaténé prêt à être vectorisé.
        """
        parts = [
            title or "",
            subtitle or "",
            " ".join(tags) if tags else "",
            description or "",
        ]

        return " ".join(part.strip() for part in parts if part and part.strip())

    def generate_embedding(
        self,
        text: str
    ) -> np.ndarray:
        """
        Génère l'embedding d'un texte.

        Parameters
        ----------
        text : str
            Texte à encoder.

        Returns
        -------
        numpy.ndarray
            Vecteur d'embedding.
        """

        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )



    def encode_keywords(
        self,
        keywords: list[str]
    ) -> np.ndarray:
        """
        Génère l'embedding d'une liste de mots-clés.

        Parameters
        ----------
        keywords : list[str]
            Liste des mots-clés enrichis.

        Returns
        -------
        numpy.ndarray
            Embedding de la requête enrichie.
        """

        text = self.prepare_query(keywords)

        return self.generate_embedding(text)
    
    def encode_dataset(
        self,
        title: str,
        description: str,
        tags: list[str],
        subtitle: str = ""
    ) -> np.ndarray:
        """
        Génère l'embedding d'un dataset à partir de ses métadonnées.

        Parameters
        ----------
        title : str
            Titre du dataset.

        description : str
            Description du dataset.

        tags : list[str]
            Liste des tags associés au dataset.

        subtitle : str, optional
            Sous-titre du dataset.

        Returns
        -------
        numpy.ndarray
            Embedding du dataset.
        """
        text = self.prepare_dataset(
            title,
            description,
            tags,
            subtitle
        )

        return self.generate_embedding(text)
    
    def decode_embeddings(
        self,
        embeddings: pd.Series
    ) -> np.ndarray:
        """
        Convertit les embeddings stockés dans SQLite
        en tableau NumPy.

        Parameters
        ----------
        embeddings : pandas.Series
            Série contenant les embeddings (BLOB).

        Returns
        -------
        numpy.ndarray
            Tableau des embeddings.
        """

        return np.vstack(
            embeddings.apply(
                lambda blob: np.frombuffer(
                    blob,
                    dtype=np.float32
                )
            )
        )

    
    def compute_similarity(
        self,
        query_embedding: np.ndarray,
        dataset_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Calcule la similarité cosinus entre une requête
        et un ensemble d'embeddings de datasets.

        Parameters
        ----------
        query_embedding : numpy.ndarray
            Embedding de la requête utilisateur.

        dataset_embeddings : numpy.ndarray
            Tableau contenant les embeddings des datasets.

        Returns
        -------
        numpy.ndarray
            Scores de similarité entre la requête et chaque dataset.
        """
    
        return cosine_similarity(
            query_embedding.reshape(1, -1),
            dataset_embeddings
        ).flatten()

