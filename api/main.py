from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path
import logging
import time
from fastapi import Request
import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("API_KEY")

# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model" / "telco_churn_model.pkl"
FRONTEND_PATH = BASE_DIR / "frontend"


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(title="Telco Customer Churn API")



@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    logger.info(
        "Request | method=%s | path=%s | status=%d | duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        duration * 1000
    )

    return response


# Serve CSS and JavaScript files
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_PATH),
    name="static"
)



prediction_count = 0
churn_prediction_count = 0
no_churn_prediction_count = 0





# --------------------------------------------------
# Load trained model
# --------------------------------------------------

bundle = joblib.load(MODEL_PATH)

model = bundle["model"]
threshold = bundle["threshold"]


# --------------------------------------------------
# Input schema
# --------------------------------------------------

class CustomerData(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float


# --------------------------------------------------
# Home page
# --------------------------------------------------

@app.get("/")
def home():
    return FileResponse(FRONTEND_PATH / "index.html")


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


# --------------------------------------------------
# monitoring endpoint
# --------------------------------------------------


@app.get("/monitoring")
def monitoring():
    return {
        "total_predictions": prediction_count,
        "churn_predictions": churn_prediction_count,
        "no_churn_predictions": no_churn_prediction_count
    }


# --------------------------------------------------
# Prediction
# --------------------------------------------------

def run_prediction(customer: CustomerData):

    input_data = pd.DataFrame([customer.model_dump()])

    probability = model.predict_proba(input_data)[0, 1]

    prediction = int(probability >= threshold)

    global prediction_count, churn_prediction_count, no_churn_prediction_count

    prediction_count += 1

    if prediction == 1:
        churn_prediction_count += 1
    else:
        no_churn_prediction_count += 1

    logger.info(
        "Prediction made | probability=%.4f | threshold=%.2f | prediction=%d",
        probability,
        threshold,
        prediction
    )

    return {
        "churn_probability": round(float(probability), 4),
        "threshold": threshold,
        "prediction": prediction,
        "prediction_label": (
            "Likely to churn"
            if prediction == 1
            else "Likely to stay"
        )
    }




@app.post("/predict")
def predict(customer: CustomerData, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )

    return run_prediction(customer)





@app.post("/frontend-predict")
def frontend_predict(customer: CustomerData):

    return run_prediction(customer)