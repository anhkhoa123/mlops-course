# Mo phong toan bo vong doi ML co logging va bao cao

import time
import numpy as np
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score,
    recall_score, roc_auc_score, classification_report,
)


# ============================================================
# Dataclass luu ket qua tung giai doan
# ============================================================

@dataclass
class DataInfo:
    """Thong tin ve tap du lieu sau khi thu thap."""
    n_samples     : int
    n_features    : int
    n_classes     : int
    class_ratio   : dict          # ty le phan phoi nhan
    missing_ratio : float         # ty le gia tri bi mat
    collected_at  : str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class FeatureSet:
    """Tap dac trung sau khi chuan bi."""
    feature_names   : list[str]
    n_train         : int
    n_val           : int
    n_test          : int
    scaler_applied  : bool


@dataclass
class ExperimentResult:
    """Ket qua 1 lan thi nghiem huan luyen."""
    experiment_id   : str
    model_name      : str
    hyperparams     : dict
    accuracy        : float
    f1              : float
    precision       : float
    recall          : float
    auc_roc         : float
    cv_score_mean   : float       # diem cross-validation trung binh
    cv_score_std    : float       # do lech chuan cross-validation
    train_time_sec  : float
    trained_at      : str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ProjectReport:
    """Bao cao tong ket toan bo vong doi du an."""
    project_name    : str
    problem_type    : str
    target_metric   : str
    data_info       : Optional[DataInfo]          = None
    feature_set     : Optional[FeatureSet]        = None
    experiments     : list[ExperimentResult]      = field(default_factory=list)
    best_experiment : Optional[ExperimentResult]  = None
    deploy_ready    : bool                        = False
    started_at      : str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================
# Cac ham cho tung giai doan
# ============================================================

def log(message: str, indent: int = 0):
    """In log co timestamp va thu tu."""
    prefix = "  " * indent
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {prefix}{message}")


# ------ Giai doan 1: Xac dinh bai toan ------

def define_problem() -> dict:
    """
    Giai doan 1: Xac dinh ro bai toan truoc khi viet bat ky dong code nao.
    Tra ve dict chua cac thong so cua bai toan.
    """
    log("GIAI DOAN 1: XAC DINH BAI TOAN")
    log("Bai toan: Du doan kha nang vay von duoc chap thuan", 1)
    log("Loai bai toan: Phan loai nhi phan (Binary Classification)", 1)
    log("Metric chinh: F1-score (vi du lieu mat can bang)", 1)
    log("Nguong chap nhan: F1 >= 0.85, AUC-ROC >= 0.90", 1)
    log("Nguong latency: < 50ms moi request", 1)

    return {
        "problem_type"      : "binary_classification",
        "target_metric"     : "f1_score",
        "min_f1"            : 0.85,
        "min_auc_roc"       : 0.90,
        "max_latency_ms"    : 50,
        "positive_class"    : "approved",
    }


# ------ Giai doan 2: Thu thap & kham pha du lieu ------

def collect_and_explore_data(n_samples: int = 2000) -> tuple[pd.DataFrame, DataInfo]:
    """
    Giai doan 2: Thu thap du lieu va khám pha co ban.
    Tra ve DataFrame va DataInfo.
    """
    log("GIAI DOAN 2: THU THAP & KHAM PHA DU LIEU")
    log(f"Dang lay {n_samples} mau tu database...", 1)

    np.random.seed(42)

    # Sinh du lieu gia lap — trong thuc te doc tu database
    age          = np.random.randint(18, 65, n_samples)
    income       = np.random.uniform(5_000_000, 100_000_000, n_samples)
    credit_score = np.random.randint(300, 850, n_samples)
    loan_amount  = np.random.uniform(10_000_000, 500_000_000, n_samples)
    loan_term    = np.random.randint(6, 120, n_samples)
    employment_years = np.random.uniform(0, 30, n_samples)

    # Them gia tri bi mat (missing values) gia lap — thuc te hay gap
    credit_score_with_missing = credit_score.astype(float)
    missing_idx = np.random.choice(n_samples, size=int(n_samples * 0.08), replace=False)
    credit_score_with_missing[missing_idx] = np.nan   # 8% bi mat

    # Tinh nhan: duoc duyet neu diem tin dung cao va ty le no hop ly
    loan_to_income = loan_amount / (income * loan_term)
    approved = ((credit_score > 600) & (loan_to_income < 0.4)).astype(int)

    df = pd.DataFrame({
        "age"             : age,
        "income"          : income,
        "credit_score"    : credit_score_with_missing,
        "loan_amount"     : loan_amount,
        "loan_term"       : loan_term,
        "employment_years": employment_years,
        "approved"        : approved,
    })

    # Thong ke kham pha
    n_approved = int(approved.sum())
    n_rejected = n_samples - n_approved
    missing    = float(df.isnull().sum().sum() / (n_samples * len(df.columns)))

    data_info = DataInfo(
        n_samples     = n_samples,
        n_features    = len(df.columns) - 1,   # tru cot nhan
        n_classes     = 2,
        class_ratio   = {
            "approved": round(n_approved / n_samples, 3),
            "rejected": round(n_rejected / n_samples, 3),
        },
        missing_ratio = round(missing, 4),
    )

    log(f"Da lay {n_samples} mau", 1)
    log(f"So dac trung: {data_info.n_features}", 1)
    log(f"Phan phoi nhan: {data_info.class_ratio}", 1)
    log(f"Ty le gia tri bi mat: {data_info.missing_ratio:.1%}", 1)

    if data_info.missing_ratio > 0.1:
        log("CANH BAO: Ty le gia tri bi mat cao (>10%)", 1)

    return df, data_info


