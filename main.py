from fastapi import FastAPI, Query
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests

app = FastAPI()

EXCLUDE = [
    "contact", "about", "privacy", "terms", "legal", "cookie",
    "careers", "jobs", "login", "signup", "signin", "register",
    "account", "support", "help", "faq", "sitemap","wp"
]

MAX_PAGES = 20


# ------------------------------------
# HELPERS
# ------------------------------------
def is_internal(link, domain):
    return urlparse(link).netloc == domain

def is_relevant(url):
    url = url.lower()
    return not any(x in url for x in EXCLUDE)

def normalize(url):
    parsed = urlparse(url)
    clean = parsed.scheme + "://" + parsed.netloc + parsed.path.rstrip("/")
    return clean

def fetch_html(url):
    try:
        r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return r.text
    except:
        return None
    return None


# ------------------------------------
# API ENDPOINT
# ------------------------------------
@app.get("/internal-pages")
def get_internal_pages(website: str = Query(..., description="Homepage URL")):
    homepage_clean = normalize(website)
    domain = urlparse(homepage_clean).netloc

    html = fetch_html(homepage_clean)
    if not html:
        return {"error": "Unable to fetch website"}

    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for a in soup.find_all("a", href=True):
        raw = a["href"].strip()
        full = urljoin(homepage_clean, raw)
        clean = normalize(full)

        if is_internal(clean, domain) and is_relevant(clean):
            links.add(clean)

    # Ensure homepage is first
    links = list(links)
    links = [homepage_clean] + [u for u in links if u != homepage_clean]

    links = links[:MAX_PAGES]

    # Convert list → dictionary format
    result = {str(i + 1): links[i] for i in range(len(links))}

    return result
