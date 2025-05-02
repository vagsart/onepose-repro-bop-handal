#!/bin/bash


DATASET_ROOT_ONBOARD="path/to/bop/datasets//handal/static"
DATASET_ROOT_TEST="path/to/bop/datasets/handal/val"
MODEL_ROOT="path/to/bop/datasets/handal/models_eval"
OUTPUT_ROOT_ONBOARD="path/to/output/onboarding"
OUTPUT_ROOT_TEST="path/to/output/test"


# Onboardings

# Loop through all folders in DATASET_ROOT_ONBOARD
for folder in "$DATASET_ROOT_ONBOARD"/*/; do
    folder_name=$(basename "$folder")

    if [[ "$folder_name" == *down* ]]; then
        echo "Skipping folder $folder_name"
        continue
    fi

    echo "Processing folder $folder_name"
    python src/parse_onboarding.py --dataset_root "$DATASET_ROOT_ONBOARD" --folder_name "$folder_name" --model_root "$MODEL_ROOT" --output_root "$OUTPUT_ROOT_ONBOARD"

done
# 

# Tests
echo "Processing folder 000001"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000001 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000002"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000002 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000003"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000003 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000004"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000004 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000005"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000005 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000006"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000006 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000007"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000007 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000008"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000008 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000009"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000009 --output_root "$OUTPUT_ROOT_TEST"

echo "Processing folder 000010"
python src/parse_test.py --dataset_root "$DATASET_ROOT_TEST" --folder_name 000010 --output_root "$OUTPUT_ROOT_TEST"
