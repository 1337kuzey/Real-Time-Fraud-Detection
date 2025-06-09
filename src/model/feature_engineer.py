import pandas as pd
import numpy as np

#feature engineering
def transform(X):
    X = X.copy()
    X['TransactionAmt'] = pd.to_numeric(X['TransactionAmt'], errors='coerce').fillna(0.0)
    X['TransactionDT'] = pd.to_numeric(X['TransactionDT'], errors='coerce').fillna(0)
    X['TransactionAmt_log'] = np.log1p(X['TransactionAmt'])
    X['hour'] = (X['TransactionDT'] // 3600) % 24
    X['weekday'] = (X['TransactionDT'] // (3600 * 24)) % 7
    X['DeviceInfo'] = X['DeviceInfo'].fillna('unknown').str.lower()
    X['DeviceInfo_clean'] = X['DeviceInfo'].str.extract(r'(^[a-zA-Z]+)')
    return X
