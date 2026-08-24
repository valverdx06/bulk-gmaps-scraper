import os
import sys
import time
import random
import re
import asyncio
import html
import json
from urllib.parse import quote_plus, urljoin, unquote_plus
import httpx
import pandas as pd
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import Stealth

from config import (
    GMAPS_BASE_URL, DEFAULT_TIMEOUT,
    CHROMIUM_ARGS, USER_AGENTS, COOKIE_SELECTORS,
    CONTACT_PATHS, SOCIAL_PATTERNS, OUTPUT_DIR
)
from utils.logger import logger
from utils.exporter import export_data

# Comprehensive Fragrance Industry Search Terms
KEYWORDS = [
    "Perfume store",
    "Fragrance shop",
    "Perfume boutique",
    "Fragrance boutique",
    "Niche perfume store",
    "Perfume shop",
    "Custom perfume shop",
    "Cologne store",
    "Arabian perfume store",
    "Perfume oil shop",
    "Artisan perfumer boutique"
]

# Complete 50 US States & Top Metropolitan Areas (350+ Cities)
US_LOCATIONS = [
    # Top Metros
    "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Miami, FL",
    "Dallas, TX", "Atlanta, GA", "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX",
    "San Diego, CA", "Austin, TX", "Las Vegas, NV", "Orlando, FL", "Charlotte, NC",
    "Seattle, WA", "Denver, CO", "Boston, MA", "Nashville, TN", "Tampa, FL",
    "Detroit, MI", "Minneapolis, MN", "Indianapolis, IN", "San Francisco, CA", "Columbus, OH",
    "Fort Worth, TX", "Portland, OR", "Memphis, TN", "Baltimore, MD", "Milwaukee, WI",
    "Albuquerque, NM", "Tucson, AZ", "Fresno, CA", "Sacramento, CA", "Kansas City, MO",
    "Mesa, AZ", "Omaha, NE", "Raleigh, NC", "Virginia Beach, VA", "Long Beach, CA",
    "Oakland, CA", "Tulsa, OK", "Arlington, TX", "New Orleans, LA", "Wichita, KS",
    "Cleveland, OH", "Bakersfield, CA", "Honolulu, HI", "Anaheim, CA", "Santa Ana, CA",
    "Riverside, CA", "Corpus Christi, TX", "Lexington, KY", "Stockton, CA", "Henderson, NV",
    "St. Louis, MO", "Cincinnati, OH", "Pittsburgh, PA", "Greensboro, NC", "Anchorage, AK",
    "Plano, TX", "Lincoln, NE", "Irvine, CA", "Newark, NJ", "Toledo, OH", "Durham, NC",
    "Chula Vista, CA", "Fort Wayne, IN", "Jersey City, NJ", "St. Petersburg, FL", "Laredo, TX",
    "Madison, WI", "Chandler, AZ", "Buffalo, NY", "Lubbock, TX", "Scottsdale, AZ", "Reno, NV",
    "Glendale, AZ", "Gilbert, AZ", "Winston-Salem, NC", "North Las Vegas, NV", "Norfolk, VA",
    "Chesapeake, VA", "Garland, TX", "Irving, TX", "Hialeah, FL", "Fremont, CA",
    "Boise, ID", "Richmond, VA", "Baton Rouge, LA", "Spokane, WA", "Des Moines, IA",
    "Tacoma, WA", "San Bernardino, CA", "Modesto, CA", "Fontana, CA", "Santa Clarita, CA",
    "Birmingham, AL", "Oxnard, CA", "Fayetteville, NC", "Rochester, NY", "Moreno Valley, CA",
    "Glendale, CA", "Yonkers, NY", "Huntington Beach, CA", "Aurora, IL", "Salt Lake City, UT",
    "Amarillo, TX", "Montgomery, AL", "Grand Rapids, MI", "Little Rock, AR", "Akron, OH",
    "Augusta, GA", "Huntsville, AL", "Columbus, GA", "Grand Prairie, TX", "Shreveport, LA",
    "Overland Park, KS", "Tallahassee, FL", "Mobile, AL", "Knoxville, TN", "Worcester, MA",
    "Tempe, AZ", "Cape Coral, FL", "Brownsville, TX", "Fort Lauderdale, FL", "Providence, RI",
    "Newport News, VA", "Chattanooga, TN", "Rancho Cucamonga, CA", "Santa Rosa, CA", "Oceanside, CA",
    "Sioux Falls, SD", "Ontario, CA", "Vancouver, WA", "Elk Grove, CA", "Pembroke Pines, FL",
    "Salem, OR", "Eugene, OR", "Peoria, AZ", "Corona, CA", "Springfield, MO",
    "Jackson, MS", "Cary, NC", "Fort Collins, CO", "Hayward, CA", "Lancaster, CA",
    "Alexandria, VA", "Salinas, CA", "Palmdale, CA", "Lakewood, CO", "Springfield, MA",
    "Sunnyvale, CA", "Hollywood, FL", "Pasadena, CA", "Clarksville, TN", "Pomona, CA",
    "Kansas City, KS", "Macon, GA", "Escondido, CA", "Paterson, NJ", "Joliet, IL",
    "Naperville, IL", "Rockford, IL", "Torrance, CA", "Bridgeport, CT", "Savannah, GA",
    "Killeen, TX", "Bellevue, WA", "Mesquite, TX", "Syracuse, NY", "McAllen, TX",
    "Pasadena, TX", "Orange, CA", "Fullerton, CA", "Dayton, OH", "Miramar, FL",
    "Olathe, KS", "Thornton, CO", "Roseville, CA", "Denton, TX", "Waco, TX",
    "Surprise, AZ", "Carrollton, TX", "West Valley City, UT", "Charleston, SC", "Warren, MI",
    "Hampton, VA", "Gainesville, FL", "Visalia, CA", "Coral Springs, FL", "Columbia, SC",
    "Cedar Rapids, IA", "Sterling Heights, MI", "New Haven, CT", "Stamford, CT", "Concord, CA",
    "Kent, WA", "Santa Clara, CA", "Elizabeth, NJ", "Round Rock, TX", "Thousand Oaks, CA",
    "Topeka, KS", "Simi Valley, CA", "Fargo, ND", "Norman, OK", "Columbia, MO",
    "Abilene, TX", "Wilmington, NC", "Hartford, CT", "Clovis, CA", "Allentown, PA",
    # Additional High-Density & Luxury Markets
    "Beverly Hills, CA", "Newport Beach, CA", "Boca Raton, FL", "West Palm Beach, FL", "Naples, FL",
    "Sarasota, FL", "Key West, FL", "Clearwater, FL", "Delray Beach, FL", "Coral Gables, FL",
    "Scottsdale, AZ", "Paradise Valley, AZ", "Sedona, AZ", "Aspen, CO", "Boulder, CO",
    "Vail, CO", "Greenwich, CT", "Stamford, CT", "Princeton, NJ", "Hoboken, NJ",
    "Montclair, NJ", "Cherry Hill, NJ", "Morristown, NJ", "White Plains, NY", "Albany, NY",
    "Saratoga Springs, NY", "The Hamptons, NY", "Brooklyn, NY", "Queens, NY", "Manhattan, NY",
    "Staten Island, NY", "Bronx, NY", "Long Island, NY", "Garden City, NY", "Manhasset, NY",
    "Asheville, NC", "Chapel Hill, NC", "Wilmington, NC", "Greenville, SC", "Myrtle Beach, SC",
    "Hilton Head Island, SC", "Charleston, SC", "Savannah, GA", "Alpharetta, GA", "Roswell, GA",
    "Carmel, IN", "Ann Arbor, MI", "Troy, MI", "Birmingham, MI", "Grosse Pointe, MI",
    "Edina, MN", "Wayzata, MN", "St. Paul, MN", "Frisco, TX", "The Woodlands, TX",
    "Sugar Land, TX", "Southlake, TX", "Highland Park, TX", "McKinney, TX", "Grapevine, TX",
    "Park City, UT", "Provo, UT", "Bellevue, WA", "Kirkland, WA", "Redmond, WA",
    "Tacoma, WA", "Bellingham, WA", "Bend, OR", "Lake Oswego, OR", "Charlottesville, VA",
    "Arlington, VA", "Alexandria, VA", "Reston, VA", "Tysons, VA", "Virginia Beach, VA",
    # State Capitals & Regional Hubs
    "Juneau, AK", "Fairbanks, AK", "Little Rock, AR", "Fayetteville, AR", "Dover, DE",
    "Wilmington, DE", "Boise, ID", "Meridian, ID", "Coeur d'Alene, ID", "Iowa City, IA",
    "Davenport, IA", "Sioux City, IA", "Lawrence, KS", "Bowling Green, KY", "Covington, KY",
    "Lafayette, LA", "Lake Charles, LA", "Portland, ME", "Bangor, ME", "Annapolis, MD",
    "Bethesda, MD", "Frederick, MD", "Cambridge, MA", "Lowell, MA", "Quincy, MA",
    "Duluth, MN", "Rochester, MN", "Gulfport, MS", "Biloxi, MS", "Hattiesburg, MS",
    "Billings, MT", "Missoula, MT", "Bozeman, MT", "Helena, MT", "Manchester, NH",
    "Nashua, NH", "Concord, NH", "Santa Fe, NM", "Las Cruces, NM", "Bismarck, ND",
    "Grand Forks, ND", "Canton, OH", "Akron, OH", "Dayton, OH", "Oklahoma City, OK",
    "Edmond, OK", "Reading, PA", "Erie, PA", "Scranton, PA", "Lancaster, PA",
    "Newport, RI", "Warwick, RI", "Rapid City, SD", "Aberdeen, SD", "Murfreesboro, TN",
    "Franklin, TN", "Johnson City, TN", "Burlington, VT", "Morgantown, WV", "Charleston, WV",
    "Huntington, WV", "Green Bay, WI", "Kenosha, WI", "Appleton, WI", "Cheyenne, WY",
    "Casper, WY", "Jackson, WY"
]

