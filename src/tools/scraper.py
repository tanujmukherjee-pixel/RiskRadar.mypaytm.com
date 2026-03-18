"""Async web scraper for merchant website data extraction."""

import asyncio
from typing import List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from ..domains.mcc import ScrapedData

SCRAPE_CONCURRENCY = 5
SCRAPE_TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def _normalise_url(url: str) -> str:
    """Ensure URL has a scheme."""
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def _extract_data(url: str, html: str) -> ScrapedData:
    """Parse HTML and extract merchant signals."""
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_description = (
        meta_desc.get("content", "").strip() if meta_desc else None  # type: ignore[union-attr]
    )

    meta_kw = soup.find("meta", attrs={"name": "keywords"})
    meta_keywords = (
        meta_kw.get("content", "").strip() if meta_kw else None  # type: ignore[union-attr]
    )

    h1_tags = [t.get_text(strip=True) for t in soup.find_all("h1")][:5]
    h2_tags = [t.get_text(strip=True) for t in soup.find_all("h2")][:5]

    return ScrapedData(
        url=url,
        title=title,
        meta_description=meta_description,
        meta_keywords=meta_keywords,
        h1_tags=h1_tags,
        h2_tags=h2_tags,
    )


def _find_about_url(base_url: str, html: str) -> str | None:
    """Try to find an about/company page link."""
    soup = BeautifulSoup(html, "html.parser")
    about_keywords = ("/about", "/about-us", "/company", "/who-we-are", "/our-story")
    for tag in soup.find_all("a", href=True):
        raw_href = tag["href"]
        href = str(raw_href).lower()
        if any(kw in href for kw in about_keywords):
            return urljoin(base_url, str(raw_href))
    return None


async def _scrape_one(
    client: httpx.AsyncClient, sem: asyncio.Semaphore, url: str
) -> ScrapedData:
    """Scrape a single URL with concurrency control."""
    url = _normalise_url(url)
    async with sem:
        try:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            data = _extract_data(url, resp.text)

            # Optionally fetch about page for richer context
            about_url = _find_about_url(url, resp.text)
            if about_url and about_url != url:
                try:
                    about_resp = await client.get(about_url, follow_redirects=True)
                    if about_resp.status_code == 200:
                        about_soup = BeautifulSoup(about_resp.text, "html.parser")
                        body = about_soup.get_text(separator=" ", strip=True)
                        data.about_content = body[:1500]
                except Exception:  # noqa: BLE001
                    pass

            return data
        except Exception as exc:  # noqa: BLE001
            return ScrapedData(url=url, error=str(exc))


async def scrape_urls(urls: List[str]) -> List[ScrapedData]:
    """Scrape a list of merchant URLs concurrently."""
    sem = asyncio.Semaphore(SCRAPE_CONCURRENCY)
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"}
    async with httpx.AsyncClient(
        timeout=SCRAPE_TIMEOUT, headers=headers, verify=False
    ) as client:
        tasks = [_scrape_one(client, sem, url) for url in urls]
        return await asyncio.gather(*tasks)
