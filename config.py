import os

# General Settings
DEFAULT_HEADLESS = True
DEFAULT_TIMEOUT = 35000  # ms
MAX_RESULTS_DEFAULT = 20

# Stochastic delays (seconds) to prevent rate limits
MIN_DELAY = 1.2
MAX_DELAY = 2.8

# Google Maps Settings (Default interface set to English)
GMAPS_BASE_URL = "https://www.google.com/maps/search/{query}/?hl={lang}"
DEFAULT_LANG = "en"

# Chromium Stealth & Hardware GPU Acceleration Arguments
CHROMIUM_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-infobars",
    "--disable-popup-blocking",
    "--disable-notifications",
    "--lang=en-US,en",
    "--ignore-gpu-blocklist",
    "--enable-gpu-rasterization",
    "--enable-zero-copy",
    "--enable-accelerated-2d-canvas",
    "--enable-features=VaapiVideoDecoder,CanvasOopRasterization"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]

# Multilingual Cookie Consent Selectors (Prioritizing English)
COOKIE_SELECTORS = [
    '//button[contains(., "Accept all")]',
    '//button[contains(., "I agree")]',
    'button[aria-label*="Accept"]',
    'button[aria-label*="Aceptar"]',
    'button[aria-label*="Aceitar"]',
    'form[action*="consent"] button',
    '//button[contains(., "Aceptar todo")]',
    '//button[contains(., "Aceitar tudo")]',
    '//button[contains(., "Tout accepter")]'
]

# Comprehensive Contact Page Paths for Deep Web Crawling (including Shopify, WordPress, WooCommerce)
CONTACT_PATHS = [
    "",
    "/contact",
    "/contact-us",
    "/pages/contact",
    "/pages/contact-us",
    "/about",
    "/about-us",
    "/pages/about",
    "/pages/about-us",
    "/policies/privacy-policy",
    "/policies/terms-of-service",
    "/privacy-policy",
    "/terms-of-service",
    "/customer-service",
    "/help",
    "/faq",
    "/pages/faq",
    "/contacto",
    "/nosotros"
]


# Social Media Regex Patterns
SOCIAL_PATTERNS = {
    "facebook": r"https?://(?:www\.)?(?:facebook\.com|fb\.com)/[A-Za-z0-9\.\_\-]+",
    "instagram": r"https?://(?:www\.)?instagram\.com/[A-Za-z0-9\.\_\-]+",
    "linkedin": r"https?://(?:www\.)?linkedin\.com/(?:company|in)/[A-Za-z0-9\.\_\-]+",
    "twitter": r"https?://(?:www\.)?(?:twitter\.com|x\.com)/[A-Za-z0-9\.\_\-]+"
}

# Output Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
