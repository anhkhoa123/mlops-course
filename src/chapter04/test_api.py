# Kiem thu tu dong toan bo endpoint
# Chay: python -m pytest src/chapter04/test_api.py -v

import pytest
from fastapi.testclient import TestClient
from src.chapter04.main import app


# TestClient gia lap HTTP request ma khong can chay server that
# Rat huu ich trong CI/CD pipeline
client = TestClient(app)


class TestHealthEndpoint:
    """Kiem thu endpoint /health"""

    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_correct_fields(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "model_version" in data

    def test_health_status_is_healthy(self):
        response = client.get("/health")
        assert response.json()["status"] == "healthy"

    def test_model_is_loaded(self):
        response = client.get("/health")
        assert response.json()["model_loaded"] is True


class TestModelInfoEndpoint:
    """Kiem thu endpoint /model/info"""

    def test_model_info_returns_200(self):
        response = client.get("/model/info")
        assert response.status_code == 200

    def test_model_info_has_required_fields(self):
        data = client.get("/model/info").json()
        assert "model_version" in data
        assert "algorithm" in data
        assert "features" in data
        assert "accuracy" in data

    def test_accuracy_in_valid_range(self):
        data = client.get("/model/info").json()
        assert 0.0 <= data["accuracy"] <= 1.0


class TestPredictEndpoint:
    """Kiem thu endpoint /predict"""

    # Du lieu mau dung chuan — dung lai nhieu test
    valid_payload = {
        "age": 35,
        "income": 50_000_000,
        "credit_score": 750,
        "loan_amount": 100_000_000,
        "loan_term_months": 24,
    }

    def test_predict_returns_200(self):
        response = client.post("/predict", json=self.valid_payload)
        assert response.status_code == 200

    def test_predict_response_has_required_fields(self):
        data = client.post("/predict", json=self.valid_payload).json()
        assert "approved" in data
        assert "probability" in data
        assert "model_version" in data
        assert "message" in data

    def test_probability_in_valid_range(self):
        data = client.post("/predict", json=self.valid_payload).json()
        assert 0.0 <= data["probability"] <= 1.0

    def test_approved_is_boolean(self):
        data = client.post("/predict", json=self.valid_payload).json()
        assert isinstance(data["approved"], bool)

    def test_invalid_credit_score_returns_422(self):
        """credit_score phai trong khoang 300-850"""
        bad_payload = {**self.valid_payload, "credit_score": 999}
        response = client.post("/predict", json=bad_payload)
        assert response.status_code == 422

    def test_negative_income_returns_422(self):
        """income phai > 0"""
        bad_payload = {**self.valid_payload, "income": -1000}
        response = client.post("/predict", json=bad_payload)
        assert response.status_code == 422

    def test_missing_required_field_returns_422(self):
        """Thieu truong bat buoc phai tra ve 422"""
        incomplete = {"age": 35, "income": 50_000_000}
        response = client.post("/predict", json=incomplete)
        assert response.status_code == 422

    def test_underage_applicant_returns_422(self):
        """Tuoi phai >= 18"""
        bad_payload = {**self.valid_payload, "age": 16}
        response = client.post("/predict", json=bad_payload)
        assert response.status_code == 422

    def test_default_loan_term_is_used_when_not_provided(self):
        """loan_term_months co gia tri mac dinh, khong can truyen"""
        payload_without_term = {k: v for k, v in self.valid_payload.items()
                                if k != "loan_term_months"}
        response = client.post("/predict", json=payload_without_term)
        assert response.status_code == 200
