from src.nlp.query_processor import QueryProcessor
from src.nlp.translator import Translator
from src.nlp.synonym_engine import SynonymEngine
from src.nlp.embedding_engine import EmbeddingEngine

def main():

    processor = QueryProcessor()
    translator = Translator()
    synonym_engine = SynonymEngine()
    embedding_engine = EmbeddingEngine()

    queries = [
        "Je cherche un dataset sur le diabète",
        "Je veux apprendre la classification",
        "Heart disease dataset",
        "dataset sur la santé"
    ]

    for query in queries:

        print("=" * 80)
        print(f"Requête utilisateur : {query}")

        processed = processor.process_query(query)

        translated_keywords = translator.translate_keywords(
            keywords=processed["keywords"],
            language=processed["language"]
        )

        enriched_keywords = synonym_engine.enrich_keywords(
            translated_keywords
        )
        embedding = embedding_engine.encode_keywords(
            enriched_keywords
        )

        print(f"Langue              : {processed['language']}")
        print(f"Mots-clés           : {processed['keywords']}")
        print(f"Mots traduits       : {translated_keywords}")
        print(f"Mots enrichis       : {enriched_keywords}")
        print(f"Dimension de l'embedding : {embedding.shape}")
        print(f"Premières valeurs : {embedding[:10]}")

if __name__ == "__main__":
    main()