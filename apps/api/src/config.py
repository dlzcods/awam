import os
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "groq" or "gemini"

HF_TOKEN = os.getenv("HF_TOKEN")

# Embedding model — contextual multilingual, 384 dimensions.
# Uses the e5 prefix convention: "query: " / "passage: ".
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SCRAP_RESULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "scrap", "result")
SCRAP_CLEANED_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "scrap", "cleaned")
INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss_index")