EXCLUDED_CHAINS = {
    "walmart", "cvs", "walgreens", "target", "costco", "sam's club", "sams club",
    "kroger", "dollar tree", "dollar general", "family dollar", "rite aid",
    "ross", "tj maxx", "t.j. maxx", "marshalls", "burlington", "kohl's", "kohls",
    "macy's", "macys", "jcpenney", "jcp", "sephora", "ulta", "bath & body works",
    "bath and body works", "victoria's secret", "victorias secret", "dillard's",
    "nordstrom", "walgreens pharmacy", "cvs pharmacy", "publix", "albertsons",
    "bed bath & beyond", "tjx", "target optical", "walmart pharmacy"
}

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}")
MAILTO_REGEX = re.compile(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})', re.IGNORECASE)

IGNORED_DOMAINS = {
    "sentry.io", "wixpress.com", "example.com", "schema.org", "domain.com",
    "png", "jpg", "jpeg", "svg", "gif", "webp", "googleapis.com", "cloudflare.com",
    "w3.org", "myshopify.com", "google.com", "facebook.com", "instagram.com",
    "twitter.com", "linkedin.com", "youtube.com", "apple.com", "microsoft.com"
}

def is_excluded_chain(name: str) -> bool:
    n_clean = name.lower()
    for chain in EXCLUDED_CHAINS:
        if chain in n_clean:
            return True
    return False

