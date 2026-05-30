# AWAM - Accessible Wisdom for Law & Advocacy Matters
## Indonesian Legal RAG with Query Reformulation

A retrieval-augmented generation system for answering Indonesian legal questions in everyday language. Users ask in casual Bahasa Indonesia; the system reformulates the query into formal legal terminology, retrieves relevant regulations from a vector database, and generates a grounded answer citing specific laws and articles.

## Disclaimer

This repository has diverged from the original research project. Changes include:

- The frontend was rebuilt from Streamlit to a React + TypeScript SPA
- The dataset has been expanded with new scraped articles
- A multi-stage content cleaning pipeline strips boilerplate noise from scraped articles
- The embedding model was upgraded from model2vec (static 256d) to multilingual-e5-small (contextual 384d)
- Chunk settings were increased from 1000/200 to 1500/300
- Multi-provider LLM support: Groq (Qwen 3) or Gemini (Gemma 4), switchable via `LLM_PROVIDER`
- Deterministic auto-citation: citations are attached post-generation via semantic embedding matching, not left to the LLM

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
5. **Deduplication** — Remove duplicate article URLs so citation numbers are unique
6. **Generation** — The LLM produces a natural-language answer (without citation markers)
7. **Auto-citation** — A deterministic post-processing step splits the answer into sentences, matches each to the most relevant source document via e5-small embedding similarity, and appends `[N]` citations. This eliminates hallucinated citation numbers entirely.

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
|---|---|
| LLM | Qwen 3 32B (Groq) or Gemma 4 26B (Gemini) — switchable via `LLM_PROVIDER` |
| Embedding | `intfloat/multilingual-e5-small` (384d contextual, query/passage prefix) |
| Vector DB | FAISS (CPU) |
| Reranking | Cross-encoder `ms-marco-MiniLM-L-6-v2` (via sentence-transformers) |
| Backend | Python, LangChain, FastAPI |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS v4 |
| Deployment | Modal (serverless) |
| Data source | ~1,300 Hukumonline articles across 15 legal categories |

## Project structure

```
.
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   ├── config.py            # API keys, model names, chunk sizes
│   │   │   ├── content_cleaner.py   # Cleans scraped HTML into structured content
│   │   │   ├── embeddings.py        # MultilingualE5Embeddings (query/passage prefix)
│   │   │   ├── ingestion.py         # Document loading, chunking, FAISS index building
│   │   │   ├── rag_engine.py        # Core pipeline (double-hop + rerank + generate)
│   │   │   ├── utils.py             # Chunk formatting, truncation
│   │   │   └── evaluation/          # Hit Rate, MRR, Faithfulness eval scripts
│   │   ├── app.py                   # Streamlit frontend (legacy)
│   │   ├── main.py                  # CLI entry point
│   │   ├── modal_app.py             # Modal app serving the RAG endpoint
│   │   ├── ingestion_modal.py       # Modal script to build FAISS index on Modal CPU
│   │   └── requirements.txt
│   └── web/
│       ├── src/
│       │   ├── components/          # React UI components
│       │   ├── lib/                 # API client, reducer, utilities
│       │   └── types/               # TypeScript interfaces
│       ├── vite.config.ts
│       └── package.json
├── data/                            # Legal article datasets (15 categories)
├── faiss_index/                     # Pre-built FAISS index (gitignored)
├── scrap/
│   ├── code/                        # Firecrawl scraping scripts
│   ├── result/                      # Raw scraped articles (with boilerplate noise)
│   └── cleaned/                     # Cleaned articles (ready for ingestion)
├── .env.example                     # Required environment variables
├── README_Research-ID.md            # Research report (Indonesian)
└── README_Research_Eng.md           # Research report (English)
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- API key: Groq (for Qwen) or Gemini (for Gemma)

### Environment variables

Copy `.env.example` to `.env` and fill in:

```
LLM_PROVIDER=groq            # "groq" or "gemini"
GROQ_API_KEY=...             # Required if provider=groq
GROQ_MODEL=qwen/qwen3-32b
GEMINI_API_KEY=...           # Required if provider=gemini
GEMINI_MODEL=gemma-4-26b-a4b-it
VITE_API_URL=...             # API endpoint URL (frontend reads this)
HF_TOKEN=...                 # HuggingFace token for cross-encoder model
```

### Data pipeline

The system runs on cleaned legal articles. The data pipeline has two stages:

**Stage 1 — Clean raw scraped data:**

```sh
cd apps/api
python -c "from src.content_cleaner import clean_articles; clean_articles('../../scrap/result', '../../scrap/cleaned')"
```

This strips navigation headers, ads, related-article blocks, and other boilerplate from ~1,300 articles. Output goes to `scrap/cleaned/`.

**Stage 2 — Build the FAISS index (choose one):**

```sh
# Option A: Build on Modal (recommended — 3-5 min on Modal CPU)
modal run apps/api/ingestion_modal.py

