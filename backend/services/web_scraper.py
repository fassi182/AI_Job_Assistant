"""
Fetches and cleans text content from a job posting URL (or a company
website) using requests + BeautifulSoup.
"""
from typing import Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def normalize_url(url: str) -> str:
    """Normalize a user-provided URL by adding https:// if missing."""
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url.lstrip('/')}"
        parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"URL must use http or https: {url}")
    if not parsed.netloc or parsed.netloc.startswith(":") or parsed.netloc.endswith("."):
        raise ValueError(f"Invalid URL: {url}")
    return url


def fetch_page_text(url: str, timeout: int = 15) -> str:
    """Fetches a URL and returns cleaned visible text content."""
    url = normalize_url(url)
    response = requests.get(url, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned


def guess_company_homepage(job_url: str) -> Optional[str]:
    """Best-effort guess of a company's homepage from a job posting URL's
    domain. Returns None if it looks like a generic job-board domain."""
    job_boards = {"linkedin.com", "indeed.com", "glassdoor.com", "lever.co", "greenhouse.io"}
    job_url = normalize_url(job_url)
    domain = urlparse(job_url).netloc.replace("www.", "")
    if any(board in domain for board in job_boards):
        return None
    return f"https://{domain}"
