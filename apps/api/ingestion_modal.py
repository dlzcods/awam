"""
Standalone Modal script for building the FAISS index with multilingual-e5-small
embeddings from cleaned scraped data.

Usage:
    modal run ingestion_modal.py

The script:
  1. Loads cleaned JSON articles from the mounted scrap/cleaned/ directory
  2. Chunks with RecursiveCharacterTextSplitter(1500, 300)
  3. Embeds with intfloat/multilingual-e5-small (passage: prefix)
  4. Builds FAISS index
  5. Saves to the Modal volume at /data/faiss_index/
"""
import modal

# ── Constants (keep in sync with apps/api/src/config.py) ───────────────────

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
INDEX_OUTPUT_PATH = "/data/faiss_index"
CLEANED_DATA_PATH = "/root/scrap/cleaned"

# ── Modal infrastructure ───────────────────────────────────────────────────

vol = modal.Volume.from_name("rag-storage", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "langchain",
        "langchain-community",
        "langchain-text-splitters",
        "sentence-transformers",
        "faiss-cpu",
    )
    # Include cleaned data (small JSON files, ~20-30MB total)
    .add_local_dir(
        "../../scrap/cleaned",
        remote_path=CLEANED_DATA_PATH,
    )
)

app = modal.App("rag-ingestion")


# ── Embeddings class (self-contained, no dependency on src/) ───────────────

from typing import List
from langchain_core.embeddings import Embeddings


class MultilingualE5Embeddings(Embeddings):
    """Custom LangChain wrapper for intfloat/multilingual-e5-small.

    Implements the e5 prefix convention:
      - Documents: "passage: " prefix
      - Queries:   "query: " prefix
    """

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        prefixed = ["passage: " + t for t in texts]
        embeddings = self.model.encode(
            prefixed,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        prefixed = "query: " + text
        embedding = self.model.encode(
            [prefixed],
            normalize_embeddings=True,
        )
        return embedding[0].tolist()


# ── Main function ──────────────────────────────────────────────────────────

@app.function(
    image=image,
    volumes={"/data": vol},
    timeout=2000,  
)
def build_index():
    import json
    import os

    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS

    # ── 1. Load cleaned data ───────────────────────────────────────────
    print(f"Loading cleaned data from: {CLEANED_DATA_PATH}")
    json_files = []
    for root, _dirs, files in os.walk(CLEANED_DATA_PATH):
        for fname in files:
            if fname.endswith(".json"):
                json_files.append(os.path.join(root, fname))

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in {CLEANED_DATA_PATH}. "
            f"Directory contents: {os.listdir(CLEANED_DATA_PATH)}"
        )

    print(f"Found {len(json_files)} JSON files.")

    seen_urls = set()
    docs = []

    for fp in json_files:
        rel = os.path.relpath(fp, CLEANED_DATA_PATH)
        print(f"  Loading {rel}...")
        with open(fp, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for entry in data:
            url = entry.get("link", "")
            if url and url in seen_urls:
                continue
            seen_urls.add(url)
            metadata = {
                "title": entry.get("title", ""),
                "link": url,
                "publish_date": entry.get("publish_date", ""),
                "tags": entry.get("tags", []),
                "theme": entry.get("theme", ""),
            }
            content = entry.get("content", "")
            docs.append(Document(page_content=content, metadata=metadata))

    print(f"Loaded {len(docs)} unique documents.")

    # ── 2. Chunk ───────────────────────────────────────────────────────
    print(f"Chunking with size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"Produced {len(chunks)} chunks.")

    # ── 3. Embed + build index ─────────────────────────────────────────
    print(f"Initializing embeddings: {EMBEDDING_MODEL}")
    embeddings = MultilingualE5Embeddings(EMBEDDING_MODEL)

    print("Building FAISS index (this may take a few minutes)...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # ── 4. Save to volume ──────────────────────────────────────────────
    os.makedirs(INDEX_OUTPUT_PATH, exist_ok=True)
    print(f"Saving index to {INDEX_OUTPUT_PATH}...")
    vectorstore.save_local(INDEX_OUTPUT_PATH)

    # Persist to Modal volume
    vol.commit()
    print(f"Done! {len(chunks)} chunks indexed with {EMBEDDING_MODEL}.")
    print(f"Index saved at: {INDEX_OUTPUT_PATH}")