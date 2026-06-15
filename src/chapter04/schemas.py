# Dinh nghia cau truc du lieu vao/ra cho API

from pydantic import BaseModel, Field
from typing import Optional


class LoanRequest(BaseModel):
    """
    Du lieu dau vao khi goi endpoint /predict.
    Moi truong deu duoc FastAPI kiem tra tu dong.
    """
    age: int = Field(
        ...,              # "..." nghia la bat buoc, khong co gia tri mac dinh
        ge=18,            # >= 18
        le=100,           # <= 100
        description="Tuoi cua khach hang",
        example=35,
    )
    income: float = Field(
        ...,
        gt=0,             # > 0
        description="Thu nhap hang thang (VND)",
        example=25000000,
    )
    credit_score: int = Field(
        ...,
        ge=300,
        le=850,
        description="Diem tin dung (300-850)",
        example=720,
    )
    loan_amount: float = Field(
        ...,
        gt=0,
        description="So tien muon vay (VND)",
        example=100000000,
    )
    loan_term_months: int = Field(
        default=12,       # co gia tri mac dinh, khong bat buoc truyen
        ge=1,
        le=360,
        description="Thoi han vay (thang)",
        example=24,
    )


class LoanResponse(BaseModel):
    """
    Du lieu tra ve sau khi du doan.
    """
    approved: bool
    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Xac suat duoc duyet vay",
    )
    model_version: str
    message: str


class HealthResponse(BaseModel):
    """Ket qua health check."""
    status: str
    model_loaded: bool
    model_version: str


class ModelInfoResponse(BaseModel):
    """Thong tin ve model dang phuc vu."""
    model_version: str
    algorithm: str
    trained_at: str
    features: list[str]
    accuracy: Optional[float] = None
