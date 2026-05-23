# from firecrawl import Firecrawl
# import os
from bs4 import BeautifulSoup
# from config import API_FIRECRAWL

# API_KEY = os.getenv("FIRECRAWL_API_KEY", API_FIRECRAWL)
# fc = Firecrawl(api_key=API_KEY)

# def scrape_date(url):
#     print(f"Scraping date from: {url}")
    
#     doc = fc.scrape(url, formats=["html"])
#     html = doc.html
#     soup = BeautifulSoup(html, "html.parser")
    
#     # 1. Coba meta tag
#     date_meta = soup.find("div", class_="css-17qwrqj e12pag3i0")
#     print(date_meta)

#     print("=====================================================================================")

#     inner_div = date_meta.select_one('div.css-17qwrqj e12pag3i0')
#     if inner_div:
#         print("Inner div text:", inner_div.get_text(strip=True))
    
#     # 2. Coba JSON-LD
#     # script_tags = soup.find_all("script", type="application/ld+json")
#     # for script in script_tags:
#     #     try:
#     #         import json
#     #         data = json.loads(script.string)
#     #         if isinstance(data, dict):
#     #             if "datePublished" in data:
#     #                 return data["datePublished"]
#     #             if "publishedTime" in data:
#     #                 return data["publishedTime"]
#     #     except:
#     #         pass
    
#     # # 3. Coba time tag
#     # time_element = soup.find("time")
#     # if time_element:
#     #     return time_element.get("datetime") or time_element.get_text(strip=True)
    
#     # print("Date not found with any method.")
#     # return None






from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

# def scrape_with_selenium(url):
#     driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))  # Tanpa options
#     driver.get(url)
    
#     html = driver.page_source
#     soup = BeautifulSoup(html, "html.parser")
    
#     tags_div = soup.select_one('div.css-17qwrqj.e12pag3i0')
#     if tags_div:
#         print("Full tags div:", tags_div.prettify())
    
#     driver.quit()

# def scrape_with_selenium(url):
#     try:
#         driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
#         driver.get(url)
        
#         html = driver.page_source
#         soup = BeautifulSoup(html, "html.parser")
        
#         tags_div = soup.select_one('div.css-17qwrqj.e12pag3i0')
#         if tags_div:
#             print("Full tags div found.")
            
#             # Cari a tags dan ambil teks saja
#             tag_links = tags_div.select('a.__tag_click')
#             for link in tag_links:
#                 tag_text = link.get_text(strip=True)
#                 print(f"Tag: {tag_text}")
#         else:
#             print("Tags div not found.")
        
#         driver.quit()
#     except Exception as e:
#         print(f"Error: {e}")

def scrape_with_selenium(url):
    try:
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        driver.get(url)
        
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        tags_div = soup.select_one('div.css-17qwrqj.e12pag3i0')
        if tags_div:
            tag_links = tags_div.select('a.__tag_click')
            tags_list = [link.get_text(strip=True) for link in tag_links]
            return {"tags": tags_list}
        else:
            return {"tags": []}
        
        driver.quit()
    except Exception as e:
        print(f"Error: {e}")
        return {"tags": []}






# Contoh penggunaan
if __name__ == "__main__":
    article_url = "https://www.hukumonline.com/klinik/a/saksi-dan-bukti-transfer-uang-dalam-perjanjian-utang-piutang-lt510e2c82af14e/"
    
    date = scrape_with_selenium(article_url)
    print(f"Testing: {date}")