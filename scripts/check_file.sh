#!/bin/bash

# Nhan duong dan file tu tham so thu nhat
FILE_PATH=$1

# Kiem tra co truyen tham so vao khong
if [ -z "$FILE_PATH" ]; then
    echo "Loi: Chua truyen duong dan file"
    echo "Cach dung: ./check_file.sh "
    exit 1   # thoat voi ma loi
fi

# Kiem tra file co ton tai khong
if [ -f "$FILE_PATH" ]; then
    echo "File ton tai: $FILE_PATH"
    echo "Kich thuoc : $(wc -l < $FILE_PATH) dong"
else
    echo "Khong tim thay file: $FILE_PATH"
    exit 1
fi

echo "Kiem tra hoan tat."
