#!/bin/bash

# Project Name
PROJECT_NAME="arthasetu_api"

echo "🚀 Initializing $PROJECT_NAME..."

# 1. Create Directory Structure
mkdir -p $PROJECT_NAME/{core,api/{services,routes,schemas},templates,static,middleware}
cd $PROJECT_NAME

# 2. Initialize Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Core Dependencies
pip install django django-ninja psycopg2-binary sentence-transformers requests python-dotenv django-cors-headers gunicorn

# 4. Generate Requirements.txt
pip freeze > requirements.txt

# 5. Create .env template
cat <<EOF > .env
DEBUG=True
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
DATABASE_URL=postgres://user:password@host:port/dbname
MODAL_LLM_URL=https://your-modal-endpoint.modal.run
EOF

# 6. Initialize Django Project
django-admin startproject core .

# 7. Create custom project files
# --- api/schemas/query.py ---
cat <<EOF > api/schemas/query.py
from ninja import Schema
from typing import List, Optional

class QueryRequest(Schema):
    query: str
    top_k: int = 5

class SourceContext(Schema):
    content: str
    doc_level: str
    metadata: Optional[dict] = None

class QueryResponse(Schema):
    answer: str
    sources: List[SourceContext]
EOF

# --- api/services/vector_service.py ---
cat <<EOF > api/services/vector_service.py
import os
import psycopg2
from sentence_transformers import SentenceTransformer

class VectorService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.db_url = os.getenv("DATABASE_URL")

    def find_context(self, query: str, limit: int = 5):
        embedding = self.model.encode(query).tolist()
        conn = psycopg2.connect(self.db_url)
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT content, doc_level 
                    FROM knowledge_base 
                    ORDER BY embedding <=> %s::vector 
                    LIMIT %s
                """, (embedding, limit))
                return [{"content": r[0], "doc_level": r[1]} for r in cur.fetchall()]
        finally:
            conn.close()
EOF

# --- api/services/llm_service.py ---
cat <<EOF > api/services/llm_service.py
import os
import requests

class LLMService:
    def __init__(self):
        self.endpoint = os.getenv("MODAL_LLM_URL")

    def get_reasoning(self, query: str, context: str):
        prompt = f"System: Use context to answer. Context: {context}\nUser: {query}"
        response = requests.post(self.endpoint, json={"prompt": prompt})
        return response.json().get("answer", "Error connecting to LLM")
EOF

# --- api/routes/v1.py ---
cat <<EOF > api/routes/v1.py
from ninja import Router
from api.schemas.query import QueryRequest, QueryResponse
from api.services.vector_service import VectorService
from api.services.llm_service import LLMService

router = Router()
vector_svc = VectorService()
llm_svc = LLMService()

@router.post("/ask", response=QueryResponse)
def ask(request, payload: QueryRequest):
    sources = vector_svc.find_context(payload.query, limit=payload.top_k)
    context_str = "\n".join([s['content'] for s in sources])
    answer = llm_svc.get_reasoning(payload.query, context_str)
    
    return {"answer": answer, "sources": sources}
EOF

# --- api/api_main.py ---
cat <<EOF > api/api_main.py
from ninja import NinjaAPI
from api.routes.v1 import router as v1_router

api = NinjaAPI(title="ArthaSetu API", version="1.0.0")
api.add_router("/v1/", v1_router)
EOF

echo "✅ Project scaffolded! Run 'python manage.py runserver' after configuring DATABASE_URL."
