from src.extraction.kaggle_extractor import KaggleExtractor
from src.profiling.metadata_profiler import MetadataProfiler


def main():

    extractor = KaggleExtractor()

    # Authentification à l'API Kaggle
    extractor.authenticate()

    profiler = MetadataProfiler()

    dataframe = extractor.search_to_dataframe(
        query="health",
        limit=10
    )

    dataframe = profiler.profile_dataframe(dataframe)

    print("\n========== METADATA SCORES ==========\n")

    print(
        dataframe[
            [
                "title",
                "completeness_score",
                "freshness_score",
                "reusability_score",
                "metadata_score",
            ]
        ].to_string(index=False)
    )

    print("\n========== RAW METADATA ==========\n")

    print(
        dataframe[
            [
                "title",
                "license",
                "creator",
                "owner",
                "subtitle",
                "last_updated",
                "tags",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()