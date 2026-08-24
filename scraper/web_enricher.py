import re
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
from config import CONTACT_PATHS, USER_AGENTS, SOCIAL_PATTERNS
from utils.logger import logger

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}")

IGNORED_DOMAINS = {
    "sentry.io", "wixpress.com", "example.com", "schema.org", "domain.com",
    "png", "jpg", "jpeg", "svg", "gif", "webp"
}

def clean_url(url: str) -> str:
    """Ensures http/https scheme on URL."""
    if not url:
        return ""
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        return f"https://{url}"
    return url

def is_valid_email(email: str) -> bool:
    """Filters out false positive emails (image filenames, font files, schema tags)."""
    email_lower = email.lower()
    ext = email_lower.split(".")[-1]
    if ext in IGNORED_DOMAINS:
        return False
    for domain in IGNORED_DOMAINS:
        if domain in email_lower:
            return False
    return True

def extract_social_links(html_text: str) -> dict[str, str]:
    """Extracts Facebook, Instagram, LinkedIn, and Twitter profile links from page HTML."""
    socials = {"facebook": "", "instagram": "", "linkedin": "", "twitter": ""}

    for platform, pattern in SOCIAL_PATTERNS.items():
        matches = re.findall(pattern, html_text, re.IGNORECASE)
        for link in matches:
            link_lower = link.lower()
            # Exclude share/intent links
            if any(share_word in link_lower for share_word in ["sharer", "share", "intent", "plugins", "dialog"]):
                continue
            # Format clean link
            socials[platform] = link.rstrip("/")
            break

    return socials

def enrich_business_web_data(website_url: str, timeout: float = 4.0) -> dict:
    """
    Crawls the official business website and contact subpages to extract emails and social media profiles.
    Returns: {"email": str, "facebook": str, "instagram": str, "linkedin": str, "twitter": str}
    """
    data = {
        "email": "",
        "facebook": "",
        "instagram": "",
        "linkedin": "",
        "twitter": ""
    }

    url = clean_url(website_url)
    if not url:
        return data

    # Skip social media links directly set as business websites
    social_domains = ["facebook.com", "instagram.com", "twitter.com", "linkedin.com", "youtube.com", "wa.me", "t.me"]
    if any(sd in url.lower() for sd in social_domains):
        return data

    headers = {
        "User-Agent": USER_AGENTS[0],
        "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    found_emails = set()

    with httpx.Client(headers=headers, follow_redirects=True, timeout=timeout, verify=False) as client:
        for path in CONTACT_PATHS:
            try:
                target_url = urljoin(url, path) if path else url
                response = client.get(target_url)
                if response.status_code == 200:
                    html_text = response.text

                    # 1. Extract Emails
                    email_matches = EMAIL_REGEX.findall(html_text)
                    for match in email_matches:
                        if is_valid_email(match):
                            found_emails.add(match)

                    # 2. Extract Social Links (if not found yet)
                    page_socials = extract_social_links(html_text)
                    for key, val in page_socials.items():
                        if not data[key] and val:
                            data[key] = val

                    # If we found email and all social links, stop crawling further paths
                    if found_emails and all(data[k] for k in ["facebook", "instagram", "linkedin", "twitter"]):
                        break
            except Exception:
                continue

    if found_emails:
        data["email"] = sorted(list(found_emails))[0]

    return data
