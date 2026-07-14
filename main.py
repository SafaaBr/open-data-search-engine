from src.nlp.query_processor import QueryProcessor
from src.nlp.translator import Translator


def main():

    processor = QueryProcessor()
    translator = Translator()

    queries = [
        "Je cherche un dataset sur le diabète",
        "Je veux apprendre la classification",
        "Heart disease dataset",
        "dataset qui parle sur la santé"
    ]

    for query in queries:

        processed = processor.process_query(query)

        translated_keywords = translator.translate_keywords(
            keywords=processed["keywords"],
            language=processed["language"]
        )

        print("=" * 70)
        print("Original :", query)
        print("Keywords :", processed["keywords"])
        print("Translated :", translated_keywords)


if __name__ == "__main__":
    main()