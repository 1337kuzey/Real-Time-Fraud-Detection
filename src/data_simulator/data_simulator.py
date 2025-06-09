import pandas as pd
import time
import json
from kafka import KafkaProducer

#config
KAFKA_TOPIC = "fraud_transactions"
KAFKA_BROKER = "localhost:9092"

#load a sample of the dataset
def load_data(path: str, n_rows: int = 100, start_line: int = 0):
    skip = range(1, start_line)  # skip rows 1 to start_line-1 (0 is header)    
    df = pd.read_csv(path, nrows=n_rows, skiprows=skip)
    df = df.astype(str)  #convert all columns to string for Kafka JSON serialization
    return df

#Kafka JSON serializer
def json_serializer(data):
    return json.dumps(data).encode("utf-8")

#simulate streaming data row by row
def stream_data(df: pd.DataFrame, producer: KafkaProducer, delay: float = 1.0):
    print(f"Starting to stream {len(df)} rows to Kafka topic '{KAFKA_TOPIC}'")
    for idx, row in df.iterrows():
        message = row.to_dict()
        producer.send(KAFKA_TOPIC, value=message)
        print(f"Sent row {idx + 1}")
        time.sleep(delay)

if __name__ == "__main__":
    dataset_path = "data/merged/test_transaction_identity_merged.csv"

    df = load_data(dataset_path, n_rows=10000, start_line=0)

    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=json_serializer,
    )

    try:
        stream_data(df, producer, delay=0.5)
    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")
    finally:
        producer.flush()
        producer.close()
