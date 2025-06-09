import pandas as pd
import os

RAW_DIR = "data/raw"
MERGED_DIR = "data/merged"

os.makedirs(MERGED_DIR, exist_ok=True)

def merge_and_save(transaction_file, identity_file, output_file):
    output_path = os.path.join(MERGED_DIR, output_file)

    if not os.path.exists(output_path):
        print(f"[INFO] Merged file {output_file} not found. Merging now...")

        transaction = pd.read_csv(os.path.join(RAW_DIR, transaction_file))
        identity = pd.read_csv(os.path.join(RAW_DIR, identity_file))

        merged = transaction.merge(identity, how="left", on="TransactionID")
        merged.to_csv(output_path, index=False)

        print(f"[INFO] Merged dataset saved to {output_path}")
    else:
        print(f"[INFO] Merged file already exists: {output_path}")

#Merge train data
merge_and_save("train_transaction.csv", "train_identity.csv", "train_transaction_identity_merged.csv")
#Merge test data
merge_and_save("test_transaction.csv", "test_identity.csv", "test_transaction_identity_merged.csv")
