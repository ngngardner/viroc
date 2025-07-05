FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
COPY uv.lock /app/
COPY README.md /app/
COPY src/ /app/src/
WORKDIR /app
RUN uv sync

# Pre-load the GOT-OCR model during build to avoid downloading at runtime
RUN uv run python -c "from transformers import AutoModelForImageTextToText, AutoProcessor; AutoModelForImageTextToText.from_pretrained('stepfun-ai/GOT-OCR-2.0-hf', device_map='cpu'); AutoProcessor.from_pretrained('stepfun-ai/GOT-OCR-2.0-hf', use_fast=True)"

# Set environment variable for Triton server URL
ENV TRITON_SERVER_URL=triton:8991

EXPOSE 8995

CMD ["uv", "run", "python", "-m", "viroc"]
