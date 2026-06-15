#!/bin/bash

# Lap qua danh sach cac buoc trong pipeline
echo "Cac buoc trong pipeline ML:"
STEPS="load_data preprocess feature_engineering train evaluate"

for step in $STEPS; do
    echo "  Dang chay buoc: $step ..."
    sleep 0.3   # gia lap thoi gian xu ly
    echo "  Hoan thanh: $step"
done

echo ""
echo "Toan bo pipeline chay xong!"

# Lap qua file trong thu muc
echo ""
echo "Cac file Python trong du an:"
for file in src/**/*.py; do
    echo "  $file"
done
