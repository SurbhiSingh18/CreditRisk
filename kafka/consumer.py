import json
import csv
from kafka import KafkaConsumer


KAFKA_SERVER = "localhost:9092"
TOPIC = "credit-applicants"
OUTPUT_FILE = "data/kafka_raw_applicants.csv"


def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        group_id="credit-risk-hdfs-consumer",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8"))
    )

    rows = []
    fieldnames = None

    print("Listening for applicant records...")

    for message in consumer:
        applicant = message.value

        if fieldnames is None:
            fieldnames = list(applicant.keys())

        rows.append(applicant)

        print(f"Received applicant {applicant['applicant_id']}")

        if len(rows) == 1000:
            break

    consumer.close()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} applicants to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