def clean_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'[\uE000-\uF8FF\u2700-\u27BF]', '', text)
    cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip(' ,')

def parse_address_components(address: str) -> tuple[str, str, str]:
    if not address:
        return "", "", "USA"
    parts = [p.strip() for p in address.split(",") if p.strip()]
    country = "USA"
    postal_code = ""
    city = ""

    zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
    if zip_match:
        postal_code = zip_match.group(1)

    if len(parts) >= 2:
        potential_city_part = parts[-2]
        city = re.sub(r'\b\d{5}(?:-\d{4})?\b', '', potential_city_part).strip()
        city = re.sub(r'\b[A-Z]{2}\b', '', city).strip()
    elif len(parts) == 1:
        city = parts[0]

    return city, postal_code, country

def extract_coordinates_from_url(url: str) -> tuple[float | None, float | None]:
    if not url:
        return None, None
    match_3d = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', url)
    if match_3d:
        return float(match_3d.group(1)), float(match_3d.group(2))
    match_at = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match_at:
        return float(match_at.group(1)), float(match_at.group(2))
    return None, None

def is_valid_email(email: str) -> bool:
    if not email or len(email) < 6:
        return False
    email_lower = email.lower().strip()
    ext = email_lower.split(".")[-1]
    if ext in IGNORED_DOMAINS:
        return False
    for domain in IGNORED_DOMAINS:
        if domain in email_lower:
            return False
    if email_lower.startswith(("info@", "sales@", "support@", "orders@", "contact@", "hello@", "service@", "boutique@", "perfume@")):
        return True
    return True

