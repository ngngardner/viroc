default:
    just --list

doc:
    typst watch docs/main.typ

dev:
    uv run fastapi dev --port 8995 src/viroc/app.py

local:
    docker compose up

test:
    echo "Ground Truth - 皖A·XH350"
    curl -X POST http://localhost:8995/predict \
        -F "file=@test/sample_image.jpg"
