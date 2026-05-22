import modal
from pydantic import BaseModel
from typing import List, Optional
import os

rag_image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "langchain",
        "langchain-community",
        "langchain-groq",
        "langchain-google-genai",
        "faiss-cpu",
        "sentence-transformers",
        "model2vec",
        "fastapi",
        "pydantic",
        "python-dotenv"
    )
    .add_local_dir("src", remote_path="/root/src")
    .add_local_file(".env", remote_path="/root/.env")
)

vol = modal.Volume.from_name("rag-storage", create_if_missing=True)
app = modal.App("hukumonline-rag")

class QueryRequest(BaseModel):
    query: str

class Reference(BaseModel):
    title: str
    url: str
    publish_date: str
    theme: str

class QueryResponse(BaseModel):
    original_query: str
    reformulated_query: str
    answer: str
    references: List[Reference]

@app.cls(
    image=rag_image, 
    secrets=[
        modal.Secret.from_name("my-google-secret"),
        modal.Secret.from_name("my-groq-secret")
    ], 
    volumes={"/data": vol},
    min_containers=1
)
class Model:
    def __init__(self):
        self.engine = None

    def get_engine(self):
        if self.engine is None:
            from src import rag_engine, ingestion, config
            import os

            possible_paths = ["/data/faiss_index", "/data/data/faiss_index"]
            final_path = "/data/faiss_index" 
            
            for p in possible_paths:
                if os.path.exists(p) and "index.faiss" in os.listdir(p):
                    final_path = p
                    print(f"DEBUG: Found valid index at {p}")
                    break
            
            config.INDEX_PATH = final_path
            
            if os.path.exists(config.INDEX_PATH):
                print(f"DEBUG: Index found at {config.INDEX_PATH}. Files: {os.listdir(config.INDEX_PATH)}")
            else:
                print(f"DEBUG: Index NOT FOUND at {config.INDEX_PATH}. Walking /data to debug:")
                for root, dirs, files in os.walk("/data"):
                    print(f"{root} -> {files}")

            print("Initializing RAG Engine (Lazy Load)...")
            self.engine = rag_engine.RAGEngine()
        return self.engine

    @modal.method()
    def process_query(self, query: str):
        return self.get_engine().process_query(query)

    @modal.fastapi_endpoint(method="POST", label="query")
    def web_query(self, request: QueryRequest):
        try:
            result = self.process_query.local(request.query)
            return result
        except Exception as e:
            import traceback
            error_detail = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            print(f"ERROR: {error_detail}")
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=error_detail)

    @modal.fastapi_endpoint(method="POST", label="reindex")
    def admin_reindex(self, item: dict):
        return {"message": "Re-indexing logic needs data source connection"}
