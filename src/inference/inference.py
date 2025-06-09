from src.model.feature_engineer import transform
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import os
import time

app = FastAPI()

#Metrics setup
PREDICTION_COUNT = Counter("predict_requests_total", "Total number of prediction requests", ["method", "endpoint"])
PREDICTION_SCORE = Histogram("fraud_score", "Distribution of fraud prediction scores")
INFERENCE_LATENCY = Histogram("inference_latency_seconds", "Inference latency in seconds")
PREDICTION_LABEL = Counter("fraud_prediction_count", "Count of fraud vs real predictions" ,["label"])

#Load the full pipeline
print("[INFO] Loading model and preprocessing pipeline...")
model_name = os.getenv("MODEL_NAME", "XGBoost")
full_pipeline = joblib.load(f"src/model/saved/{model_name}_ieee_model.pkl")

#Request schema
class TransactionInput(BaseModel):
    data: dict  #expecting a merged transaction row as a dict

#Health check
@app.get("/")
def root():
    return {"status": "running"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

#Predict endpoint
@app.post("/predict")
def predict(request_data: TransactionInput):
    start_time = time.time()
    try:
        print("[INFO] Received transaction for inference")
        PREDICTION_COUNT.labels(method="POST", endpoint="/predict").inc()

        df = request_data.data
        df = pd.DataFrame([df])
        #print(f"[DEBUG] Incoming features: {list(df.columns)}")

        df_eng = transform(df)
        prediction = int(full_pipeline.predict(df_eng)[0])
        score = float(full_pipeline.predict_proba(df_eng)[0][1])

        PREDICTION_SCORE.observe(score)
        INFERENCE_LATENCY.observe(time.time() - start_time)
        label = "fraud" if prediction == 1 else "real"
        PREDICTION_LABEL.labels(label=label).inc()

        return {"prediction": prediction, "score": round(score, 4)}

    except Exception as e:
        print(f"[ERROR] Inference error: {e}")
        return {"error": str(e)}
