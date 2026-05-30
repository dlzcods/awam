import json
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from . import config

def load_data(source_path: str = None):
    """
    Load all JSON article files from the specified directory (recursive).

    Prefers cleaned data (SCRAP_CLEANED_PATH) if available, falls back to
    raw data (SCRAP_RESULT_PATH). Accepts an explicit source_path override.
    """
    all_data = []
    json_files = []

    # Determine source path
    if source_path:
        data_dir = source_path
    elif os.path.exists(config.SCRAP_CLEANED_PATH):
        data_dir = config.SCRAP_CLEANED_PATH
        print(f"Using CLEANED data from: {data_dir}")
    elif os.path.exists(config.SCRAP_RESULT_PATH):
        data_dir = config.SCRAP_RESULT_PATH
        print(f"WARNING: Cleaned data not found, using RAW data from: {data_dir}")
    else:
        raise FileNotFoundError(
            f"No data directory found. Tried:\n"
            f"  cleaned: {config.SCRAP_CLEANED_PATH}\n"
            f"  raw:     {config.SCRAP_RESULT_PATH}"
        )

    for root, _dirs, files in os.walk(data_dir):
        for filename in files:
            if filename.endswith(".json"):
                json_files.append(os.path.join(root, filename))

    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {data_dir}")

    seen_urls = set()
    for file_path in json_files:
        print(f"Loading {os.path.relpath(file_path)}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    print(f"  Warning: not a list, skipping.")
        except Exception as e:
            print(f"  Error: {e}")

    docs = []
    for entry in all_data:
        url = entry.get("link", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)

        metadata = {
            "title": entry.get("title", ""),
            "link": url,
            "publish_date": entry.get("publish_date", ""),
            "tags": entry.get("tags", []),
            "theme": entry.get("theme", "")
        }
        content = entry.get("content", "")
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)

    print(f"Loaded {len(docs)} unique documents from {len(json_files)} files.")
    return docs

def build_index():
    print("Loading data...")
    raw_docs = load_data()
    
    print(f"Splitting {len(raw_docs)} documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(raw_docs)
    
    print("Initializing Embeddings...")
    
    # Use multilingual-e5-small contextual embeddings with passage prefix
    from .embeddings import MultilingualE5Embeddings
    embeddings = MultilingualE5Embeddings(config.EMBEDDING_MODEL)
    
    print("Creating FAISS index...")
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    print(f"Saving index to {config.INDEX_PATH}...")
    vectorstore.save_local(config.INDEX_PATH)
    print("Index built and saved successfully.")


def clean_and_build_index():
    """
    Run the full pipeline: clean raw data -> build FAISS index from cleaned data.

    Usage:
        python ingestion.py --rebuild
    """
    from .content_cleaner import clean_articles

    print("=" * 50)
    print("Stage 1/2: Cleaning raw scraped data...")
    print("=" * 50)
    clean_articles(
        config.SCRAP_RESULT_PATH,
        config.SCRAP_CLEANED_PATH,
        validate=True,
    )

    print()
    print("=" * 50)
    print("Stage 2/2: Building FAISS index from cleaned data...")
    print("=" * 50)
    build_index()

    print()
    print("Pipeline complete! Cleaned data -> FAISS index ready.")


if __name__ == "__main__":
    import sys
    if "--rebuild" in sys.argv or "--from-raw" in sys.argv:
        clean_and_build_index()
    else:
        build_index()