# ------ Giai doan 3: Chuan bi du lieu ------

def prepare_data(df: pd.DataFrame) -> tuple:
    """
    Giai doan 3: Xu ly gia tri bi mat, tao dac trung moi, chia du lieu.
    Tra ve X_train, X_val, X_test, y_train, y_val, y_test, feature_names.
    """
    log("GIAI DOAN 3: CHUAN BI DU LIEU & FEATURE ENGINEERING")

    df = df.copy()

    # Xu ly gia tri bi mat: dien gia tri trung vi
    missing_before = df["credit_score"].isnull().sum()
    df["credit_score"] = df["credit_score"].fillna(df["credit_score"].median())
    log(f"Da xu ly {missing_before} gia tri bi mat o credit_score (dien trung vi)", 1)

    # Feature Engineering: tao dac trung moi
    df["loan_to_income"]      = df["loan_amount"] / df["income"]
    df["monthly_payment"]     = df["loan_amount"] / df["loan_term"]
    df["payment_to_income"]   = df["monthly_payment"] / (df["income"] / 12)
    df["credit_income_score"] = df["credit_score"] * np.log1p(df["income"]) / 100
    log("Da tao 4 dac trung moi: loan_to_income, monthly_payment, payment_to_income, credit_income_score", 1)

    # Chuan bi X va y
    feature_cols = [
        "age", "income", "credit_score", "loan_amount",
        "loan_term", "employment_years",
        "loan_to_income", "monthly_payment",
        "payment_to_income", "credit_income_score",
    ]
    X = df[feature_cols].values
    y = df["approved"].values

    # Chia du lieu 70 / 15 / 15
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp
        # 0.176 ~= 15 / 85 de tap val chiem dung 15% toan bo
    )

    # Chuan hoa dac trung
    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train)   # fit_transform tren train
    X_val   = scaler.transform(X_val)         # chi transform tren val va test
    X_test  = scaler.transform(X_test)        # tuyet doi khong fit tren val/test

    log(f"Tap train : {len(X_train)} mau", 1)
    log(f"Tap val   : {len(X_val)} mau", 1)
    log(f"Tap test  : {len(X_test)} mau", 1)
    log("Da chuan hoa voi StandardScaler (fit tren train, transform val+test)", 1)

    feature_set = FeatureSet(
        feature_names  = feature_cols,
        n_train        = len(X_train),
        n_val          = len(X_val),
        n_test         = len(X_test),
        scaler_applied = True,
    )

    return X_train, X_val, X_test, y_train, y_val, y_test, feature_set, scaler


# ------ Giai doan 4: Huan luyen & thi nghiem ------

