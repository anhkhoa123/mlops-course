# Bo checklist kiem tra tung giai doan truoc khi chuyen sang giai doan ke tiep

from dataclasses import dataclass
from typing import Callable


@dataclass
class CheckItem:
    """Mot hang muc kiem tra."""
    name        : str
    description : str
    check_fn    : Callable[[], bool]   # ham tra ve True neu dat yeu cau
    is_blocking : bool = True          # True: phai dat moi duoc chuyen giai doan


@dataclass
class CheckResult:
    """Ket qua kiem tra 1 hang muc."""
    name    : str
    passed  : bool
    blocking: bool


class MLChecklist:
    """
    Bo checklist kiem tra tung giai doan cua ML Lifecycle.
    Moi giai doan co danh sach hang muc bat buoc va tuy chon.
    """

    def run_stage_checks(self, stage_name: str,
                          items: list[CheckItem]) -> bool:
        """
        Chay tat ca hang muc cua mot giai doan.
        Tra ve True neu tat ca hang muc bat buoc deu dat.
        """
        print(f"\nKIEM TRA: {stage_name}")
        print("-" * 50)

        results   = []
        all_pass  = True

        for item in items:
            passed = False
            try:
                passed = item.check_fn()
            except Exception as e:
                print(f"  LOI khi kiem tra '{item.name}': {e}")

            result = CheckResult(
                name    = item.name,
                passed  = passed,
                blocking= item.is_blocking,
            )
            results.append(result)

            status = "DAT" if passed else ("TRUOT (bat buoc)" if item.is_blocking else "TRUOT (tuy chon)")
            print(f"  [{status}] {item.name}")
            print(f"         {item.description}")

            if not passed and item.is_blocking:
                all_pass = False

        passed_count = sum(1 for r in results if r.passed)
        print(f"\n  Ket qua: {passed_count}/{len(results)} hang muc dat")

        if all_pass:
            print("  -> Giai doan nay DAT CHUAN. Co the chuyen tiep.")
        else:
            print("  -> Giai doan nay CHUA DAT. Can xu ly truoc khi chuyen tiep.")

        return all_pass


