# VIROC: Vehicle Identification OCR

Requirements:
- uv
- docker

## Installation

Install uv with standalone installers:

```
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Running

```
# Download and export the YOLOv5 model to onnx
uv run scripts/export_yolo.py

# Download dataset (optional to run notebooks)
# requires setting up kaggle auth (see https://www.kaggle.com/docs/api)
uv run python -c 'from viroc.dataset import download; download()'

# Start containers
docker compose up -d

# Run test request
uv run just test
```
