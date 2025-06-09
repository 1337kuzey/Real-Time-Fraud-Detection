from kafka import KafkaConsumer
import requests
import json
import datetime

# Define ANSI escape codes for colors and reset (logging)
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[33m'
RESET = '\033[0m'

#Configuration
KAFKA_TOPIC = "fraud_transactions"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
FASTAPI_URL = "http://localhost:8000/predict"

#Setup Kafka consumer
print(f"[{datetime.datetime.now()}] Starting Kafka consumer on topic '{KAFKA_TOPIC}'...")
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="fraud-detectors"
)

print(f"[{datetime.datetime.now()}] Kafka consumer connected. Waiting for messages...\n")

#Message loop
for message in consumer:
    transaction = message.value
    print(f"[{datetime.datetime.now()}] New transaction received")
    #print(json.dumps(transaction, indent=2))

    try:
        # Send transaction to FastAPI for prediction
        response = requests.post(FASTAPI_URL, json={"data": transaction})
        result = response.json()

        print(f"[{datetime.datetime.now()}] -> Sent to FastAPI. Response:")
        print(json.dumps(result, indent=2))

        if result.get("prediction") == 1:
            print(f"[{datetime.datetime.now()}] {YELLOW}FRAUD DETECTED!{RESET}")
            # Optionally send alert, write to DB, etc.
        else:
            print(f"[{datetime.datetime.now()}] {GREEN}Legitimate transaction.{RESET}")
        print()

    except Exception as e:
        print(f"[{datetime.datetime.now()}] {RED}Error during inference: {e}{RESET}")