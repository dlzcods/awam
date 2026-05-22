import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    pass 

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower() # Options: "gemini", "groq"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
HF_TOKEN = os.getenv("HF_TOKEN")

# Local embedding model (static, very fast)
EMBEDDING_MODEL = "blobbybob/potion-mxbai-256d-v2"
LLM_MODEL = "qwen/qwen3-32b"

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss_index")
