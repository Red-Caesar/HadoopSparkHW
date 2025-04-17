#!/bin/bash
DATA_DIR="./data"
ZIP_URL="https://www.kaggle.com/api/v1/datasets/download/devdope/900k-spotify"
ZIP_FILE="${DATA_DIR}/900k-spotify.zip"
TARGET_FILE="spotify_dataset.csv"
OUTPUT_FILE="${DATA_DIR}/${TARGET_FILE}"

mkdir -p "${DATA_DIR}"

if [ -f "${OUTPUT_FILE}" ]; then
    echo "File already exists: ${OUTPUT_FILE}"
    echo "Skipping download and extraction."
    exit 0
fi

if [ -f "${ZIP_FILE}" ]; then
    echo "ZIP file already exists: ${ZIP_FILE}"
else
    echo "Downloading dataset..."
    curl -L -o "${ZIP_FILE}" "${ZIP_URL}" || {
        echo "Error: Failed to download file"
        exit 1
    }
fi

echo "Extracting and processing archive..."
unzip -p "${ZIP_FILE}" "${TARGET_FILE}" > "${OUTPUT_FILE}" || {
    echo "Error: Failed to extract target file from archive"
    exit 1
}

rm "${ZIP_FILE}"
echo "Successfully processed dataset. Output file: ${OUTPUT_FILE}"
