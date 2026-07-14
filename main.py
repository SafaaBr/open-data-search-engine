from src.nlp.query_processor import QueryProcessor


def main():

    processor = QueryProcessor()

    queries = [
        "classification",
        "Je veux apprendre la classification.",
        "Je cherche un dataset sur le diabète.",
        "Heart disease dataset",
        "Regression"
    ]

    for query in queries:

        result = processor.process_query(query)

        print("-" * 50)
        print(result)


if __name__ == "__main__":
    main()