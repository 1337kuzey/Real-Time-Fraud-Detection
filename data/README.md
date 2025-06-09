# Data Directory  

This folder contains the data used for the Real-Time Fraud Detection System built on the IEEE-CIS Fraud Detection dataset.  

---

## Download Instructions  

To run this project, you'll need to manually download the IEEE-CIS Fraud Detection dataset from [Kaggle](https://www.kaggle.com/c/ieee-fraud-detection/data).  

Once downloaded, place the raw files in the following directory structure:  

data/
├── raw/
│ ├── train_transaction.csv
│ ├── train_identity.csv
│ ├── test_transaction.csv
│ └── test_identity.csv
├── merged/
│ ├── train_transaction_identity_merged.csv ← will be created by script
│ └── test_transaction_identity_merged.csv ← will be created by script
└── README.md

---

## Preprocessing Script  
To merge the transaction and identity files for training and testing:  
  
1. Make sure the raw `.csv` files are located in `data/raw/`.  
2. Run the following script:  
`python -m src.data_preparation.merge_raw`