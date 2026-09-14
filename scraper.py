"""
Scraper for uetmardan.edu.pk.

Crawls the site ONE time (the old two-script version crawled it twice —
once for pages, once to find PDF links — which is slower and can find a
different set of links if the site changes between the two runs).

For every internal page found:
  - saves cleaned page text to data/raw/<slug>.txt
For every PDF link found:
  - downloads it to data/pdfs/<slug>.pdf
  - extracts its text to data/raw/<slug>_pdf.txt (skipped if the PDF has
    no extractable text, e.g. a scanned image)

Writes one data/raw/manifest.json describing every text file produced,
which build_index.py reads to attach source URLs and fetch dates to each
chunk.

Run:
    python scraper.py
"""

import json
import os
import re
import time
from collections import deque
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

BASE_URL = "https://www.uetmardan.edu.pk"
START_PATH = "/uetm/"

RAW_DIR = "data/raw"
PDF_DIR = "data/pdfs"
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

MAX_PAGES = 800
DELAY_SECONDS = 1
MIN_PAGE_TEXT_CHARS = 50
MIN_PDF_TEXT_CHARS = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

SKIP_KEYWORDS = (
    "javascript:", "mailto:", ".jpg", ".jpeg", ".png", ".gif", "logout", "login", "#",
    "news_detail", "news_archive", "event_detail", "events_archive",
    "press_release", "/tender", "/gallery",
)


def is_internal(url):
    netloc = urlparse(url).netloc
    return netloc == "" or "uetmardan.edu.pk" in netloc


def normalize(url):
    return url.split("#")[0].rstrip("/")


def looks_like_real_href(href):
    """Reject anchor tags where the site's markup has embedded extra text
    or a bare external domain instead of a clean relative/absolute URL
    (e.g. href="Google Scholar: https://scholar.google.com/..." or a bare
    "linkedin.com/in/..." with no scheme)."""
    if " " in href:
        return False
    if href.startswith(("http://", "https://", "/")):
        return True
    return False


def clean_filename(url_path):
    name = url_path.strip("/").replace("/", "_")
    name = name if name else "home"
    name = re.sub(r'[<>:"|?*]', "_", name)  # strip Windows-illegal filename characters
    if len(name) > 150:
        name = name[:150]
    return name


def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(parts).strip()


def download_pdf(pdf_url, manifest, now):
    slug = clean_filename(urlparse(pdf_url).path)
    pdf_path = os.path.join(PDF_DIR, slug + ".pdf")

    try:
        resp = requests.get(pdf_url, timeout=30, headers=HEADERS)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"PDF FAILED (download): {pdf_url} -> {e}")
        return

    with open(pdf_path, "wb") as f:
        f.write(resp.content)

    try:
        text = extract_pdf_text(pdf_path)
    except Exception as e:
        print(f"PDF FAILED (extract): {pdf_url} -> {e}")
        return

    if len(text) < MIN_PDF_TEXT_CHARS:
        print(f"PDF SKIPPED (no extractable text, likely scanned): {pdf_url}")
        return

    txt_filename = slug + "_pdf.txt"
    with open(os.path.join(RAW_DIR, txt_filename), "w", encoding="utf-8") as f:
        f.write(text)

    manifest.append({
        "filename": txt_filename,
        "url": pdf_url,
        "doc_type": "pdf",
        "fetched_at": now,
    })
    print(f"PDF SAVED: {pdf_url}")


def crawl():
    visited = set()
    to_visit = deque([START_PATH])
    manifest = []
    seen_pdf_urls = set()
    now = datetime.now(timezone.utc).isoformat()

    while to_visit and len(visited) < MAX_PAGES:
        path = to_visit.popleft()
        full_url = urljoin(BASE_URL, path)
        norm = normalize(full_url)
        if norm in visited:
            continue
        visited.add(norm)

        try:
            resp = requests.get(full_url, timeout=20, headers=HEADERS)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"FAILED: {full_url} -> {e}")
            time.sleep(DELAY_SECONDS)
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        base_tag = soup.find("base", href=True)
        resolve_base = urljoin(full_url, base_tag["href"]) if base_tag else full_url

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not looks_like_real_href(href):
                continue
            if href.lower().endswith(".pdf"):
                joined = urljoin(resolve_base, href)
                if is_internal(joined):
                    seen_pdf_urls.add(joined)
                continue
            if any(kw in href.lower() for kw in SKIP_KEYWORDS):
                continue
            joined = urljoin(resolve_base, href)
            if is_internal(joined) and normalize(joined) not in visited:
                to_visit.append(joined)

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        title = soup.title.string.strip() if soup.title else path
        lines = [ln.strip() for ln in soup.get_text(separator="\n").splitlines() if ln.strip()]
        clean_text = "\n".join(lines)

        if len(clean_text) >= MIN_PAGE_TEXT_CHARS:
            filename = clean_filename(urlparse(full_url).path) + ".txt"
            with open(os.path.join(RAW_DIR, filename), "w", encoding="utf-8") as f:
                f.write(clean_text)
            manifest.append({
                "filename": filename,
                "url": full_url,
                "title": title,
                "doc_type": "html",
                "fetched_at": now,
            })
            print(f"SAVED ({len(visited)}): {full_url}")
        else:
            print(f"SKIPPED (too little content): {full_url}")

        time.sleep(DELAY_SECONDS)

    print(f"\nCrawled {len(visited)} pages. Found {len(seen_pdf_urls)} PDF links. Downloading...\n")
    for pdf_url in seen_pdf_urls:
        download_pdf(pdf_url, manifest, now)
        time.sleep(DELAY_SECONDS)

    with open(os.path.join(RAW_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nDone. {len(manifest)} documents saved to {RAW_DIR}/. See manifest.json.")


if __name__ == "__main__":
    crawl()