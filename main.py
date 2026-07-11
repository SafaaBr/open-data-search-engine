from src.extraction.kaggle_extractor import KaggleExtractor
from src.database.database_manager import DatabaseManager


def main():

    # -------- Extraction Kaggle --------

    extractor = KaggleExtractor()

    extractor.authenticate()

    df = extractor.search_to_dataframe(
        query="diabetes",
        limit=5
    )

    # -------- SQLite --------

    db = DatabaseManager()

    db.connect()

    db.create_tables()

    db.save_dataframe(df)

    dataframe = db.load_dataframe()

    print(dataframe)

    db.close()


if __name__ == "__main__":
    main()