def extract_social_links(html_text: str) -> dict[str, str]:
    socials = {"facebook": "", "instagram": "", "linkedin": "", "twitter": ""}
    for platform, pattern in SOCIAL_PATTERNS.items():
        matches = re.findall(pattern, html_text, re.IGNORECASE)
        for link in matches:
            link_lower = link.lower()
            if any(share_word in link_lower for share_word in ["sharer", "share", "intent", "plugins", "dialog", "wp-content"]):
                continue
            socials[platform] = link.rstrip("/")
            break
    return socials

async def async_enrich_single_website(client: httpx.AsyncClient, website_url: str, semaphore: asyncio.Semaphore) -> dict:
    """High-efficiency deep crawler extracting direct emails, mailto links, and social profiles."""
    data = {"email": "", "facebook": "", "instagram": "", "linkedin": "", "twitter": ""}
    if not website_url:
        return data

    url = website_url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"

    social_domains = ["facebook.com", "instagram.com", "twitter.com", "linkedin.com", "youtube.com", "wa.me", "t.me"]
    if any(sd in url.lower() for sd in social_domains):
        return data

    async with semaphore:
        found_emails = set()
        for path in CONTACT_PATHS:
            try:
                target_url = urljoin(url, path) if path else url
                resp = await client.get(target_url, timeout=4.0, follow_redirects=True)
                if resp.status_code == 200:
                    raw_html = resp.text
                    unescaped_html = html.unescape(raw_html)

                    # 1. Direct Mailto Links
                    for m_match in MAILTO_REGEX.findall(unescaped_html):
                        clean_m = m_match.split("?")[0].strip()
                        if is_valid_email(clean_m):
                            found_emails.add(clean_m)

                    # 2. Raw Body Regex
                    for match in EMAIL_REGEX.findall(unescaped_html):
                        if is_valid_email(match):
                            found_emails.add(match)

                    # 3. Social Media Links
                    page_socials = extract_social_links(unescaped_html)
                    for k, v in page_socials.items():
                        if not data[k] and v:
                            data[k] = v

                    # If we found high-quality emails + socials, exit loop early
                    if found_emails and data["instagram"] and data["facebook"]:
                        break
            except Exception:
                continue

        if found_emails:
            # Sort emails prioritizing contact/info/sales/orders
            sorted_emails = sorted(
                list(found_emails),
                key=lambda e: (
                    0 if any(p in e.lower() for p in ["info@", "contact@", "sales@", "hello@", "orders@", "support@", "service@"]) else 1,
                    len(e)
                )
            )
            data["email"] = sorted_emails[0]

    return data

