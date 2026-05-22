from firecrawl import Firecrawl
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re
import json
from dotenv import load_dotenv

# Load .env from project root (two levels up from scrap/code/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

API_KEY = os.getenv("FIRECRAWL_API_KEY")
if not API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in .env file. Please add it.")
fc = Firecrawl(api_key=API_KEY)

# Base directory for results (relative to this script's location)
RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "result")


def get_existing_links(theme_name):
    """
    Load all existing article links for a theme by scanning its category folder.
    Returns a set of URLs that have already been scraped.
    """
    theme_folder = os.path.join(RESULT_DIR, theme_name)
    existing_links = set()

    if not os.path.exists(theme_folder):
        return existing_links

    for filename in os.listdir(theme_folder):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(theme_folder, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                articles = json.load(f)
                for article in articles:
                    if "link" in article:
                        existing_links.add(article["link"])
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Warning: Could not read {filepath}: {e}")

    return existing_links


def extract_article_links(list_url):
    print("Fetching list page:", list_url)
    doc = fc.scrape(list_url, formats=["html"])
    html = doc.html
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.select("a[href]"):
        href = a.get("href")
        text = a.get_text(strip=True)
        if not href or not text:
            continue
        if "/klinik/a/" in href:
            if href.startswith("/"):
                href = "https://www.hukumonline.com" + href
            links.append({"title": text, "link": href})

    seen = set()
    unique_links = []
    for item in links:
        if item["link"] not in seen:
            seen.add(item["link"])
            unique_links.append(item)

    print(f"Found {len(unique_links)} unique links on {list_url}")
    return unique_links


def extract_publish_date(soup):
    """Extract publish date from the article page"""
    # 1. Cari di metadata
    date_meta = soup.find("meta", property="article:published_time")
    if date_meta and date_meta.get("content"):
        return date_meta.get("content")

    # 2. Cari di structured data (JSON-LD)
    script_tags = soup.find_all("script", type="application/ld+json")
    for script in script_tags:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                if "datePublished" in data:
                    return data["datePublished"]
                if "publishedTime" in data:
                    return data["publishedTime"]
        except:
            pass

    # 3. Cari di elemen time
    date_elem = soup.find("time")
    if date_elem:
        return date_elem.get("datetime") or date_elem.get_text(strip=True)

    # 4. Cari pattern tanggal dalam teks
    date_pattern = re.compile(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)[a-z]*,?\s+\d{4}')
    text = soup.get_text()
    match = date_pattern.search(text)
    if match:
        return match.group(0)

    return None


def extract_article_content(html):
    """Extract clean article content from HTML"""
    soup = BeautifulSoup(html, "html.parser")

    main_wrapper = soup.select_one("div.css-103zlhi.elbhtsw0")

    if main_wrapper:
        unwanted_selectors = [
            "article.css-1eyd3st.ejhsnq53",
            "div.css-ukcqzp",
            "div.css-uk4b7z",
            "div.adunitContainer",
            ".swiper",
            "iframe",
        ]

        for selector in unwanted_selectors:
            for elem in main_wrapper.select(selector):
                elem.decompose()

        content_div = main_wrapper.select_one("div.css-15rxf41.e1vjmfpm0")

        if content_div:
            text = content_div.get_text(separator=" ", strip=True)
            text = re.sub(r'KLINIK TERKAIT.*?(?=\s[A-Z]|\s\s|$)', '', text, flags=re.DOTALL)
            text = re.sub(r'Belajar Hukum Secara Online.*?Lihat Semua Kelas\s*', '', text, flags=re.DOTALL)
            text = re.sub(r'Navigate (left|right)\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

    # Fallback 1
    wrapper = soup.select_one("div.css-15rxf41.e1vjmfpm0")
    if wrapper:
        for selector in ["article.css-1eyd3st", "div.css-ukcqzp", "div.css-uk4b7z"]:
            for elem in wrapper.select(selector):
                elem.decompose()

        text = wrapper.get_text(separator=" ", strip=True)
        text = re.sub(r'KLINIK TERKAIT.*?(?=\s[A-Z]|\s\s|$)', '', text, flags=re.DOTALL)
        text = re.sub(r'Belajar Hukum Secara Online.*?Lihat Semua Kelas\s*', '', text, flags=re.DOTALL)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    # Fallback 2
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def scrape_full_article(article, theme):
    """Scrape full article with all metadata"""
    url = article["link"]
    print("Scraping article:", url)

    doc = fc.scrape(url, formats=["html"])
    html = doc.html if hasattr(doc, "html") else None

    content_clean = None
    publish_date = None

    if html:
        soup = BeautifulSoup(html, "html.parser")
        content_clean = extract_article_content(html)
        publish_date = extract_publish_date(soup)
    else:
        content_clean = getattr(doc, "markdown", "")

    # Fallback untuk tanggal dari metadata Firecrawl
    if not publish_date and hasattr(doc, "metadata"):
        meta = doc.metadata
        if hasattr(meta, "published_at"):
            publish_date = meta.published_at
        elif isinstance(meta, dict):
            publish_date = meta.get("published_at") or meta.get("publishedTime")

    return {
        "theme": theme,
        "title": article["title"],
        "link": url,
        "publish_date": publish_date,
        "content": content_clean
    }


def scrape_theme(theme_url, theme_name, start_page=1, end_page=1):
    """Scrape articles from a specific theme with deduplication"""
    print(f"\n{'='*60}")
    print(f"Starting scraping for theme: {theme_name}")
    print(f"Pages: {start_page} to {end_page}")
    print(f"{'='*60}\n")

    # Load existing links for deduplication
    existing_links = get_existing_links(theme_name)
    if existing_links:
        print(f"Found {len(existing_links)} existing articles for '{theme_name}' - will skip duplicates")

    theme_results = []
    skipped_count = 0

    for page in range(start_page, end_page + 1):
        if page == 1:
            list_url = theme_url
        else:
            list_url = theme_url.rstrip('/') + f"/page/{page}/"

        article_links = extract_article_links(list_url)

        for art in article_links:
            # Deduplication check
            if art["link"] in existing_links:
                print(f"⏭ Already scraped: {art['title']}")
                skipped_count += 1
                continue

            try:
                data = scrape_full_article(art, theme_name)
                theme_results.append(data)
                print(f"✓ Scraped: {data['title']}")
                print(f"  Date: {data['publish_date']}")
                time.sleep(2)
            except Exception as ex:
                print(f"✗ Error scraping {art['link']}: {ex}")

    print(f"\n✓ Theme '{theme_name}' completed!")
    print(f"  New articles: {len(theme_results)}")
    print(f"  Skipped (already exists): {skipped_count}\n")
    return theme_results


def save_results(theme_name, results, start_page, end_page):
    """Save results to category folder with date and page info in filename"""
    if not results:
        print(f"⚠ No new results to save for '{theme_name}'")
        return None

    # Create category folder if it doesn't exist
    theme_folder = os.path.join(RESULT_DIR, theme_name)
    os.makedirs(theme_folder, exist_ok=True)

    # Generate filename: {theme}_{date}_hal{start}-{end}.json
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = os.path.join(theme_folder, f"{theme_name}_{today}_hal{start_page}-{end_page}.json")

    # If file already exists for today with same pages, merge with it
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_today = json.load(f)
            existing_today_links = {a["link"] for a in existing_today}
            new_only = [a for a in results if a["link"] not in existing_today_links]
            results = existing_today + new_only
        except (json.JSONDecodeError, IOError):
            pass

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✓ Saved {len(results)} articles to: {output_file}")
    return output_file


if __name__ == "__main__":
    # ============================================================
    # KONFIGURASI - Edit bagian ini untuk mengatur scraping
    # ============================================================
    #
    # Format setiap tema:
    #   "name"       : nama kategori (harus sama dengan folder di result/)
    #   "url"        : URL halaman list klinik hukumonline
    #   "start_page" : halaman awal (1 = halaman pertama)
    #   "end_page"   : halaman akhir (setiap halaman ~10 artikel)
    #
    # Contoh: start_page=1, end_page=5 akan scrape halaman 1-5 (~50 artikel)
    #
    # Tema yang tersedia:
    #   bisnis, hak-asasi-manusia, ilmu-hukum, kekayaan-intelektual,
    #   keluarga, kenegaraan, ketenagakerjaan, olahraga, perdata,
    #   perlindungan-konsumen, pertanahan-dan-properti, pidana,
    #   profesi-hukum, start-up-umkm, teknologi
    # ============================================================

    themes = [
        {
            "name": "kenegaraan",
            "url": "https://www.hukumonline.com/klinik/kenegaraan/",
            "start_page": 1,
            "end_page": 5
        },
        # Uncomment dan tambahkan tema lain sesuai kebutuhan:
        # {
        #     "name": "pidana",
        #     "url": "https://www.hukumonline.com/klinik/pidana/",
        #     "start_page": 1,
        #     "end_page": 5
        # },
        # {
        #     "name": "bisnis",
        #     "url": "https://www.hukumonline.com/klinik/bisnis/",
        #     "start_page": 6,
        #     "end_page": 10
        # },
    ]

    # Jalankan scraping dan simpan per tema
    all_results = []
    saved_files = []

    for theme in themes:
        theme_name = theme.get("name", "unknown")
        theme_url = theme.get("url")
        start_page = theme.get("start_page", 1)
        end_page = theme.get("end_page", 1)

        if not theme_url:
            print(f"⚠ Skipping theme '{theme_name}': No URL provided")
            continue

        try:
            # Scrape tema (with deduplication)
            results = scrape_theme(theme_url, theme_name, start_page, end_page)
            all_results.extend(results)

            # Save to category folder with date and page info
            output_file = save_results(theme_name, results, start_page, end_page)

            if output_file:
                saved_files.append({
                    "theme": theme_name,
                    "file": output_file,
                    "count": len(results)
                })

        except Exception as ex:
            print(f"✗ Error scraping theme '{theme_name}': {ex}")

    # Summary
    print(f"\n{'='*60}")
    print("SCRAPING COMPLETED!")
    print(f"{'='*60}")
    print(f"Total new articles scraped: {len(all_results)}")
    print(f"\nFiles saved:")
    for file_info in saved_files:
        print(f"  - {file_info['theme']}: {file_info['count']} articles → {file_info['file']}")
    print(f"{'='*60}\n")
