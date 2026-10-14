import csv
import json
import time

from kafka import KafkaProducer


KAFKA_SERVER = "localhost:9092"
TOPIC = "credit-applicants"
CSV_FILE = "data/german_credit.csv"


def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda value: json.dumps(value).encode("utf-8")
    )


def main():
    producer = create_producer()

    with open(CSV_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for applicant_id, row in enumerate(reader, start=1):
            row["applicant_id"] = applicant_id

            producer.send(TOPIC, value=row)

            print(f"Sent applicant {applicant_id}")

            time.sleep(0.05)

    producer.flush()
    producer.close()

    print("All applicant records sent successfully.")


if __name__ == "__main__":
    main()
