import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

INPUT_FILE = "data/kafka_raw_applicants.csv"
OUTPUT_FILE = "data/processed_credit_risk.csv"

# Features selected for risk segmentation
FEATURES = [
    "checking_account",
    "duration_months",
    "credit_history",
    "credit_amount",
    "savings_account",
    "employment",
    "installment_rate",
    "age",
    "existing_credits",
    "other_installment_plans"
]

# Categorical features
CATEGORICAL_FEATURES = [
    "checking_account",
    "credit_history",
    "savings_account",
    "employment",
    "other_installment_plans"
]

# Numerical features
NUMERICAL_FEATURES = [
    "duration_months",
    "credit_amount",
    "installment_rate",
    "age",
    "existing_credits"
]


def main():

    print("Reading dataset...")
    df = pd.read_csv(INPUT_FILE)

    print(f"Original dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # Select only features used for clustering
    X = df[FEATURES].copy()

    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES
            ),
            (
                "numerical",
                StandardScaler(),
                NUMERICAL_FEATURES
            )
        ]
    )

    print("Encoding categorical features...")
    print("Scaling numerical features...")

    X_processed = preprocessor.fit_transform(X)

    # Convert processed data to DataFrame
    feature_names = preprocessor.get_feature_names_out()

    processed_df = pd.DataFrame(
        X_processed,
        columns=feature_names
    )

    # Keep applicant ID separately
    processed_df.insert(
        0,
        "applicant_id",
        df["applicant_id"].values
    )

    # Keep original credit risk only for later evaluation.
    # It is NOT used as a clustering feature.
    processed_df["credit_risk"] = df["credit_risk"].values

    processed_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nPreprocessing completed successfully.")
    print(f"Processed dataset: {processed_df.shape[0]} rows")
    print(f"Processed features: {X_processed.shape[1]}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
