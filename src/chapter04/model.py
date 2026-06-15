# Logic huan luyen va du doan — tach rieng khoi API

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime


class LoanModel:
    """
    Dong goi toan bo logic cua mo hinh du doan vay von.
    Tach rieng khoi API de de test va thay the sau nay.
    """

    VERSION = "v1.0.0"
    FEATURES = ["age", "income", "credit_score", "loan_amount", "loan_term_months"]
    TRAINED_AT = datetime.now().strftime("%Y-%m-%d")

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.accuracy = None

    def _generate_training_data(self, n_samples: int = 1000):
        """
        Sinh du lieu huan luyen gia lap.
        Trong thuc te: doc tu database hoac file CSV.
        """
        np.random.seed(42)

        # Sinh dac trung (features)
        age           = np.random.randint(18, 65, n_samples)
        income        = np.random.uniform(5_000_000, 100_000_000, n_samples)
        credit_score  = np.random.randint(300, 850, n_samples)
        loan_amount   = np.random.uniform(10_000_000, 500_000_000, n_samples)
        loan_term     = np.random.randint(6, 120, n_samples)

        X = np.column_stack([age, income, credit_score, loan_amount, loan_term])

        # Sinh nhan (label): duoc duyet neu diem tin dung cao
        # va ty le vay/thu nhap khong qua cao
        loan_to_income = loan_amount / (income * loan_term)
        y = ((credit_score > 600) & (loan_to_income < 0.5)).astype(int)

        return X, y

    def train(self):
        """Huan luyen mo hinh voi du lieu gia lap."""
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score

        X, y = self._generate_training_data()

        # Chia tap huan luyen va kiem tra
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Chuan hoa dac trung
        X_train = self.scaler.fit_transform(X_train)
        X_test  = self.scaler.transform(X_test)

        # Huan luyen
        self.model.fit(X_train, y_train)

        # Danh gia
        y_pred = self.model.predict(X_test)
        self.accuracy = round(accuracy_score(y_test, y_pred), 4)
        self.is_trained = True

        print(f"Huan luyen xong. Accuracy: {self.accuracy:.2%}")

    def predict(self, age, income, credit_score, loan_amount, loan_term_months):
        """
        Du doan kha nang duoc duyet vay.
        Tra ve: (approved: bool, probability: float)
        """
        if not self.is_trained:
            raise RuntimeError("Mo hinh chua duoc huan luyen")

        # Chuan bi du lieu dau vao dung dinh dang model mong doi
        features = np.array([[age, income, credit_score, loan_amount, loan_term_months]])
        features = self.scaler.transform(features)

        # Du doan xac suat
        proba     = self.model.predict_proba(features)[0]
        approved  = bool(proba[1] >= 0.5)     # proba[1] = xac suat duoc duyet
        probability = round(float(proba[1]), 4)

        return approved, probability
