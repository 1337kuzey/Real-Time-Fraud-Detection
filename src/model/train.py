import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from src.model.feature_engineer import transform
import joblib
import warnings
warnings.filterwarnings("ignore")

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

#selected features based on community + performance
NUMERIC_FEATURES = ['TransactionAmt', 'TransactionAmt_log', 'hour', 'weekday', 'D1', 'D2', 'C1', 'C13']
CATEGORICAL_FEATURES = ['ProductCD', 'card4', 'card6', 'P_emaildomain', 'DeviceInfo_clean']
BINARY_M_FEATURES = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9']

#build preprocessing pipeline
def build_pipeline():
    numeric_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])
    categorical_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    preprocessor = ColumnTransformer([
        ('num', numeric_pipeline, NUMERIC_FEATURES),
        ('cat', categorical_pipeline, CATEGORICAL_FEATURES + BINARY_M_FEATURES)
    ])
    return preprocessor

#load data
df = pd.read_csv("data/merged/train_transaction_identity_merged.csv")  # adjust nrows for speed
X = df.drop("isFraud", axis=1)
y = df["isFraud"]

X_train, X_val, y_train, y_val = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

#build pipeline
preprocessor = build_pipeline()

#define models
models = {
    "XGBoost": XGBClassifier(n_estimators=300, max_depth=6, scale_pos_weight=20,
                             learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                             use_label_encoder=False, eval_metric="logloss", n_jobs=-1, random_state=42),

    "LightGBM": LGBMClassifier(objective='binary', class_weight='balanced', num_leaves=64,
                               learning_rate=0.05, n_estimators=300, subsample=0.8,
                               colsample_bytree=0.8, n_jobs=-1, random_state=42),

    "CatBoost": CatBoostClassifier(iterations=300, learning_rate=0.05, depth=6,
                                   class_weights=[1, 20], verbose=0, random_seed=42)
}

#evaluate and export models
for name, model in models.items():
    print(f"\n[TRAINING] {name}")
    X_train_eng = transform(X_train)
    X_val_eng = transform(X_val)

    pipeline = Pipeline([
        ("preprocessing", preprocessor),
        ("model", model)
    ])
    pipeline.fit(X_train_eng, y_train)

    y_pred = pipeline.predict(X_val_eng)
    y_proba = pipeline.predict_proba(X_val_eng)[:, 1]
    roc_auc = roc_auc_score(y_val, y_proba)
    cm = confusion_matrix(y_val, y_pred)

    print(f"\n[RESULTS] {name}")
    print(classification_report(y_val, y_pred, digits=4))
    print(f"ROC AUC: {roc_auc:.4f}")
    print(f"Confusion Matrix:\n{cm}")

    #export model
    joblib.dump(pipeline, f"src/model/saved/{name}_ieee_model.pkl")
    print(f"Model exported to {name}_ieee_model.pkl")
