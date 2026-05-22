# AWAM — Accessible Wisdom for Law & Advocacy Matters
## Indonesian Legal RAG with Query Reformulation

A retrieval-augmented generation system for answering Indonesian legal questions in everyday language. Users ask in casual Bahasa Indonesia; the system reformulates the query into formal legal terminology, retrieves relevant regulations from a vector database, and generates a grounded answer citing specific laws and articles.

## Disclaimer

This repository has diverged from the original research project. Changes include:

- The frontend was rebuilt from Streamlit to a React + TypeScript SPA
- The dataset has been expanded with new scraped articles
- Embedding models have been updated

The research evaluation results (100% Hit Rate, 98.6% Faithfulness, 93% MRR) were measured on the original configuration and may not reflect current system performance.

For the original research methodology, evaluation data, and full results, see:

- [README_Research-ID.md](./README_Research-ID.md) (Bahasa Indonesia)
- [README_Research_Eng.md](./README_Research_Eng.md) (English)
- Published article: [ACSIT JIITE — Query Reformulation for Indonesian Legal RAG](https://acsit.org/index.php/jiite/article/view/113)

## What it does

Most people don't know how to phrase legal questions using proper terminology. They say things like "Bos potong gaji seenaknya" instead of citing the Manpower Law. This system bridges that gap.

The core mechanism is a double-hop retrieval pipeline:

1. **Hop 1** — Search the vector database using the raw user query to gather initial context
2. **Reformulation** — An LLM analyzes the context and rewrites the casual query into formal legal language
3. **Hop 2** — Search again using the reformulated query for higher-precision results
4. **Reranking** — A cross-encoder reranks the results to push the most relevant document to the top
5. **Generation** — The LLM produces an answer grounded in the retrieved legal documents

## Architecture

This is a monorepo with two applications:

```
apps/
  api/     Python backend (FastAPI on Modal serverless)
  web/     React + TypeScript frontend (Vite)
```

The frontend posts user queries directly to the API endpoint. The API handles the full RAG pipeline and returns the answer, reformulated query, references, and execution time.

## Tech stack

| Layer | Technology |
|-------|-----------|
| LLM | Qwen 3 32B (via Groq) |
| Embedding | blobbybob/potion-mxbai-256d-v2 |
| Vector DB | FAISS (CPU) |
| Reranking | Cross-encoder via sentence-transformers |
| Backend | Python, LangChain, FastAPI |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4 |
| Deployment | Modal (serverless) |
| Data source | Hukumonline articles (scraped) |

## Project structure

```
.
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   ├── config.py            # API keys, model config
│   │   │   ├── embeddings.py        # Embedding model setup
│   │   │   ├── ingestion.py         # Document indexing
│   │   │   ├── rag_engine.py        # Core pipeline (reformulation + rerank)
│   │   │   ├── utils.py             # Shared utilities
│   │   │   └── evaluation/          # Retrieval and quality eval scripts
│   │   ├── app.py                   # Streamlit frontend (legacy)
│   │   ├── main.py                  # CLI entry point
│   │   ├── modal_app.py             # Modal deployment config
│   │   └── requirements.txt
│   └── web/
│       ├── src/
│       │   ├── components/          # React UI components
│       │   ├── lib/                 # API client, reducer, utilities
│       │   └── types/               # TypeScript interfaces
│       ├── vite.config.ts
│       └── package.json
├── data/                            # Legal article datasets (15 categories)
├── faiss_index/                     # Pre-built FAISS index
├── scrap/                           # Scraping scripts and raw results
├── .env.example                     # Required environment variables
├── README_Research-ID.md            # Research report (Indonesian)
└── README_Research_Eng.md           # Research report (English)
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- API keys: Groq (for Qwen) and/or Google (for Gemini + embeddings)

### Environment variables

Copy `.env.example` to `.env` and fill in:

```
GROQ_API_KEY=...            # Required if using Groq/Qwen
LLM_PROVIDER=groq           # "groq" or "gemini"
GROQ_MODEL=qwen/qwen3-32b
VITE_API_URL=...            # API endpoint URL (frontend reads this)
HF_TOKEN=...                # HuggingFace token for cross-encoder model
```

### Running the API locally

```sh
cd apps/api
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python main.py
```

### Running the frontend

```sh
cd apps/web
npm install
npm run dev
```

The frontend reads `VITE_API_URL` from the root `.env` file (configured via `envDir` in vite.config.ts).

### Deploying to Modal

```sh
pip install modal
modal setup
modal deploy apps/api/modal_app.py
```

## How the pipeline works

```
User: "Bos potong gaji seenaknya, bisa dilaporin gak?"

  [Hop 1] Search FAISS with raw query
      -> Returns 3 context documents about labor law

  [Reformulation] LLM rewrites query:
      "Hak pekerja atas upah dan sanksi pemotongan gaji
       sepihak oleh pemberi kerja (UU Ketenagakerjaan)"

  [Hop 2] Search FAISS with reformulated query
      -> Returns 8 candidate documents

  [Rerank] Cross-encoder scores and reorders
      -> Top documents are the most relevant regulations

  [Generate] LLM produces answer citing specific articles
      -> "Berdasarkan Pasal 93 UU No. 13 Tahun 2003..."
```

## Research

This project originated from research on query reformulation techniques for Indonesian legal information retrieval. The published findings are available at:

"Query Reformulation for Indonesian Legal RAG Systems." *Journal of Information Technology and Education (JIITE)*, ACSIT, 2025. [https://acsit.org/index.php/jiite/article/view/113](https://acsit.org/index.php/jiite/article/view/113)

Key results from the research evaluation (original configuration):

| Metric | Score |
|--------|-------|
| Faithfulness | 98.6% |
| Answer Relevancy | 100% |
| Hit Rate | 100% |
| MRR (with reformulation) | 93% |
| MRR (without reformulation) | 90% |

## License

This project is for educational and research purposes.