# Option B: Build locally
cd apps/api
python src/ingestion.py --rebuild
```

Both options use `intfloat/multilingual-e5-small` (384d contextual embeddings with query/passage prefix convention) and chunk settings of 1500/300. The index is saved to `faiss_index/` (local) or the `rag-storage` Modal volume.

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
# 1. Build the index on Modal volume (one time, or after data changes)
modal run apps/api/ingestion_modal.py

# 2. Deploy the API
modal deploy apps/api/modal_app.py
```

Both scripts share the `rag-storage` Modal volume. The ingestion script writes the FAISS index to the volume; the API reads it at startup.

## How the pipeline works

```
User: "Bos potong gaji seenaknya, bisa dilaporin gak?"

  [Hop 1] Search FAISS with raw query (embedding: "query: Bos potong...")
      -> Returns 3 context documents about labor law

  [Reformulation] LLM rewrites query (temperature=0.7):
      "Hak pekerja atas upah dan sanksi pemotongan gaji
       sepihak oleh pemberi kerja (UU Ketenagakerjaan)"

  [Hop 2] Search FAISS with reformulated query
      -> Returns 15 candidate documents

  [Rerank] Cross-encoder scores and reorders
      -> Top 3 documents kept, deduplicated by article URL

  [Generate] LLM produces natural-language answer (no citation markers,
      temperature=0.3). System prompt uses principle-driven rules:
      explain concepts, connect dots, use plain Indonesian.

  [Auto-cite] Post-processing splits answer into sentences, matches
      each sentence to the best source document via e5-small embedding
      similarity (cosine ≥ 0.7 threshold), appends [1], [2], [3].
      Deterministic — citation numbers can never exceed available docs.
```

### Key design decisions

- **Deterministic auto-citation:** The LLM is NOT asked to produce `[N]` citations. Instead, `auto_cite()` splits the answer into sentences and matches each to source documents via e5-small embedding similarity. This eliminates hallucinated citation numbers (e.g., `[12]`, `[20]`) and ensures every factual claim is traceable to a source.
- **Multi-provider LLM:** Switch between Groq (Qwen 3) and Gemini (Gemma 4) by changing `LLM_PROVIDER` in `.env`. Gemini uses native `google-genai` SDK with `system_instruction`/`contents` separation — no LangChain wrapper overhead. Groq uses `langchain-groq`.
- **Embedding prefix convention:** e5-small requires `"query: "` before user queries and `"passage: "` before documents during both ingestion and query time. This is handled automatically inside the embeddings class.
- **Split LLM temperatures:** Reformulation uses 0.7 (benefits from creative paraphrasing). Generation uses 0.3 (reduces hallucination for factual legal answers).
- **Chunk size 1500/300:** Larger chunks preserve legal reasoning chains that span multiple sentences. Overlap prevents context breaks at chunk boundaries.
- **Cleaned data only:** The ingestion pipeline loads from `scrap/cleaned/` (not raw). If cleaned data is missing, it falls back to raw with a warning.

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