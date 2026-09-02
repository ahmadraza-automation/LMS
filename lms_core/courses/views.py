import logging
from urllib.parse import urljoin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from asgiref.sync import async_to_sync
from playwright.async_api import async_playwright

logger = logging.getLogger("radioechoes_api")

BASE_URL = "https://www.radioechoes.com"
DEFAULT_URL = "https://www.radioechoes.com/?page=series&genre=OTR&series_name=Suspense"


async def safe_text(locator):
    try:
        if await locator.count() == 0:
            return "N/A"
        text = await locator.first.inner_text()
        return text.strip() if text else "N/A"
    except Exception:
        return "N/A"


async def safe_attribute(locator, attribute):
    try:
        if await locator.count() == 0:
            return "N/A"
        value = await locator.first.get_attribute(attribute)
        return value.strip() if value else "N/A"
    except Exception:
        return "N/A"


async def scrape_page_async(target_url):
    logger.info("Scraper started for: %s", target_url)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            page = await browser.new_page()
            
            logger.info("Opening page...")
            await page.goto(
                target_url,
                wait_until="domcontentloaded",
                timeout=120000
            )
            await page.wait_for_timeout(2000)
            
            logger.info("Extracting series info...")
            series_name = await safe_text(page.locator(".seriesName"))
            genre = await safe_text(page.locator(".seriesGenre"))
            
            episodes = page.locator(".episodeWrapper")
            total = await episodes.count()
            logger.info("Found %s episodes", total)
            
            scraped_data = []
            
            for i in range(total):
                try:
                    ep = episodes.nth(i)
                    
                    title = await safe_text(ep.locator(".episodeTitle"))
                    date = await safe_text(ep.locator(".broadcastDate"))
                    length = await safe_text(ep.locator(".playEpisode .fileDetails"))
                    play = await safe_attribute(ep.locator(".playEpisode a"), "href")
                    download = await safe_attribute(ep.locator(".downloadEpisode a"), "href")
                    file_size = await safe_text(ep.locator(".downloadEpisode .fileDetails"))
                    description = await safe_text(ep.locator(".episodeDescription"))
                    thumbnail = await safe_attribute(ep.locator("img"), "src")
                    
                    if download != "N/A":
                        download = urljoin(BASE_URL, download)
                    if play != "N/A":
                        play = urljoin(BASE_URL, play)
                    if thumbnail != "N/A":
                        thumbnail = urljoin(BASE_URL, thumbnail)
                    
                    episode_data = {
                        "Series Name": series_name,
                        "Episode Name": title,
                        "Genre": genre,
                        "Original Broadcast Date": date,
                        "Episode Length": length,
                        "Download Link": download,
                        "Play Link": play,
                        "File Size": file_size,
                        "Description": description,
                        "Thumbnail": thumbnail,
                    }
                    
                    scraped_data.append(episode_data)
                    
                except Exception as exc:
                    logger.warning("Error scraping episode %s: %s", i, exc)
                    continue
            
            logger.info("Scraping completed. Total: %s", len(scraped_data))
            return {
                'success': True,
                'data': scraped_data,
                'total': len(scraped_data)
            }
            
        except Exception as exc:
            logger.exception("Scraper error: %s", exc)
            return {
                'success': False,
                'error': str(exc),
                'data': []
            }
        finally:
            await browser.close()


@require_http_methods(["GET"])
def radioechoes_scraper_api(request):
    target_url = request.GET.get('url', DEFAULT_URL)
    
    if not target_url or not target_url.startswith("https://www.radioechoes.com"):
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid URL'
        }, status=400)
    
    try:
        logger.info("API request for: %s", target_url)
        result = async_to_sync(scrape_page_async)(target_url)
        
        if result['success']:
            return JsonResponse({
                'status': 'success',
                'message': 'Scraping completed',
                'scraped_url': target_url,
                'total_episodes': result['total'],
                'data': result['data']
            }, safe=False)
        else:
            return JsonResponse({
                'status': 'error',
                'message': result['error'],
                'data': []
            }, status=500)
    
    except Exception as exc:
        logger.exception("API error: %s", exc)
        return JsonResponse({
            'status': 'error',
            'message': str(exc)
        }, status=500)