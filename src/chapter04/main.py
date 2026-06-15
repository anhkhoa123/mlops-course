# API server chinh — noi ket noi schemas va model

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from src.chapter04.schemas import (
    LoanRequest,
    LoanResponse,
    HealthResponse,
    ModelInfoResponse,
)
from src.chapter04.model import LoanModel


# ============================================================
# Khoi tao model mot lan khi server bat dau
# Dung "lifespan" thay vi @app.on_event (cach moi cua FastAPI)
# ============================================================
model = LoanModel()
model.train()  # Ép huấn luyện ngay lập tức khi file vừa được import

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Chay khi server khoi dong: huan luyen model.
    Trong thuc te: tai model tu file .pkl hoac MLflow registry.
    """
    print("Server dang khoi dong — huan luyen model...")
    model.train()
    print("Model san sang phuc vu request")
    yield
    # Code sau yield chay khi server tat
    print("Server dang tat")


app = FastAPI(
    title="Loan Prediction API",
    description="API du doan kha nang duoc duyet vay von",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# Endpoint 1: Health check
# GET /health
# Load balancer goi endpoint nay de biet server con song khong
# ============================================================
@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        model_loaded=model.is_trained,
        model_version=LoanModel.VERSION,
    )


# ============================================================
# Endpoint 2: Thong tin model
# GET /model/info
# ============================================================
@app.get("/model/info", response_model=ModelInfoResponse)
def get_model_info():
    if not model.is_trained:
        raise HTTPException(status_code=503, detail="Model chua san sang")

    return ModelInfoResponse(
        model_version=LoanModel.VERSION,
        algorithm="RandomForestClassifier",
        trained_at=LoanModel.TRAINED_AT,
        features=LoanModel.FEATURES,
        accuracy=model.accuracy,
    )


# ============================================================
# Endpoint 3: Du doan
# POST /predict
# Day la endpoint chinh — nhan du lieu, tra ve ket qua du doan
# ============================================================
@app.post("/predict", response_model=LoanResponse)
def predict(request: LoanRequest):
    """
    Nhan thong tin khach hang, tra ve ket qua xet duyet vay.

    FastAPI tu dong:
    - Phan tich JSON tu request body thanh object LoanRequest
    - Kiem tra tung truong dung kieu va rang buoc da khai bao
    - Tra loi loi 422 neu du lieu sai truoc khi vao toi ham nay
    """
    if not model.is_trained:
        raise HTTPException(status_code=503, detail="Model chua san sang, thu lai sau")

    try:
        approved, probability = model.predict(
            age              = request.age,
            income           = request.income,
            credit_score     = request.credit_score,
            loan_amount      = request.loan_amount,
            loan_term_months = request.loan_term_months,
        )
    except Exception as e:
        # Bat loi khong mong doi, tra ve 500 thay vi de server crash
        raise HTTPException(status_code=500, detail=f"Loi khi du doan: {str(e)}")

    # Tao message giai thich ket qua
    if approved:
        message = f"Duoc duyet. Xac suat chap thuan: {probability:.0%}"
    else:
        message = f"Tu choi. Xac suat chap thuan chi dat: {probability:.0%}"

    return LoanResponse(
        approved      = approved,
        probability   = probability,
        model_version = LoanModel.VERSION,
        message       = message,
    )
