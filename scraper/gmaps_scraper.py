import time
import random
import re
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import Stealth

from config import (
    GMAPS_BASE_URL, DEFAULT_LANG, DEFAULT_TIMEOUT,
    CHROMIUM_ARGS, USER_AGENTS, COOKIE_SELECTORS,
    MIN_DELAY, MAX_DELAY
)
from utils.logger import logger
from scraper.web_enricher import enrich_business_web_data

def clean_text(text: str) -> str:
    """Removes unicode icon symbols and formats clean text strings."""
    if not text:
        return ""
    cleaned = re.sub(r'[\uE000-\uF8FF\u2700-\u27BF]', '', text)
    cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip(' ,')

def parse_address_components(address: str) -> tuple[str, str, str]:
    """
    Parses a full address string into (city, postal_code, country).
    Example: 'Av. del Obispo Quesada, 15, 40006 Segovia, Spain' -> ('Segovia', '40006', 'Spain')
    """
    if not address:
        return "", "", ""

    parts = [p.strip() for p in address.split(",") if p.strip()]
    country = parts[-1] if len(parts) >= 1 else ""

    postal_code = ""
    city = ""

    # Look for zip/postal code pattern (4-6 digits)
    zip_match = re.search(r'\b(\d{4,6})\b', address)
    if zip_match:
        postal_code = zip_match.group(1)

    # Infer city from parts before country
    if len(parts) >= 2:
        potential_city_part = parts[-2]
        # Remove postal code digits from city string if combined (e.g. '40006 Segovia')
        city = re.sub(r'\b\d{4,6}\b', '', potential_city_part).strip()
    elif len(parts) == 1:
        city = parts[0]

    return city, postal_code, country

def extract_coordinates_from_url(url: str) -> tuple[float | None, float | None]:
    """Extracts latitude and longitude floats from Google Maps URLs."""
    if not url:
        return None, None

    # Pattern 1: !3d40.93613!4d-4.113489
    match_3d = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', url)
    if match_3d:
        return float(match_3d.group(1)), float(match_3d.group(2))

    # Pattern 2: @40.93613,-4.113489
    match_at = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match_at:
        return float(match_at.group(1)), float(match_at.group(2))

    return None, None

