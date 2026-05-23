from firecrawl import Firecrawl
import os
import time
from bs4 import BeautifulSoup
import re
from config import API_FIRECRAWL

API_KEY = os.getenv("FIRECRAWL_API_KEY", API_FIRECRAWL)
fc = Firecrawl(api_key=API_KEY)

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
    # Coba beberapa selector untuk tanggal
    
    # 1. Cari di metadata
    date_meta = soup.find("meta", property="article:published_time")
    if date_meta and date_meta.get("content"):
        return date_meta.get("content")
    
    # 2. Cari di structured data (JSON-LD)
    script_tags = soup.find_all("script", type="application/ld+json")
    for script in script_tags:
        try:
            import json
            data = json.loads(script.string)
            if isinstance(data, dict):
                if "datePublished" in data:
                    return data["datePublished"]
                if "publishedTime" in data:
                    return data["publishedTime"]
        except:
            pass
    
    # 3. Cari di elemen dengan class/id yang mengandung tanggal
    date_elem = soup.find("time")
    if date_elem:
        return date_elem.get("datetime") or date_elem.get_text(strip=True)
    
    # 4. Cari pattern tanggal dalam teks (format: DD MMM, YYYY)
    date_pattern = re.compile(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)[a-z]*,?\s+\d{4}')
    text = soup.get_text()
    match = date_pattern.search(text)
    if match:
        return match.group(0)
    
    return None

def extract_article_content(html):
    """Extract clean article content from HTML"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Cari wrapper utama yang berisi konten artikel
    main_wrapper = soup.select_one("div.css-103zlhi.elbhtsw0")
    
    if main_wrapper:
        # Hapus elemen yang tidak diinginkan HANYA di dalam wrapper ini
        unwanted_selectors = [
            "article.css-1eyd3st.ejhsnq53",  # KLINIK TERKAIT section
            "div.css-ukcqzp",  # Iklan kursus online
            "div.css-uk4b7z",  # Iklan in-article
            "div.adunitContainer",  # Container iklan
            ".swiper",  # Carousel
            "iframe",  # Iframes
        ]
        
        for selector in unwanted_selectors:
            for elem in main_wrapper.select(selector):
                elem.decompose()
        
        # Cari div yang berisi konten artikel (css-15rxf41)
        content_div = main_wrapper.select_one("div.css-15rxf41.e1vjmfpm0")
        
        if content_div:
            # Ambil semua teks dari content_div
            text = content_div.get_text(separator="\n", strip=True)
            
            # Bersihkan teks yang tidak diinginkan
            text = re.sub(r'KLINIK TERKAIT.*?(?=\n[A-Z]|\n\n|$)', '', text, flags=re.DOTALL)
            text = re.sub(r'Belajar Hukum Secara Online.*?Lihat Semua Kelas\s*', '', text, flags=re.DOTALL)
            text = re.sub(r'Navigate (left|right)\s*', '', text, flags=re.IGNORECASE)
            
            # Bersihkan whitespace berlebih
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            return text.strip()
    
    # Fallback 1: Cari langsung content wrapper
    wrapper = soup.select_one("div.css-15rxf41.e1vjmfpm0")
    if wrapper:
        # Hapus elemen tidak diinginkan
        for selector in ["article.css-1eyd3st", "div.css-ukcqzp", "div.css-uk4b7z"]:
            for elem in wrapper.select(selector):
                elem.decompose()
        
        text = wrapper.get_text(separator="\n", strip=True)
        text = re.sub(r'KLINIK TERKAIT.*?(?=\n[A-Z]|\n\n|$)', '', text, flags=re.DOTALL)
        text = re.sub(r'Belajar Hukum Secara Online.*?Lihat Semua Kelas\s*', '', text, flags=re.DOTALL)
        return text.strip()
    
    # Fallback 2: Ambil semua teks
    return soup.get_text(separator="\n", strip=True)

def scrape_full_article(article):
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
        "title": article["title"],
        "link": url,
        "publish_date": publish_date,
        "content": content_clean
    }

def scrape_pages(start_page=1, end_page=2):
    """Scrape multiple pages of articles"""
    all_results = []
    
    for page in range(start_page, end_page + 1):
        if page == 1:
            list_url = "https://www.hukumonline.com/klinik/perdata/"
        else:
            list_url = f"https://www.hukumonline.com/klinik/perdata/page/{page}/"
        
        article_links = extract_article_links(list_url)
        
        for art in article_links:
            try:
                data = scrape_full_article(art)
                all_results.append(data)
                print(f"✓ Scraped: {data['title']}")
                print(f"  Date: {data['publish_date']}")
                time.sleep(2)
            except Exception as ex:
                print(f"✗ Error scraping {art['link']}: {ex}")
    
    return all_results

if __name__ == "__main__":
    results = scrape_pages(start_page=1, end_page=1)
    
    import json
    with open("../result/hukumonline_perdata_articles.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Done! Total articles scraped: {len(results)}")
    print(f"  Saved to: hukumonline_perdata_articles.json")