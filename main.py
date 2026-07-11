"""
Point d'entrée principal du projet.
"""
import pandas as pd
from src.extraction.kaggle_extractor import KaggleExtractor



def main():

    extractor = KaggleExtractor()

    extractor.authenticate()

    df = extractor.search_to_dataframe(
        query="diabetes",
        limit=5
    )

    print(df)
    

if __name__ == "__main__":
    main()
