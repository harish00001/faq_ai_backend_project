# FAQ AI Backend

Production-style FastAPI backend for FAQ training and semantic search using local embeddings and FAISS.

## Features
- FastAPI project structure
- SQLite + SQLAlchemy for FAQ storage
- SentenceTransformer embeddings
- FAISS vector index for semantic search
- Health, train, list, search, and delete APIs
- Automatic index rebuild on data change
- Structured logging and centralized settings
- Docker support
- Basic tests

## Tech Stack
- FastAPI
- SQLAlchemy
- SQLite
- Sentence Transformers (`BAAI/bge-small-en-v1.5`)
- FAISS
- Pytest

## Project Structure
```bash
faq_ai_backend_project/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
├── scripts/
├── tests/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## Quick Start
### 1) Create environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2) Run
```bash
uvicorn app.main:app --reload
```

### 3) Open docs
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Overview
### Health
```http
GET /health
```

### Train one FAQ
```http
POST /api/v1/faqs
Content-Type: application/json

{
  "question": "How do I reset my password?",
  "answer": "Go to settings, click reset password, then follow the email link.",
  "category": "account",
  "tags": ["password", "login"]
}
```

### Bulk train FAQs
```http
POST /api/v1/faqs/bulk
Content-Type: application/json

{
  "items": [
    {
      "question": "How do I update my email?",
      "answer": "Open your profile page and change the email field.",
      "category": "account",
      "tags": ["email", "profile"]
    }
  ]
}
```

### Semantic search
```http
POST /api/v1/faqs/search
Content-Type: application/json

{
  "query": "I forgot my password",
  "top_k": 3
}
```

### List FAQs
```http
GET /api/v1/faqs?skip=0&limit=20
```

### Delete FAQ
```http
DELETE /api/v1/faqs/{faq_id}
```

## Notes
- The first request may take longer while the embedding model downloads.
- For a larger production deployment, move from SQLite to PostgreSQL and move index rebuilds to background jobs.
- This starter keeps correctness simple by rebuilding the full FAISS index after create/update/delete operations.

## Run tests
```bash
pytest -q
```
# faq_ai_backend_project
