import json
import os
from langchain_community.document_loaders import JSONLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from . import config

def load_data():
    if not os.path.exists(config.DATA_PATH):
        raise FileNotFoundError(f"Data directory not found at {config.DATA_PATH}")
    all_data = []
    for filename in os.listdir(config.DATA_PATH):
        if filename.endswith(".json"):
            file_path = os.path.join(config.DATA_PATH, filename)
            print(f"Loading data from {filename}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    else:
                        print(f"Warning: {filename} does not contain a list of objects. Skipping.")
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    docs = []
    for entry in all_data:
        metadata = {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "publish_date": entry.get("publish_date", ""),
            "tags": entry.get("tags", []),
            "theme": entry.get("theme", "")
        }
        content = entry.get("content", "")
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)
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
    
    # Use model2vec static embeddings (very fast)
    from .embeddings import Model2VecEmbeddings
    embeddings = Model2VecEmbeddings(config.EMBEDDING_MODEL)
    
    print("Creating FAISS index...")
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    print(f"Saving index to {config.INDEX_PATH}...")
    vectorstore.save_local(config.INDEX_PATH)
    print("Index built and saved successfully.")

if __name__ == "__main__":
    build_index()