def run_experiments(X_train, X_val, y_train, y_val) -> list[ExperimentResult]:
    """
    Giai doan 4: Thu nghiem nhieu model va hyperparameter.
    Tra ve danh sach ket qua thi nghiem.
    """
    log("GIAI DOAN 4: HUAN LUYEN & THI NGHIEM")

    # Cac thi nghiem can chay — trong thuc te dung MLflow (Chuong 9)
    experiments_config = [
        {
            "id"        : "exp_001",
            "model_name": "LogisticRegression",
            "model"     : LogisticRegression(C=1.0, max_iter=500, random_state=42),
            "params"    : {"C": 1.0, "max_iter": 500},
        },
        {
            "id"        : "exp_002",
            "model_name": "RandomForest_100",
            "model"     : RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            "params"    : {"n_estimators": 100, "max_depth": 10},
        },
        {
            "id"        : "exp_003",
            "model_name": "RandomForest_200",
            "model"     : RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42),
            "params"    : {"n_estimators": 200, "max_depth": 15},
        },
        {
            "id"        : "exp_004",
            "model_name": "GradientBoosting",
            "model"     : GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
            "params"    : {"n_estimators": 100, "learning_rate": 0.1},
        },
    ]

    results = []

    for cfg in experiments_config:
        log(f"Dang chay thi nghiem {cfg['id']}: {cfg['model_name']}...", 1)
        start = time.time()

        # Huan luyen
        cfg["model"].fit(X_train, y_train)
        train_time = time.time() - start

        # Du doan tren tap validation
        y_pred      = cfg["model"].predict(X_val)
        y_pred_prob = cfg["model"].predict_proba(X_val)[:, 1]

        # Cross-validation tren tap train de kiem tra do on dinh
        cv_scores = cross_val_score(
            cfg["model"], X_train, y_train,
            cv=5, scoring="f1"
        )

        result = ExperimentResult(
            experiment_id  = cfg["id"],
            model_name     = cfg["model_name"],
            hyperparams    = cfg["params"],
            accuracy       = round(accuracy_score(y_val, y_pred), 4),
            f1             = round(f1_score(y_val, y_pred), 4),
            precision      = round(precision_score(y_val, y_pred), 4),
            recall         = round(recall_score(y_val, y_pred), 4),
            auc_roc        = round(roc_auc_score(y_val, y_pred_prob), 4),
            cv_score_mean  = round(cv_scores.mean(), 4),
            cv_score_std   = round(cv_scores.std(), 4),
            train_time_sec = round(train_time, 2),
        )
        results.append(result)

        log(f"  F1={result.f1:.4f} | AUC={result.auc_roc:.4f} | "
            f"CV={result.cv_score_mean:.4f}(+/-{result.cv_score_std:.4f}) | "
            f"Time={result.train_time_sec}s", 1)

    return results


# ------ Giai doan 5: Danh gia ------

def evaluate_best_model(results: list[ExperimentResult],
                         problem_config: dict,
                         X_test, y_test,
                         models: list) -> tuple[ExperimentResult, bool]:
    """
    Giai doan 5: Chon model tot nhat va danh gia tren tap test.
    Tap test chi duoc dung 1 lan duy nhat o buoc nay.
    """
    log("GIAI DOAN 5: DANH GIA & CHON MODEL TOT NHAT")

    # Chon model co F1 cao nhat tren tap validation
    best = max(results, key=lambda r: r.f1)
    log(f"Model tot nhat tren tap validation: {best.model_name}", 1)
    log(f"  F1={best.f1} | AUC-ROC={best.auc_roc}", 1)

    # Danh gia tren tap test — chi lam 1 lan
    log("Danh gia tren tap TEST (chi lam 1 lan duy nhat)...", 1)

    # Lay model object tuong ung
    best_idx   = next(i for i, r in enumerate(results) if r.experiment_id == best.experiment_id)
    best_model = models[best_idx]

    y_pred      = best_model.predict(X_test)
    y_pred_prob = best_model.predict_proba(X_test)[:, 1]

    test_f1      = round(f1_score(y_test, y_pred), 4)
    test_auc_roc = round(roc_auc_score(y_test, y_pred_prob), 4)

    log(f"Ket qua tren tap test:", 1)
    log(f"  F1       = {test_f1}", 2)
    log(f"  AUC-ROC  = {test_auc_roc}", 2)
    log(f"  Accuracy = {round(accuracy_score(y_test, y_pred), 4)}", 2)

    # Kiem tra dap ung nguong chap nhan
    meets_f1      = test_f1      >= problem_config["min_f1"]
    meets_auc_roc = test_auc_roc >= problem_config["min_auc_roc"]
    deploy_ready  = meets_f1 and meets_auc_roc

    if deploy_ready:
        log("Model DAP UNG nguong chat luong — San sang deploy", 1)
    else:
        log("Model CHUA DAP UNG nguong chat luong:", 1)
        if not meets_f1:
            log(f"  F1 = {test_f1} < {problem_config['min_f1']} (yeu cau)", 2)
        if not meets_auc_roc:
            log(f"  AUC-ROC = {test_auc_roc} < {problem_config['min_auc_roc']} (yeu cau)", 2)

    return best, deploy_ready


