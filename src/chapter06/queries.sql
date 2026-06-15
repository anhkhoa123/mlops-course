-- ============================================================
-- queries.sql
-- Tap hop cac cau query thuong dung trong du an MLOps vay von
-- Chay: sqlite3 -header -column data/db/mlops.db < src/chapter06/queries.sql
-- ============================================================

.headers on
.mode column

-- ============================================================
-- Query 1: Tong quan du lieu
-- ============================================================
SELECT '=== TONG QUAN DU LIEU ===' AS section;

SELECT
    (SELECT COUNT(*) FROM customers)         AS so_khach_hang,
    (SELECT COUNT(*) FROM loan_applications) AS so_don_vay,
    (SELECT COUNT(*) FROM predictions)       AS so_du_doan,
    (SELECT COUNT(*) FROM model_metrics)     AS so_phien_ban_model;

-- ============================================================
-- Query 2: Danh sach don cho xu ly (pending)
-- Su dung hang ngay de biet don nao can duyet
-- ============================================================
SELECT '=== DON DANG CHO XU LY ===' AS section;

SELECT
    la.id               AS don_id,
    c.name              AS khach_hang,
    c.credit_score,
    la.loan_amount,
    la.purpose,
    la.applied_at
FROM loan_applications la
INNER JOIN customers c ON la.customer_id = c.id
WHERE la.status = 'pending'
ORDER BY la.applied_at;

-- ============================================================
-- Query 3: Hieu suat model theo thoi gian
-- Dung trong dashboard monitoring
-- ============================================================
SELECT '=== HIEU SUAT TUNG PHIEN BAN MODEL ===' AS section;

SELECT
    mm.model_version,
    mm.accuracy,
    mm.f1_score,
    mm.training_samples,
    COUNT(p.id)                                     AS so_lan_du_doan,
    ROUND(AVG(p.latency_ms), 2)                     AS latency_tb_ms,
    mm.evaluated_at
FROM model_metrics mm
LEFT JOIN predictions p ON mm.model_version = p.model_version
GROUP BY mm.model_version
ORDER BY mm.evaluated_at;

-- ============================================================
-- Query 4: Khach hang co nhieu don nhat
-- ============================================================
SELECT '=== KHACH HANG CO NHIEU DON VAY NHAT ===' AS section;

SELECT
    c.name,
    c.credit_score,
    COUNT(la.id)                AS so_don,
    SUM(la.loan_amount)         AS tong_so_tien_vay,
    GROUP_CONCAT(la.purpose)    AS cac_muc_dich
FROM customers c
INNER JOIN loan_applications la ON c.id = la.customer_id
GROUP BY c.id
HAVING so_don > 1
ORDER BY so_don DESC;
