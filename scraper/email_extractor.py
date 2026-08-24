import re
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
from config import CONTACT_PATHS, USER_AGENTS
from utils.logger import logger

# Patrón Regex robusto para emails
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}")

# Dominios / Extensiones irrelevantes a ignorar
IGNORED_DOMAINS = {
    "sentry.io", "wixpress.com", "example.com", "schema.org", "domain.com",
    "png", "jpg", "jpeg", "svg", "gif", "webp"
}

def clean_url(url: str) -> str:
    """Asegura esquema http/https en la URL."""
    if not url:
        return ""
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        return f"https://{url}"
    return url

def is_valid_email(email: str) -> bool:
    """Filtra falsos positivos de emails (imágenes, fuentes, esquemas)."""
    email_lower = email.lower()
    ext = email_lower.split(".")[-1]
    if ext in IGNORED_DOMAINS:
        return False
    for domain in IGNORED_DOMAINS:
        if domain in email_lower:
            return False
    return True

def extract_email_from_website(website_url: str, timeout: float = 4.0) -> str:
    """
    Rastrea el sitio web oficial y subpáginas de contacto para extraer el primer email válido.
    """
    url = clean_url(website_url)
    if not url:
        return ""

    # Omitir redes sociales comunes donde no se puede raspar fácil
    social_domains = ["facebook.com", "instagram.com", "twitter.com", "linkedin.com", "youtube.com", "wa.me", "t.me"]
    if any(sd in url.lower() for sd in social_domains):
        return ""

    headers = {
        "User-Agent": USER_AGENTS[0],
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    found_emails = set()

    with httpx.Client(headers=headers, follow_redirects=True, timeout=timeout, verify=False) as client:
        for path in CONTACT_PATHS:
            try:
                target_url = urljoin(url, path) if path else url
                response = client.get(target_url)
                if response.status_code == 200:
                    text = response.text
                    matches = EMAIL_REGEX.findall(text)
                    for match in matches:
                        if is_valid_email(match):
                            found_emails.add(match)

                    # Si encontramos emails en esta ruta, no necesitamos seguir escaneando subpáginas
                    if found_emails:
                        email_list = sorted(list(found_emails))
                        logger.info(f"Email(s) encontrado(s) en {target_url}: {', '.join(email_list)}")
                        return email_list[0]
            except Exception:
                # Ignorar errores de conexión/timeout en subpáginas para mantener velocidad
                continue

    return ""
