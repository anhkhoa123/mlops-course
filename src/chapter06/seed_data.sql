-- ============================================================
-- Du lieu mau de thuc hanh cac cau query
-- ============================================================

-- Xoa du lieu cu truoc khi them moi
DELETE FROM model_metrics;
DELETE FROM predictions;
DELETE FROM loan_applications;
DELETE FROM customers;

-- Reset auto increment ve 1
DELETE FROM sqlite_sequence;

-- ============================================================
-- Them khach hang
-- ============================================================
INSERT INTO customers (name, age, income, credit_score) VALUES
    ('Nguyen Van An',   35, 45000000, 750),
    ('Tran Thi Binh',   28, 25000000, 620),
    ('Le Van Cuong',    42, 80000000, 800),
    ('Pham Thi Dung',   31, 32000000, 580),
    ('Hoang Van Em',    55, 60000000, 720),
    ('Nguyen Thi Phuong', 26, 18000000, 540),
    ('Tran Van Giang',  48, 95000000, 810),
    ('Le Thi Huong',    33, 38000000, 690),
    ('Pham Van Ky',     29, 22000000, 560),
    ('Do Thi Lan',      44, 55000000, 740);

-- ============================================================
-- Them don xin vay
-- ============================================================
INSERT INTO loan_applications (customer_id, loan_amount, loan_term, purpose, status) VALUES
    (1, 200000000, 24, 'mua_xe',      'approved'),
    (1, 500000000, 60, 'mua_nha',     'pending'),
    (2, 50000000,  12, 'tieu_dung',   'approved'),
    (3, 800000000, 120,'mua_nha',     'approved'),
    (4, 30000000,  6,  'tieu_dung',   'rejected'),
    (5, 150000000, 36, 'kinh_doanh',  'approved'),
    (6, 20000000,  12, 'tieu_dung',   'rejected'),
    (7, 1000000000,120,'mua_nha',     'approved'),
    (8, 100000000, 24, 'kinh_doanh',  'pending'),
    (9, 40000000,  18, 'mua_xe',      'rejected'),
    (10,250000000, 60, 'mua_nha',     'approved'),
    (2, 80000000,  24, 'kinh_doanh',  'pending');

-- ============================================================
-- Them ket qua du doan
-- ============================================================
INSERT INTO predictions (application_id, model_version, approved, probability, latency_ms) VALUES
    (1,  'v1.0.0', 1, 0.87, 12.3),
    (2,  'v1.0.0', 0, 0.45, 11.8),
    (3,  'v1.0.0', 1, 0.72, 13.1),
    (4,  'v1.0.0', 1, 0.91, 10.9),
    (5,  'v1.0.0', 0, 0.23, 12.5),
    (6,  'v1.0.0', 1, 0.81, 11.2),
    (7,  'v1.0.0', 0, 0.31, 14.0),
    (8,  'v1.0.0', 1, 0.95, 10.5),
    (9,  'v1.0.0', 0, 0.42, 13.8),
    (10, 'v1.0.0', 0, 0.38, 12.1),
    (11, 'v1.0.0', 1, 0.78, 11.5),
    (12, 'v1.0.0', 0, 0.55, 12.9),
    -- Model v2.0.0 du doan lai mot so don
    (1,  'v2.0.0', 1, 0.92, 8.1),
    (3,  'v2.0.0', 1, 0.79, 7.9),
    (5,  'v2.0.0', 0, 0.18, 8.5),
    (7,  'v2.0.0', 0, 0.25, 8.3);

-- ============================================================
-- Them chi so model
-- ============================================================
INSERT INTO model_metrics
    (model_version, accuracy, precision_score, recall_score, f1_score, training_samples)
VALUES
    ('v1.0.0', 0.8750, 0.8820, 0.8710, 0.8765, 8000),
    ('v2.0.0', 0.9150, 0.9200, 0.9080, 0.9140, 12000);
