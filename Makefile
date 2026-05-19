.PHONY: install up down logs test lint format seed run-once init-neo4j init-qdrant backend frontend

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

up:
	cd infra && docker compose up -d

down:
	cd infra && docker compose down

logs:
	cd infra && docker compose logs -f

test:
	pytest tests -v

lint:
	ruff check .

format:
	ruff format .

seed:
	python scripts/seed_sample_data.py

run-once:
	python scripts/run_pipeline_once.py

init-neo4j:
	python scripts/init_neo4j.py

init-qdrant:
	python scripts/init_qdrant.py

backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev
