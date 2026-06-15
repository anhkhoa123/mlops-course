#!/bin/bash

# ============================================================
# train_pipeline.sh
# Chay toan bo pipeline ML theo thu tu
# Su dung: ./scripts/train_pipeline.sh
# ============================================================

# "set -e": dung script ngay neu bat ky lenh nao tra ve loi
# Khong co dong nay, script tiep tuc chay du buoc truoc that bai
set -e

# ---- Cau hinh ----
LOG_FILE="logs/training_$(date '+%Y%m%d_%H%M%S').log"
PYTHON="python3"

# Tao thu muc logs neu chua co
mkdir -p logs

# Ham ghi log — in ra man hinh va ghi vao file cung luc
log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$message"
    echo "$message" >> "$LOG_FILE"
}

# Ham chay buoc pipeline voi logging tu dong
run_step() {
    local step_name=$1
    local command=$2

    log "BAT DAU: $step_name"
    eval "$command"
    log "HOAN THANH: $step_name"
    echo "--------------------------------------------"
}

# ---- Bat dau pipeline ----
log "=========================================="
log "BAT DAU PIPELINE HUAN LUYEN"
log "Log file: $LOG_FILE"
log "=========================================="

run_step "Kiem tra moi truong" \
    "$PYTHON -c 'import numpy, pandas, sklearn; print(\"Thu vien OK\")'"

run_step "Chuan bi du lieu" \
    "$PYTHON src/prepare_data.py"

run_step "Huan luyen mo hinh" \
    "$PYTHON src/train.py"

run_step "Danh gia mo hinh" \
    "$PYTHON src/evaluate.py"

log "=========================================="
log "PIPELINE CHAY THANH CONG"
log "Xem log day du tai: $LOG_FILE"
log "=========================================="
