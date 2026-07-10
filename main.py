"""
Point d'entrée principal du projet.
"""

from src.extraction.kaggle_extractor import KaggleExtractor


def main():
    """
    Lance le programme.
    """

    print("=== Moteur de recherche Open Data ===")

    extractor = KaggleExtractor()

    extractor.authenticate()

    print("Le module d'extraction est prêt.")


if __name__ == "__main__":
    main()