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
# Prediction
# --------------------------------------------------

@app.post("/predict")
def predict(customer: CustomerData):

    input_data = pd.DataFrame([customer.model_dump()])

    probability = model.predict_proba(input_data)[0, 1]

    prediction = int(probability >= threshold)


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