async def async_worker(worker_id: int, locations: list[str], browser, global_state: dict, output_filename: str):
    """Asynchronous browser worker utilizing GPU rasterization & headless stealth."""
    context = await browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={"width": 1280, "height": 800},
        locale="en-US"
    )
    page = await context.new_page()
    await Stealth().apply_stealth_async(page)

    for location in locations:
        if global_state["stop_event"].is_set():
            break

        for keyword in KEYWORDS:
            if global_state["stop_event"].is_set():
                break

            search_query = f"{keyword} in {location}, USA"
            search_url = GMAPS_BASE_URL.format(query=quote_plus(search_query), lang="en")

            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)
                await asyncio.sleep(0.6)

                for selector in COOKIE_SELECTORS:
                    try:
                        btn = page.locator(selector).first
                        if await btn.is_visible(timeout=300):
                            await btn.click()
                            await asyncio.sleep(0.2)
                            break
                    except Exception:
                        pass

                feed_selector = 'div[role="feed"]'
                try:
                    await page.wait_for_selector(feed_selector, timeout=4000)
                except PlaywrightTimeoutError:
                    feed_selector = 'div.m6QEua[role="feed"]'

                for _ in range(6):
                    try:
                        await page.locator(feed_selector).first.evaluate("el => el.scrollBy(0, 1500)")
                        await asyncio.sleep(0.6)
                    except Exception:
                        break

                place_links = await page.locator(f'{feed_selector} a[href*="/maps/place/"]').all()
                if not place_links:
                    place_links = await page.locator('a.hfnt0d').all()

                for link in place_links:
                    if global_state["stop_event"].is_set():
                        break

                    try:
                        href = await link.get_attribute("href") or ""
                        await link.scroll_into_view_if_needed()
                        await link.click()
                        await asyncio.sleep(0.4)

                        await page.wait_for_selector('h1', timeout=2000)

                        name = ""
                        for h1 in await page.locator('h1').all():
                            txt = clean_text(await h1.inner_text())
                            if txt and txt.lower() not in ("results", "resultados", "google maps", "sponsored"):
                                name = txt
                                break

                        # If name was captured as Sponsored or missing, extract real title from URL
                        if not name or name.lower() in ("sponsored", "results", "resultados"):
                            url_match = re.search(r'/maps/place/([^/]+)/', href or page.url)
                            if url_match:
                                name = clean_text(unquote_plus(url_match.group(1)))

                        if not name or is_excluded_chain(name):
                            continue

                        address = ""
                        addr_btn = page.locator('button[data-item-id="address"]').first
                        if await addr_btn.is_visible(timeout=350):
                            address = clean_text(await addr_btn.inner_text())
                        else:
                            alt_addr = page.locator('button[aria-label*="Address"]').first
                            if await alt_addr.is_visible(timeout=350):
                                address = clean_text(await alt_addr.inner_text())

                        city, postal_code, country = parse_address_components(address)
                        dedup_key = f"{name.lower().strip()}_{address.lower().strip()}"

                        async with global_state["lock"]:
                            if dedup_key in global_state["seen_keys"]:
                                continue
                            global_state["seen_keys"].add(dedup_key)

                        category = ""
                        cat_btn = page.locator('button[jsaction*="category"], button.Dkbeec').first
                        if await cat_btn.is_visible(timeout=350):
                            category = clean_text(await cat_btn.inner_text())

                        lat, lng = extract_coordinates_from_url(href or page.url)

                        phone = ""
                        phone_btn = page.locator('button[data-item-id*="phone:"]').first
                        if await phone_btn.is_visible(timeout=350):
                            phone = clean_text(await phone_btn.inner_text())

                        website = ""
                        web_link = page.locator('a[data-item-id="authority"]').first
                        if await web_link.is_visible(timeout=350):
                            website = await web_link.get_attribute("href") or ""

                        rating = None
                        reviews_count = None
                        try:
                            rev_btn = page.locator('button[aria-label*="reviews"]').first
                            if await rev_btn.is_visible(timeout=350):
                                rev_text = await rev_btn.inner_text()
                                m_rev = re.search(r'([\d\.,]+)', rev_text)
                                if m_rev:
                                    reviews_count = int(m_rev.group(1).replace(",", "").replace(".", ""))

                            rating_el = page.locator('div.F7263c, div.fontBodyMedium span[aria-hidden="true"]').first
                            if await rating_el.is_visible(timeout=350):
                                r_txt = await rating_el.inner_text()
                                if re.match(r'^\d+[\.,]\d+$', r_txt.strip()):
                                    rating = float(r_txt.strip().replace(',', '.'))
                        except Exception:
                            pass

                        lead = {
                            "name": name,
                            "category": category or "Perfume Store",
                            "rating": rating,
                            "reviews_count": reviews_count,
                            "phone": phone,
                            "email": "",
                            "website": website,
                            "address": address,
                            "city": city or location.split(",")[0],
                            "postal_code": postal_code,
                            "country": country,
                            "latitude": lat,
                            "longitude": lng,
                            "facebook": "",
                            "instagram": "",
                            "linkedin": "",
                            "twitter": "",
                            "place_id": dedup_key,
                            "url": href if href.startswith("http") else f"https://www.google.com{href}"
                        }

                        async with global_state["lock"]:
                            global_state["all_leads"].append(lead)
                            total_now = len(global_state["all_leads"])
                            logger.info(f"[Worker {worker_id}] [{total_now}/{global_state['target']}] ✅ {name} | {city or location} | {phone}")

                            if total_now % 50 == 0:
                                export_data(list(global_state["all_leads"]), output_filename)
                                logger.info(f"💾 Auto-checkpoint saved: {total_now} leads written to Excel/CSV.")

                            if total_now >= global_state["target"]:
                                global_state["stop_event"].set()
                                break

                    except Exception:
                        continue

            except Exception:
                continue

    await context.close()

