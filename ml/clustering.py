import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

INPUT_FILE = "data/processed_credit_risk.csv"
OUTPUT_FILE = "data/clustered_credit_risk.csv"


def main():

    print("Loading processed dataset...")

    df = pd.read_csv(INPUT_FILE)

    # Columns that must NOT be used for clustering
    excluded_columns = [
        "applicant_id",
        "credit_risk"
    ]

    feature_columns = [
        column
        for column in df.columns
        if column not in excluded_columns
    ]

    X = df[feature_columns]

    print(f"Applicants: {len(df)}")
    print(f"Clustering features: {len(feature_columns)}")

    results = {}

    # Test both possible numbers of risk tiers
    for k in [4, 5]:

        print(f"\nRunning K-means with K={k}...")

        kmeans = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=20
        )

        labels = kmeans.fit_predict(X)

        score = silhouette_score(X, labels)

        results[k] = score

        print(f"Silhouette score for K={k}: {score:.4f}")

    # Select K with the better silhouette score
    best_k = max(results, key=results.get)

    print("\n--------------------------------")
    print("K-MEANS MODEL SELECTION")
    print("--------------------------------")

    for k, score in results.items():
        print(f"K={k}: silhouette score = {score:.4f}")

    print(f"\nSelected K = {best_k}")

    # Train final model
    final_kmeans = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=20
    )

    df["cluster"] = final_kmeans.fit_predict(X)

    # Save clustered dataset
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"\nClustered dataset saved to: {OUTPUT_FILE}")

    print("\nCluster counts:")
    print(df["cluster"].value_counts().sort_index())


if __name__ == "__main__":
    main()