# ------ Giai doan 6: Trien khai (tom tat) ------

def simulate_deployment(best: ExperimentResult, deploy_ready: bool):
    """
    Giai doan 6: Tom tat cac buoc trien khai.
    Chi tiet se hoc o Chuong 11.
    """
    log("GIAI DOAN 6: TRIEN KHAI & GIAM SAT")

    if not deploy_ready:
        log("Khong the deploy vi model chua dat chat luong.", 1)
        log("Hanh dong tiep theo: Quay lai Giai doan 2 hoac 3", 1)
        log("  -> Kiem tra chat luong du lieu", 1)
        log("  -> Thu nghiem them dac trung moi", 1)
        log("  -> Thu them thuat toan khac", 1)
        return

    log(f"Chuan bi dong goi model {best.model_name} thanh Docker image...", 1)
    time.sleep(0.3)   # gia lap

    log("Deploy len moi truong staging...", 1)
    time.sleep(0.2)

    log("Chay smoke test tren staging...", 1)
    time.sleep(0.2)

    log("Deploy len production theo chien luoc Blue/Green...", 1)
    time.sleep(0.2)

    log("Bat dau giam sat: data drift, model accuracy, latency...", 1)
    log("Thiet lap canh bao tu dong khi accuracy giam > 5%...", 1)

    log("Trien khai thanh cong!", 1)
    log(f"Endpoint: http://api.company.com/v1/predict", 1)
    log(f"Dashboard: http://monitoring.company.com", 1)


# ============================================================
# Chay toan bo vong doi
# ============================================================

def run_full_lifecycle():
    print("\n" + "=" * 60)
    print("  VONG DOI DU AN ML: DU DOAN DUYET VAY VON")
    print("=" * 60 + "\n")

    report = ProjectReport(
        project_name = "Loan Approval Prediction",
        problem_type = "binary_classification",
        target_metric= "f1_score",
    )

    # Giai doan 1
    problem_config = define_problem()
    print()

    # Giai doan 2
    df, data_info = collect_and_explore_data(n_samples=2000)
    report.data_info = data_info
    print()

    # Giai doan 3
    X_train, X_val, X_test, y_train, y_val, y_test, feature_set, scaler = prepare_data(df)
    report.feature_set = feature_set
    print()

    # Giai doan 4
    results = run_experiments(X_train, X_val, y_train, y_val)
    report.experiments = results

    # Lay cac model object de dung trong giai doan 5
    # (trong thuc te lay tu MLflow registry)
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    models = [
        LogisticRegression(C=1.0, max_iter=500, random_state=42).fit(X_train, y_train),
        RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42).fit(X_train, y_train),
        RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42).fit(X_train, y_train),
        GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42).fit(X_train, y_train),
    ]
    print()

    # Giai doan 5
    best, deploy_ready = evaluate_best_model(
        results, problem_config, X_test, y_test, models
    )
    report.best_experiment = best
    report.deploy_ready    = deploy_ready
    print()

    # Giai doan 6
    simulate_deployment(best, deploy_ready)

    return report


if __name__ == "__main__":
    report = run_full_lifecycle()

    print("\n" + "=" * 60)
    print("  TOM TAT DU AN")
    print("=" * 60)
    print(f"  Du an       : {report.project_name}")
    print(f"  So mau      : {report.data_info.n_samples}")
    print(f"  So dac trung: {report.feature_set.n_train} train samples")
    print(f"  So thi nghiem: {len(report.experiments)}")
    if report.best_experiment:
        print(f"  Model chon  : {report.best_experiment.model_name}")
        print(f"  F1-score    : {report.best_experiment.f1}")
        print(f"  AUC-ROC     : {report.best_experiment.auc_roc}")
    print(f"  San sang deploy: {'Co' if report.deploy_ready else 'Chua'}")
    print("=" * 60)
