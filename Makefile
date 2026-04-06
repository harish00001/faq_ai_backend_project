.PHONY: install run test lint init

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest -q

init:
	python scripts/init_db.py