async def async_main(target_total_leads: int = 30000, num_workers: int = 128):
    output_filename = f"ALL_US_Perfume_Stores_{target_total_leads}_Leads"

    logger.info("=" * 80)
    logger.info(f" 🚀 EXTREME 128-WORKER ALL-USA PERFUME & FRAGRANCE SCRAPER LAUNCHED")
    logger.info(f" ⚡ Target: {target_total_leads} Leads | Parallel Browser Workers: {num_workers}")
    logger.info(f" 📍 Geographic Scope: 350+ Cities covering all 50 US States")
    logger.info("=" * 80)

    global_state = {
        "all_leads": [],
        "seen_keys": set(),
        "target": target_total_leads,
        "lock": asyncio.Lock(),
        "stop_event": asyncio.Event()
    }

    chunk_size = (len(US_LOCATIONS) + num_workers - 1) // num_workers
    worker_location_chunks = [
        US_LOCATIONS[i * chunk_size : (i + 1) * chunk_size]
        for i in range(num_workers)
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_ARGS)

        tasks = [
            async_worker(i + 1, worker_location_chunks[i], browser, global_state, output_filename)
            for i in range(min(num_workers, len(worker_location_chunks)))
            if worker_location_chunks[i]
        ]

        await asyncio.gather(*tasks)
        await browser.close()

    all_leads = global_state["all_leads"]
    logger.info(f"🎉 Scraping phase complete. Total unique leads collected: {len(all_leads)}")

    # High-performance Parallel Web Intelligence Enrichment (350 concurrent async HTTP connections)
    logger.info(f"⚡ Starting 350-worker deep async web enrichment for corporate emails & socials...")
    sem = asyncio.Semaphore(350)
    headers = {
        "User-Agent": USER_AGENTS[0],
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(headers=headers, verify=False, timeout=5.0) as client:
        enrich_tasks = [
            async_enrich_single_website(client, lead["website"], sem)
            if lead.get("website") else None
            for lead in all_leads
        ]

        results = await asyncio.gather(*[t for t in enrich_tasks if t is not None])
        res_idx = 0
        for i, lead in enumerate(all_leads):
            if lead.get("website"):
                web_data = results[res_idx]
                res_idx += 1
                all_leads[i]["email"] = web_data.get("email", "")
                all_leads[i]["facebook"] = web_data.get("facebook", "")
                all_leads[i]["instagram"] = web_data.get("instagram", "")
                all_leads[i]["linkedin"] = web_data.get("linkedin", "")
                all_leads[i]["twitter"] = web_data.get("twitter", "")

    excel_file, csv_file = export_data(all_leads, output_filename)
    logger.info("=" * 80)
    logger.info(f"🎉 ALL-USA SCRAPING & ENRICHMENT COMPLETED SUCCESSFULLY!")
    logger.info(f"📁 FINAL EXCEL SAVED AT: {excel_file}")
    logger.info(f"📁 FINAL CSV SAVED AT:   {csv_file}")
    logger.info("=" * 80)
    return all_leads

if __name__ == "__main__":
    count = 30000
    workers = 128
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        count = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        workers = int(sys.argv[2])
    asyncio.run(async_main(target_total_leads=count, num_workers=workers))



