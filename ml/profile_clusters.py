import pandas as pd

INPUT_FILE = "data/clustered_credit_risk.csv"
RAW_FILE = "data/kafka_raw_applicants.csv"


def main():

    df = pd.read_csv(INPUT_FILE)
    raw = pd.read_csv(RAW_FILE)

    # Combine cluster assignment with original categorical values
    analysis = raw.merge(
        df[["applicant_id", "cluster"]],
        on="applicant_id",
        how="inner"
    )

    print("\n==============================")
    print("CLUSTER SIZE")
    print("==============================")

    print(
        analysis["cluster"]
        .value_counts()
        .sort_index()
    )

    print("\n==============================")
    print("NUMERICAL PROFILE")
    print("==============================")

    numerical_columns = [
        "credit_amount",
        "duration_months",
        "installment_rate",
        "age",
        "existing_credits"
    ]

    profile = analysis.groupby("cluster")[numerical_columns].mean()

    print(profile.round(2))

    print("\n==============================")
    print("CREDIT RISK DISTRIBUTION")
    print("==============================")

    risk_distribution = pd.crosstab(
        analysis["cluster"],
        analysis["credit_risk"],
        normalize="index"
    ) * 100

    risk_distribution = risk_distribution.rename(
        columns={
            1: "Good (%)",
            2: "Bad (%)"
        }
    )

    print(risk_distribution.round(2))

    print("\n==============================")
    print("CREDIT HISTORY")
    print("==============================")

    history_distribution = pd.crosstab(
        analysis["cluster"],
        analysis["credit_history"],
        normalize="index"
    ) * 100

    print(history_distribution.round(2))

    print("\n==============================")
    print("CHECKING ACCOUNT")
    print("==============================")

    checking_distribution = pd.crosstab(
        analysis["cluster"],
        analysis["checking_account"],
        normalize="index"
    ) * 100

    print(checking_distribution.round(2))

    print("\n==============================")
    print("SAVINGS ACCOUNT")
    print("==============================")

    savings_distribution = pd.crosstab(
        analysis["cluster"],
        analysis["savings_account"],
        normalize="index"
    ) * 100

    print(savings_distribution.round(2))


if __name__ == "__main__":
    main()