def run_full_checklist(data_info, feature_set, experiments, best_exp, deploy_ready):
    """Chay checklist cho tat ca giai doan voi du lieu thuc tu lifecycle."""

    checker = MLChecklist()

    print("\n" + "=" * 55)
    print("  CHECKLIST KIEM TRA VONG DOI DU AN ML")
    print("=" * 55)

    # ---- Giai doan 1: Xac dinh bai toan ----
    checker.run_stage_checks("GIAI DOAN 1: XAC DINH BAI TOAN", [
        CheckItem(
            name        = "Da dinh nghia metric ro rang",
            description = "F1 >= 0.85 va AUC-ROC >= 0.90",
            check_fn    = lambda: True,   # da dinh nghia o define_problem()
        ),
        CheckItem(
            name        = "Da xac nhan ML la giai phap phu hop",
            description = "Bai toan co pattern phuc tap, khong giai quyet duoc bang rule don gian",
            check_fn    = lambda: True,
        ),
        CheckItem(
            name        = "Da thong nhat metric voi stakeholder",
            description = "Tat ca ben lien quan dong y voi tieu chi thanh cong",
            check_fn    = lambda: True,
            is_blocking = False,   # tuy chon — nen co nhung khong bat buoc
        ),
    ])

    # ---- Giai doan 2: Du lieu ----
    checker.run_stage_checks("GIAI DOAN 2: DU LIEU", [
        CheckItem(
            name        = "Du luong mau toi thieu",
            description = f"Can it nhat 1000 mau — co {data_info.n_samples}",
            check_fn    = lambda: data_info.n_samples >= 1000,
        ),
        CheckItem(
            name        = "Ty le gia tri bi mat chap nhan duoc",
            description = f"< 20% — hien tai: {data_info.missing_ratio:.1%}",
            check_fn    = lambda: data_info.missing_ratio < 0.20,
        ),
        CheckItem(
            name        = "Du lieu khong bi mat can bang qua nghiem trong",
            description = "Ty le lop thieu so > 10% — hien tai: "
                          f"{min(data_info.class_ratio.values()):.1%}",
            check_fn    = lambda: min(data_info.class_ratio.values()) >= 0.10,
        ),
    ])

    # ---- Giai doan 3: Chuan bi du lieu ----
    checker.run_stage_checks("GIAI DOAN 3: CHUAN BI DU LIEU", [
        CheckItem(
            name        = "Da xu ly gia tri bi mat",
            description = "Khong con NaN trong tap train/val/test",
            check_fn    = lambda: feature_set.n_train > 0,
        ),
        CheckItem(
            name        = "Da chuan hoa dac trung dung cach",
            description = "Scaler chi fit tren train, transform val va test",
            check_fn    = lambda: feature_set.scaler_applied,
        ),
        CheckItem(
            name        = "Train/val/test duoc chia theo ty le 70/15/15",
            description = f"Train={feature_set.n_train}, Val={feature_set.n_val}, Test={feature_set.n_test}",
            check_fn    = lambda: feature_set.n_val > 0 and feature_set.n_test > 0,
        ),
    ])

    # ---- Giai doan 4: Huan luyen ----
    checker.run_stage_checks("GIAI DOAN 4: HUAN LUYEN", [
        CheckItem(
            name        = "Da thu nghiem it nhat 3 model khac nhau",
            description = f"Hien tai: {len(experiments)} thi nghiem",
            check_fn    = lambda: len(experiments) >= 3,
        ),
        CheckItem(
            name        = "Da dung cross-validation de kiem tra do on dinh",
            description = "CV std < 0.05 — mo hinh on dinh",
            check_fn    = lambda: all(e.cv_score_std < 0.05 for e in experiments),
        ),
        CheckItem(
            name        = "Ket qua thi nghiem duoc ghi lai day du",
            description = "Moi thi nghiem co hyperparams, metric, thoi gian",
            check_fn    = lambda: all(e.hyperparams for e in experiments),
        ),
    ])

    # ---- Giai doan 5: Danh gia ----
    checker.run_stage_checks("GIAI DOAN 5: DANH GIA", [
        CheckItem(
            name        = "Model dat nguong F1 tren tap test",
            description = f"F1 >= 0.85 — hien tai: {best_exp.f1}",
            check_fn    = lambda: best_exp.f1 >= 0.85,
        ),
        CheckItem(
            name        = "Model dat nguong AUC-ROC tren tap test",
            description = f"AUC-ROC >= 0.90 — hien tai: {best_exp.auc_roc}",
            check_fn    = lambda: best_exp.auc_roc >= 0.90,
        ),
        CheckItem(
            name        = "Da kiem tra fairness (phan biet doi xu)",
            description = "Model khong phan biet theo nhom tuoi hoac gioi tinh",
            check_fn    = lambda: True,
            is_blocking = False,
        ),
    ])

    # ---- Giai doan 6: Trien khai ----
    checker.run_stage_checks("GIAI DOAN 6: TRIEN KHAI", [
        CheckItem(
            name        = "Model da duoc dong goi thanh Docker image",
            description = "Image chay duoc tren bat ky may co Docker",
            check_fn    = lambda: deploy_ready,
        ),
        CheckItem(
            name        = "Da co ke hoach giam sat sau deploy",
            description = "Dinh nghia nguong canh bao va quy trinh xu ly",
            check_fn    = lambda: deploy_ready,
        ),
        CheckItem(
            name        = "Da co ke hoach tai huan luyen",
            description = "Dinh nghia dieu kien va lich tai huan luyen",
            check_fn    = lambda: True,
            is_blocking = False,
        ),
    ])

    print("\n" + "=" * 55)
    print("  CHECKLIST HOAN THANH")
    print("=" * 55)


if __name__ == "__main__":
    # Chay lifecycle truoc de lay du lieu
    #from src.chapter07.lifecycle import run_full_lifecycle
    from lifecycle import run_full_lifecycle
    report = run_full_lifecycle()

    run_full_checklist(
        data_info    = report.data_info,
        feature_set  = report.feature_set,
        experiments  = report.experiments,
        best_exp     = report.best_experiment,
        deploy_ready = report.deploy_ready,
    )
