#!/bin/bash

# Khai bao bien — khong co khoang trang hai ben dau =
PROJECT_NAME="mlops-course"
VERSION="1.0.0"
NUM_EPOCHS=50

# Truy cap bien bang dau $
echo "Du an  : $PROJECT_NAME"
echo "Phien ban: $VERSION"
echo "So epoch : $NUM_EPOCHS"

# Bien dac biet cua Bash
echo "Ten script  : $0"        # ten file script
echo "Tham so thu 1: $1"       # tham so truyen vao khi chay
echo "So tham so  : $#"        # tong so tham so
