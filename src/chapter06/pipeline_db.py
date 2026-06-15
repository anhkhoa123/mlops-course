# Pipeline ML hoan chinh doc du lieu tu database va luu ket qua lai

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.chapter06.db import Database
from src.chapter05.model import LoanModel


def run_prediction_pipeline():
    """
    Pipeline chay hang ngay:
    1. Lay cac don vay dang cho xu ly tu database
    2. Chay model du doan cho tung don
    3. Luu ket qua du doan vao database
    4. Cap nhat trang thai don
    5. In bao cao tom tat
    """

    db    = Database()
    model = LoanModel()

    print("=" * 55)
    print(" PIPELINE DU DOAN TU DONG")
    print("=" * 55)

    # Buoc 1: Huan luyen model
    print("\nBuoc 1: Huan luyen model...")
    model.train()
    print(f"  Model {LoanModel.VERSION} san sang. Accuracy: {model.accuracy:.2%}")

    # Buoc 2: Lay don dang cho xu ly
    print("\nBuoc 2: Lay don dang cho xu ly tu database...")
    pending = db.get_pending_applications()
    print(f"  Tim thay {len(pending)} don dang cho xu ly")

    if not pending:
        print("  Khong co don nao can xu ly. Ket thuc.")
        return

    # Buoc 3: Du doan tung don
    print("\nBuoc 3: Chay du doan...")
    print("-" * 55)

    results = []
    for app in pending:
        start_time = time.time()

        # Goi model du doan
        approved, probability = model.predict(
            age              = app["age"],
            income           = app["income"],
            credit_score     = app["credit_score"],
            loan_amount      = app["loan_amount"],
            loan_term_months = app["loan_term"],
        )

        latency_ms = (time.time() - start_time) * 1000

        # Luu ket qua vao bang predictions
        prediction_id = db.insert_prediction(
            application_id = app["application_id"],
            model_version  = LoanModel.VERSION,
            approved       = approved,
            probability    = probability,
            latency_ms     = round(latency_ms, 2),
        )

        # Cap nhat trang thai don vay
        new_status = "approved" if approved else "rejected"
        db.update_application_status(app["application_id"], new_status)

        results.append({
            "customer"     : app["customer_name"],
            "credit_score" : app["credit_score"],
            "loan_amount"  : app["loan_amount"],
            "approved"     : approved,
            "probability"  : probability,
            "latency_ms"   : latency_ms,
        })

        # In ket qua tung don
        ket_qua = "DUYET" if approved else "TU CHOI"
        print(f"  Don #{app['application_id']} | {app['customer_name']:<20}"
              f" | {ket_qua:<8} | {probability:.0%} | {latency_ms:.1f}ms")

    # Buoc 4: In bao cao tong ket
    print("-" * 55)
    print("\nBuoc 4: Bao cao tong ket")
    print("-" * 55)

    total     = len(results)
    approved  = sum(1 for r in results if r["approved"])
    rejected  = total - approved
    avg_prob  = sum(r["probability"] for r in results) / total
    avg_lat   = sum(r["latency_ms"] for r in results) / total

    print(f"  Tong so don xu ly : {total}")
    print(f"  So don duoc duyet : {approved} ({approved/total:.0%})")
    print(f"  So don bi tu choi : {rejected} ({rejected/total:.0%})")
    print(f"  Xac suat trung binh: {avg_prob:.2%}")
    print(f"  Latency trung binh : {avg_lat:.1f}ms")

    # Buoc 5: Hieu suat model tu du lieu thuc te
    print("\nBuoc 5: Hieu suat model tren du lieu thuc te")
    print("-" * 55)
    perf = db.get_model_performance(LoanModel.VERSION)
    if perf:
        print(f"  Phien ban        : {perf['model_version']}")
        print(f"  Tong du doan     : {perf['total_predictions']}")
        print(f"  Ti le duyet      : {perf['approval_rate']}%")
        print(f"  Xac suat TB      : {perf['avg_probability']:.4f}")
        print(f"  Latency TB       : {perf['avg_latency_ms']}ms")

    print("\nPipeline hoan thanh!")
    print("=" * 55)


if __name__ == "__main__":
    run_prediction_pipeline()
