import csv

input_file = "data/german.data"
output_file = "data/german_credit.csv"

columns = [
    "checking_account",
    "duration_months",
    "credit_history",
    "purpose",
    "credit_amount",
    "savings_account",
    "employment",
    "installment_rate",
    "personal_status",
    "other_debtors",
    "residence_since",
    "property",
    "age",
    "other_installment_plans",
    "housing",
    "existing_credits",
    "job",
    "dependents",
    "telephone",
    "foreign_worker",
    "credit_risk"
]

with open(input_file, "r", encoding="utf-8") as infile:
    rows = [line.strip().split() for line in infile if line.strip()]

# Verify dataset structure
for i, row in enumerate(rows, start=1):
    if len(row) != 21:
        raise ValueError(
            f"Row {i} has {len(row)} values instead of 21"
        )

with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(columns)
    writer.writerows(rows)

print(f"Created: {output_file}")
print(f"Rows: {len(rows)}")
print(f"Columns: {len(columns)}")