class GoogleMapsScraper:
    def __init__(self, headless: bool = True, lang: str = DEFAULT_LANG):
        self.headless = headless
        self.lang = lang
        self.seen_place_ids = set()

    def _random_sleep(self, min_s: float = MIN_DELAY, max_s: float = MAX_DELAY):
        time.sleep(random.uniform(min_s, max_s))

    def _accept_cookies(self, page):
        """Dismisses GDPR/Cookie consent popups if displayed."""
        for selector in COOKIE_SELECTORS:
            try:
                button = page.locator(selector).first
                if button.is_visible(timeout=1500):
                    logger.info("Dismissing cookie consent banner...")
                    button.click()
                    self._random_sleep(1.0, 2.0)
                    break
            except Exception:
                continue

    def _extract_place_id(self, url: str, name: str, address: str) -> str:
        """Generates a unique ID signature to prevent duplicate lead extractions."""
        match = re.search(r'/maps/place/([^/]+)', url)
        if match:
            return match.group(1)
        match_id = re.search(r'!1s([^!]+)!2s', url)
        if match_id:
            return match_id.group(1)
        clean_name = re.sub(r'\W+', '', name.lower())
        clean_addr = re.sub(r'\W+', '', address.lower())
        return f"{clean_name}_{clean_addr}"

    def scrape(self, query: str, max_results: int = 20, extract_web_data: bool = True) -> list[dict]:
        """
        Executes Google Maps lead scraping for the given query.
        """
        search_url = GMAPS_BASE_URL.format(query=quote_plus(query), lang=self.lang)
        logger.info(f"Starting lead scraper for query: '{query}'")
        logger.info(f"Target URL: {search_url}")

        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=CHROMIUM_ARGS
            )
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )
            page = context.new_page()
            Stealth().apply_stealth_sync(page)

            try:
                page.goto(search_url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)
                self._random_sleep(2.0, 3.0)
                self._accept_cookies(page)

                feed_selector = 'div[role="feed"]'
                try:
                    page.wait_for_selector(feed_selector, timeout=10000)
                except PlaywrightTimeoutError:
                    logger.warning("Main div[role='feed'] container not found. Trying fallback selector...")
                    feed_selector = 'div.m6QEua[role="feed"]'

                feed = page.locator(feed_selector).first
                no_new_items_count = 0

                logger.info(f"Scraping up to {max_results} leads...")

                while len(results) < max_results:
                    place_links = page.locator(f'{feed_selector} a[href*="/maps/place/"]').all()
                    if not place_links:
                        place_links = page.locator('a.hfnt0d').all()

                    current_found = len(place_links)
                    logger.info(f"DOM Places Loaded: {current_found} | Unique Leads Extracted: {len(results)}/{max_results}")

                    new_extracted_in_loop = 0

                    for link in place_links:
                        if len(results) >= max_results:
                            break

                        try:
                            href = link.get_attribute("href") or ""
                            
                            link.scroll_into_view_if_needed()
                            link.click()
                            self._random_sleep(1.2, 2.2)

                            page.wait_for_selector('h1', timeout=4000)

                            # 1. Business Name
                            name = ""
                            for h1 in page.locator('h1').all():
                                txt = clean_text(h1.inner_text())
                                if txt and txt.lower() not in ("results", "resultados", "google maps"):
                                    name = txt
                                    break

                            if not name:
                                continue

                            # 2. Business Category
                            category = ""
                            cat_btn = page.locator('button[jsaction*="category"], button.Dkbeec').first
                            if cat_btn.is_visible(timeout=1000):
                                category = clean_text(cat_btn.inner_text())

                            # 3. Address & Address Components
                            address = ""
                            addr_btn = page.locator('button[data-item-id="address"]').first
                            if addr_btn.is_visible(timeout=1000):
                                address = clean_text(addr_btn.inner_text())
                            else:
                                alt_addr = page.locator('button[aria-label*="Address"], button[aria-label*="Dirección"]').first
                                if alt_addr.is_visible(timeout=1000):
                                    address = clean_text(alt_addr.inner_text())

                            city, postal_code, country = parse_address_components(address)

                            # Deduplication check
                            place_id = self._extract_place_id(href, name, address)
                            if place_id in self.seen_place_ids:
                                continue

                            self.seen_place_ids.add(place_id)
                            new_extracted_in_loop += 1

                            # 4. Geolocation Coordinates (Latitude / Longitude)
                            current_page_url = page.url
                            lat, lng = extract_coordinates_from_url(href or current_page_url)

                            # 5. Phone Number
                            phone = ""
                            phone_btn = page.locator('button[data-item-id*="phone:"]').first
                            if phone_btn.is_visible(timeout=1000):
                                phone = clean_text(phone_btn.inner_text())
                            else:
                                alt_phone = page.locator('button[aria-label*="Phone"], button[aria-label*="Teléfono"]').first
                                if alt_phone.is_visible(timeout=1000):
                                    phone = clean_text(alt_phone.inner_text())

                            # 6. Website URL
                            website = ""
                            web_link = page.locator('a[data-item-id="authority"]').first
                            if web_link.is_visible(timeout=1000):
                                website = web_link.get_attribute("href") or ""
                            else:
                                alt_web = page.locator('a[aria-label*="Website"], a[aria-label*="sitio web"]').first
                                if alt_web.is_visible(timeout=1000):
                                    website = alt_web.get_attribute("href") or ""

                            # 7. Rating & Reviews Count
                            rating = None
                            reviews_count = None
                            try:
                                rating_el = page.locator('div.F7263c, div.fontBodyMedium span[aria-hidden="true"]').first
                                if rating_el.is_visible(timeout=1000):
                                    r_txt = rating_el.inner_text().strip()
                                    if re.match(r'^\d+[\.,]\d+$', r_txt):
                                        rating = float(r_txt.replace(',', '.'))

                                if rating is None:
                                    star_span = page.locator('span[aria-label*="stars"], span[aria-label*="estrellas"]').first
                                    if star_span.is_visible(timeout=1000):
                                        star_text = star_span.get_attribute("aria-label") or ""
                                        m_star = re.search(r'([\d,.]+)', star_text)
                                        if m_star:
                                            rating = float(m_star.group(1).replace(",", "."))

                                rev_btn = page.locator('button[aria-label*="reviews"], button[aria-label*="reseñas"]').first
                                if rev_btn.is_visible(timeout=1000):
                                    rev_text = rev_btn.inner_text().strip()
                                    m_rev = re.search(r'([\d\.]+)', rev_text.replace(" ", "").replace(",", ""))
                                    if m_rev:
                                        reviews_count = int(m_rev.group(1).replace(".", ""))
                            except Exception:
                                pass

                            # 8. Web Intelligence Enrichment (Email & Social Links)
                            web_data = {
                                "email": "",
                                "facebook": "",
                                "instagram": "",
                                "linkedin": "",
                                "twitter": ""
                            }
                            if extract_web_data and website:
                                logger.info(f"Enriching web intelligence for: {website}")
                                web_data = enrich_business_web_data(website)

                            item = {
                                "name": name,
                                "category": category,
                                "rating": rating,
                                "reviews_count": reviews_count,
                                "phone": phone,
                                "email": web_data["email"],
                                "website": website,
                                "address": address,
                                "city": city,
                                "postal_code": postal_code,
                                "country": country,
                                "latitude": lat,
                                "longitude": lng,
                                "facebook": web_data["facebook"],
                                "instagram": web_data["instagram"],
                                "linkedin": web_data["linkedin"],
                                "twitter": web_data["twitter"],
                                "place_id": place_id,
                                "url": href if href.startswith("http") else f"https://www.google.com{href}"
                            }

                            results.append(item)
                            logger.info(f"[{len(results)}/{max_results}] Extracted: {name} | Cat: {category or 'N/A'} | Rating: {rating or 'N/A'} ⭐ | Tel: {phone or 'N/A'} | Email: {web_data['email'] or 'N/A'}")

                        except Exception as e:
                            logger.debug(f"Error processing lead item: {e}")
                            continue

                    # Feed Scroll Loop
                    try:
                        feed.evaluate("el => el.scrollBy(0, 1200)")
                        self._random_sleep(1.5, 2.5)
                    except Exception:
                        break

                    # End of feed check
                    end_text = page.locator('span:has-text("You\'ve reached the end"), span:has-text("Llegaste al final")')
                    if end_text.is_visible(timeout=1000):
                        logger.info("Reached end of Google Maps search results.")
                        break

                    if new_extracted_in_loop == 0:
                        no_new_items_count += 1
                        if no_new_items_count >= 4:
                            logger.info("No new leads found after multiple scrolls. Ending search.")
                            break
                    else:
                        no_new_items_count = 0

            except Exception as e:
                logger.error(f"Scraping error: {e}")
            finally:
                browser.close()

        logger.info(f"Scraping finished. Total leads extracted: {len(results)}")
        return results
