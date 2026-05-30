# Hukumonline Scraper

Scripts for scraping legal articles from Hukumonline's Klinik section. Uses Firecrawl API for content extraction and optionally Selenium for tag metadata.

## Setup

```sh
cd scrap
pip install -r requirements.txt
```

Set the Firecrawl API key in the root `.env` file:

```
FIRECRAWL_API_KEY=your_key_here
```

## Scripts

| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `scraping-hukumonline-multiple-theme.py` | Scrape multiple categories in one run | Firecrawl |
| `scraping-hukumonline-one-theme.py` | Scrape a single category | Firecrawl |
| `scraping-hukumonline-with-tags.py` | Scrape articles with tag metadata | Firecrawl + Selenium |
| `scraping-tags.py` | Scrape only tags for existing articles | Selenium |

## Configuration

Edit the `themes` list in the script's `__main__` block:

```python
themes = [
    {
        "name": "bisnis",
        "url": "https://www.hukumonline.com/klinik/bisnis/",
        "start_page": 1,
        "end_page": 5
    },
]
```

Available categories: bisnis, hak-asasi-manusia, ilmu-hukum, kekayaan-intelektual, keluarga, kenegaraan, ketenagakerjaan, olahraga, perdata, perlindungan-konsumen, pertanahan-dan-properti, pidana, profesi-hukum, start-up-umkm, teknologi

## Running

```sh
cd scrap/code

# Without tags (faster, no browser needed)
python scraping-hukumonline-multiple-theme.py

# With tags (requires Chrome)
python scraping-hukumonline-with-tags.py
```

## Output

Results are saved to `scrap/result/{category}/`:

```
result/
├── bisnis/
│   └── bisnis_2026-05-22_hal1-5.json
├── pidana/
│   └── pidana_2026-05-22_hal1-10.json
└── ...
```

File naming: `{category}_{date}_hal{start}-{end}.json`

## Cleaning Pipeline

Raw scraped articles contain significant boilerplate noise (navigation headers, ads, related article links, footers). The cleaning pipeline strips this noise to produce clean legal content.

### Running the cleaner

```sh
cd apps/api
python -c "from src.content_cleaner import clean_articles; clean_articles('../../scrap/result', '../../scrap/cleaned')"
```

### Cleaning stages

1. **Error detection** — drops Cloudflare 502 errors and content < 200 chars
2. **Start marker detection** — finds where legal content begins (handles 5 structural variants: INTISARI_FIRST, TERIMA_KASIH_FIRST, ULASAN→KT_EMBEDDED, ULASAN_LENGKAP_FIRST, NO_MARKER)
3. **End marker cutting** — cuts at earliest noise marker (TAGS, KLINIK TERBARU, TIPS HUKUM, Artikel Selanjutnya, Butuh Lebih Banyak Artikel)
4. **Embedded KLINIK TERKAIT removal** — strips related-article blocks that appear inline at the start of content
5. **Inline noise stripping** — removes 30+ noise patterns (ads, CTAs, navigation crumbs, disclaimers, newsletter promos, pricing)
6. **Structure normalization** — removes trailing fragments, normalizes whitespace
7. **Validation** — checks cleaned content for remaining forbidden noise keywords

### Cleaned output

Results are saved to `scrap/cleaned/{category}/`:

```
cleaned/
├── bisnis/
│   └── bisnis_2026-05-22_hal1-5.json
└── ...
```

### Integrating with the RAG pipeline

The ingestion pipeline (`apps/api/src/ingestion.py`) automatically prefers cleaned data when building the FAISS index:

```sh
# Build index from cleaned data (default behavior)
python apps/api/src/ingestion.py

# Full pipeline: clean + build index in one step
python apps/api/src/ingestion.py --rebuild

# Or via the main CLI
python apps/api/main.py --rebuild
```

### Expected cleaning performance

| Metric | Target |
|--------|--------|
| Articles cleaned | ~99.8% of raw (only Cloudflare errors dropped) |
| Noise remnants | <0.5% of cleaned articles |
| Content structure consistency | Uniform across all articles |

## Deduplication

Scripts check existing JSON files in the category folder before scraping. Articles already scraped (matched by URL) are skipped. Safe to re-run without creating duplicates.
