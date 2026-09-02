import csv
import logging
import os
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://radioechoes.com/"
OUTPUT_FILE = "radioechoes_episodes.csv"

# Jin series ko scrape karna hai unki list
TARGET_SERIES = [
    ("Ace Williams", "https://radioechoes.com/?page=series&genre=OTR-Adventure&series=Ace%20Williams"),
    ("1001 Wives", "https://radioechoes.com/?page=series&genre=OTR-Drama&series=1001%20Wives"),
    ("The Whistler", "https://radioechoes.com/?page=series&genre=OTR-Mystery&series=The%20Whistler"),
    ("Suspense", "https://radioechoes.com/?page=series&genre=OTR-Drama&series=Suspense"),
    ("Gunsmoke", "https://radioechoes.com/?page=series&genre=OTR-Western&series=Gunsmoke"),
    ("The Shadow", "https://radioechoes.com/?page=series&genre=OTR-Mystery&series=The%20Shadow"),
    ("Dragnet", "https://radioechoes.com/?page=series&genre=OTR-Crime&series=Dragnet"),
    ("Boston Blackie", "https://radioechoes.com/?page=series&genre=OTR-Detective&series=Boston%20Blackie"),
    ("Dimension X", "https://radioechoes.com/?page=series&genre=OTR-Sci-Fi&series=Dimension%20X"),
    ("X Minus One", "https://radioechoes.com/?page=series&genre=OTR-Sci-Fi&series=X%20Minus%20One"),
    ("Box 13", "https://radioechoes.com/?page=series&genre=OTR-Mystery&series=Box%2013"),
]

def init_csv():
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Series Name", "Series URL", "Episode Title", "Broadcast Date", "Audio Link"])

def append_episodes(rows):
    if not rows:
        return
    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def scrape_series(page, series_name, series_url):
    episodes = []
    try:
        page.goto(series_url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        data = page.evaluate("""
            () => {
                const results = [];
                const rows = document.querySelectorAll('tr, .episodeRow, div[class*="episode"]');
                rows.forEach(row => {
                    const titleEl = row.querySelector('.episodeTitle, a.episodeTitle, span.episodeTitle');
                    if (titleEl) {
                        const title = titleEl.innerText.trim();
                        const dateEl = row.querySelector('.broadcastDate, .date');
                        const date = dateEl ? dateEl.innerText.replace('Original Broadcast Date:', '').trim() : '';
                        
                        const audioEl = row.querySelector('a[href*=".mp3"], audio source, a.download, a[title*="Download"]');
                        const audio = audioEl ? (audioEl.getAttribute('href') || audioEl.getAttribute('src') || '') : '';
                        
                        if (title) {
                            results.push({ title, date, audio });
                        }
                    }
                });
                return results;
            }
        """)

        for item in data:
            full_audio = urljoin(BASE_URL, item['audio']) if item['audio'] else ''
            episodes.append([series_name, series_url, item['title'], item['date'], full_audio])

    except Exception as exc:
        logger.warning(f"Error scraping {series_name}: {exc}")

    return episodes

def run():
    init_csv()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome", slow_mo=30)
        context = browser.new_context(viewport={"width": 1366, "height": 768})
        page = context.new_page()

        logger.info(f"Total Series to Scrape: {len(TARGET_SERIES)}")

        for idx, (s_name, s_url) in enumerate(TARGET_SERIES, start=1):
            logger.info(f"[{idx}/{len(TARGET_SERIES)}] Scraping: {s_name}")
            eps = scrape_series(page, s_name, s_url)
            if eps:
                append_episodes(eps)
                logger.info(f"  -> Saved {len(eps)} episodes.")
            time.sleep(0.5)

        browser.close()
        logger.info(f"Scraping complete! Data saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run()