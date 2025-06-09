FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (fix for LightGBM)
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY api_requirements.txt .
RUN pip install --no-cache-dir "catboost==1.2.8"
RUN pip install --no-cache-dir -r api_requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.inference.inference:app", "--host", "0.0.0.0", "--port", "8000"]