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

## Deduplication

Scripts check existing JSON files in the category folder before scraping. Articles already scraped (matched by URL) are skipped. Safe to re-run without creating duplicates.
