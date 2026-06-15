#!/bin/bash

# ============================================================
# cleanup.sh
# Don dep file tam va cache sau moi lan chay pipeline
# Su dung: ./scripts/cleanup.sh [--all]
# Tham so --all: xoa ca logs va models (dung can than)
# ============================================================

echo "Bat dau don dep..."

# Dem so file truoc khi xoa
count_before=$(find . -name "__pycache__" -o -name "*.pyc" \
               -o -name ".ipynb_checkpoints" 2>/dev/null | wc -l)

# Xoa cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
echo "  Da xoa: Python cache (__pycache__, *.pyc)"

# Xoa checkpoint cua Jupyter
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
echo "  Da xoa: Jupyter checkpoints"

# Xoa file temp
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.temp" -delete 2>/dev/null || true
echo "  Da xoa: File tam (*.tmp, *.temp)"

# Neu co tham so --all, xoa ca logs va models cu
if [ "$1" = "--all" ]; then
    echo ""
    echo "Che do --all: xoa logs va models cu..."

    # Giu lai 5 file log moi nhat, xoa phần còn lại
    ls -t logs/*.log 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    echo "  Da xoa: Log cu (giu lai 5 log moi nhat)"

    rm -rf models/*.pkl models/*.joblib 2>/dev/null || true
    echo "  Da xoa: Model cu trong models/"
fi

echo ""
echo "Don dep hoan tat!"
