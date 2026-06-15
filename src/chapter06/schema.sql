-- ============================================================
-- Schema cho he thong MLOps quan ly vay von
-- Ky hieu "--" la comment trong SQL
-- ============================================================

-- Xoa bang cu neu ton tai (thu tu xoa nguoc lai thu tu tao
-- vi rang buoc foreign key)
DROP TABLE IF EXISTS model_metrics;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS loan_applications;
DROP TABLE IF EXISTS customers;

-- ============================================================
-- Bang 1: Khach hang
-- ============================================================
CREATE TABLE customers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    -- AUTOINCREMENT: SQLite tu dong tang id, khong can truyen vao
    name          TEXT    NOT NULL,
    age           INTEGER NOT NULL CHECK (age >= 18 AND age <= 100),
    -- CHECK: rang buoc du lieu ngay tai database
    income        REAL    NOT NULL CHECK (income > 0),
    credit_score  INTEGER NOT NULL CHECK (credit_score BETWEEN 300 AND 850),
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
    -- DEFAULT: gia tri mac dinh neu khong truyen vao
    -- datetime('now'): ham SQLite tra ve thoi gian hien tai
);

-- ============================================================
-- Bang 2: Don xin vay
-- ============================================================
CREATE TABLE loan_applications (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id   INTEGER NOT NULL,
    loan_amount   REAL    NOT NULL CHECK (loan_amount > 0),
    loan_term     INTEGER NOT NULL CHECK (loan_term BETWEEN 1 AND 360),
    purpose       TEXT    NOT NULL,
    -- Muc dich vay: mua_nha, mua_xe, kinh_doanh, tieu_dung
    status        TEXT    NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending', 'approved', 'rejected')),
    applied_at    TEXT    NOT NULL DEFAULT (datetime('now')),

    -- Foreign key: dam bao customer_id phai ton tai trong bang customers
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- ============================================================
-- Bang 3: Ket qua du doan cua model
-- ============================================================
CREATE TABLE predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id  INTEGER NOT NULL,
    model_version   TEXT    NOT NULL,
    approved        INTEGER NOT NULL CHECK (approved IN (0, 1)),
    -- SQLite khong co kieu BOOLEAN, dung INTEGER 0/1
    probability     REAL    NOT NULL CHECK (probability BETWEEN 0.0 AND 1.0),
    latency_ms      REAL,
    -- Thoi gian xu ly — co the NULL neu khong do
    predicted_at    TEXT    NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (application_id) REFERENCES loan_applications (id)
);

-- ============================================================
-- Bang 4: Chi so danh gia tung phien ban model
-- ============================================================
CREATE TABLE model_metrics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    model_version   TEXT    NOT NULL UNIQUE,
    -- UNIQUE: moi phien ban model chi co 1 bo chi so
    accuracy        REAL    NOT NULL,
    precision_score REAL    NOT NULL,
    recall_score    REAL    NOT NULL,
    f1_score        REAL    NOT NULL,
    training_samples INTEGER NOT NULL,
    evaluated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ============================================================
-- Index: tang toc truy van thuong xuyen
-- Khong co index -> SQLite doc toan bo bang de tim
-- Co index -> tim nhanh nhu tim trong muc luc sach
-- ============================================================
CREATE INDEX idx_applications_customer
    ON loan_applications (customer_id);

CREATE INDEX idx_predictions_application
    ON predictions (application_id);

CREATE INDEX idx_predictions_model_version
    ON predictions (model_version);
