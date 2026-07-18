"""
Module de génération des embeddings.

Ce module est responsable de :

- charger le modèle SentenceTransformer ;
- transformer une requête enrichie en embedding ;
- retourner un vecteur compatible avec Elasticsearch.

Auteur : Safaa Bourennane
Projet : Moteur de recherche intelligent pour les jeux de données Open Data
"""

from sentence_transformers import SentenceTransformer
import numpy as np


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

    def prepare_text(
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

        return " ".join(keywords)

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

        embedding = self.model.encode(
            text,
            convert_to_numpy=True
        )

        return embedding

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

        text = self.prepare_text(keywords)

        return self.generate_embedding(text)