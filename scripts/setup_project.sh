#!/bin/bash

# ============================================================
# setup_project.sh
# Tu dong tao cau truc thu muc chuan cho du an MLOps moi
# Su dung: ./scripts/setup_project.sh 
# ============================================================

PROJECT_NAME=$1

# Kiem tra co truyen ten du an khong
if [ -z "$PROJECT_NAME" ]; then
    echo "Loi: Chua truyen ten du an"
    echo "Su dung: ./scripts/setup_project.sh "
    exit 1
fi

# Kiem tra thu muc da ton tai chua
if [ -d "$PROJECT_NAME" ]; then
    echo "Loi: Thu muc '$PROJECT_NAME' da ton tai"
    exit 1
fi

echo "Dang tao du an: $PROJECT_NAME"

# Tao cau truc thu muc
mkdir -p "$PROJECT_NAME"/{data/{raw,processed,features},notebooks,src,scripts,logs,models}

# Tao file .gitignore
cat > "$PROJECT_NAME/.gitignore" << 'GITIGNORE'
venv/
.venv/
__pycache__/
*.pyc
*.pkl
*.joblib
data/raw/
data/processed/
.env
mlruns/
mlartifacts/
.ipynb_checkpoints/
logs/
models/
.DS_Store
GITIGNORE

# Tao file README.md
cat > "$PROJECT_NAME/README.md" << README
# $PROJECT_NAME

Mo ta du an cua ban o day.

## Cau truc thu muc
- data/      : du lieu (raw, processed, features)
- notebooks/ : Jupyter Notebook phan tich
- src/       : ma nguon chinh
- scripts/   : bash script tien ich
- logs/      : file log
- models/    : model da huan luyen
README

# Tao file requirements.txt ban dau
cat > "$PROJECT_NAME/requirements.txt" << 'REQUIREMENTS'
numpy==1.26.4
pandas==2.2.1
scikit-learn==1.4.2
python-dotenv==1.0.1
REQUIREMENTS

# Tao file .env mau
cat > "$PROJECT_NAME/.env.example" << 'ENV'
# Sao chep file nay thanh .env va dien gia tri that
MODEL_VERSION=v1.0.0
DATA_PATH=./data
LOG_LEVEL=INFO
ENV

# Khoi tao Git repo
cd "$PROJECT_NAME"
git init
git add .
git commit -m "Khoi tao du an $PROJECT_NAME bang setup_project.sh"
cd ..

echo ""
echo "Tao du an thanh cong: $PROJECT_NAME"
echo "Cac buoc tiep theo:"
echo "  cd $PROJECT_NAME"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
