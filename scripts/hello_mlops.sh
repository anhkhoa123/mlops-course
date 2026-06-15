#!/bin/bash

# Script kiem tra moi truong MLOps
# Tac gia: Khoa
# Ngay tao: 2024-06-14

echo "=============================="
echo " Kiem tra moi truong MLOps"
echo "=============================="

echo ""
echo "Thong tin he thong:"
echo "  He dieu hanh : $(uname -s)"
echo "  Ten may      : $(hostname)"
echo "  User hien tai: $(whoami)"
echo "  Thu muc hien tai: $(pwd)"

echo ""
echo "Phien ban cong cu:"
echo "  Python: $(python3 --version)"
echo "  Git   : $(git --version)"
echo "  pip   : $(pip --version)"

echo ""
echo "Kiem tra xong!"
