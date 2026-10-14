import pandas as pd

CLUSTERED_FILE = "data/clustered_credit_risk.csv"
RAW_FILE = "data/kafka_raw_applicants.csv"

OUTPUT_FILE = "data/final_risk_segments.csv"
SUMMARY_FILE = "data/risk_tier_summary.csv"


# Risk labels assigned after examining the cluster profiles.
CLUSTER_TO_TIER = {
    3: "Very Low Risk",
    2: "Low Risk",
    1: "Moderate Risk",
    0: "High Risk"
}


def main():

    print("Loading clustered dataset...")
    clustered = pd.read_csv(CLUSTERED_FILE)

    print("Loading original applicant data...")
    raw = pd.read_csv(RAW_FILE)

    # Keep only the information needed from the clustering output.
    cluster_assignments = clustered[
        ["applicant_id", "cluster"]
    ]

    # Merge cluster assignments with original applicant attributes.
    df = raw.merge(
        cluster_assignments,
        on="applicant_id",
        how="inner"
    )

    # Assign meaningful risk tiers.
    df["risk_tier"] = df["cluster"].map(CLUSTER_TO_TIER)

    # Verify that every applicant received a tier.
    if df["risk_tier"].isna().any():
        raise ValueError("Some clusters do not have a risk-tier mapping.")

    # Save final applicant-level segmentation.
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"\nSaved final segmentation to: {OUTPUT_FILE}")

    # Create summary from the ORIGINAL features.
    summary = (
        df.groupby(["cluster", "risk_tier"])
        .agg(
            applicants=("applicant_id", "count"),
            avg_credit_amount=("credit_amount", "mean"),
            avg_duration_months=("duration_months", "mean"),
            avg_installment_rate=("installment_rate", "mean"),
            avg_age=("age", "mean"),
            avg_existing_credits=("existing_credits", "mean"),
            good_credit=("credit_risk", lambda x: (x == 1).sum()),
            bad_credit=("credit_risk", lambda x: (x == 2).sum())
        )
        .reset_index()
    )

    # Calculate percentages.
    summary["applicant_pct"] = (
        summary["applicants"] /
        len(df) * 100
    )

    summary["good_credit_pct"] = (
        summary["good_credit"] /
        summary["applicants"] * 100
    )

    summary["bad_credit_pct"] = (
        summary["bad_credit"] /
        summary["applicants"] * 100
    )

    # Sort from lowest to highest risk.
    risk_order = {
        "Very Low Risk": 0,
        "Low Risk": 1,
        "Moderate Risk": 2,
        "High Risk": 3
    }

    summary["risk_order"] = summary["risk_tier"].map(risk_order)

    summary = (
        summary
        .sort_values("risk_order")
        .drop(columns=["risk_order"])
    )

    # Save summary.
    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    print(f"Saved risk summary to: {SUMMARY_FILE}")

    print("\n==============================")
    print("FINAL RISK-TIER SUMMARY")
    print("==============================")

    print(
        summary.to_string(
            index=False,
            formatters={
                "avg_credit_amount": "{:.2f}".format,
                "avg_duration_months": "{:.2f}".format,
                "avg_installment_rate": "{:.2f}".format,
                "avg_age": "{:.2f}".format,
                "avg_existing_credits": "{:.2f}".format,
                "applicant_pct": "{:.2f}".format,
                "good_credit_pct": "{:.2f}".format,
                "bad_credit_pct": "{:.2f}".format
            }
        )
    )


if __name__ == "__main__":
    main()
