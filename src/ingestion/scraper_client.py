"""Robots-aware public page fetcher for optional publisher pages."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ScrapedPage:
    url: str
    title: str
    text: str


class RobotsAwareScraper:
    """Fetch public pages only when robots.txt allows it."""

    user_agent: str = "apple-news-intelligence-platform"

    def can_fetch(self, url: str) -> bool:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            parser.read()
            return parser.can_fetch(self.user_agent, url)
        except Exception as exc:
            logger.warning("Could not read robots.txt for %s: %s", url, exc)
            return False

    def fetch_page(self, url: str) -> ScrapedPage | None:
        if not self.can_fetch(url):
            logger.info("Skipping disallowed URL by robots.txt: %s", url)
            return None
        try:
            import httpx
            from bs4 import BeautifulSoup

            response = httpx.get(url, headers={"User-Agent": self.user_agent}, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.get_text(" ", strip=True) if soup.title else url
            for tag in soup(["script", "style", "noscript"]):
                tag.extract()
            text = soup.get_text(" ", strip=True)
            return ScrapedPage(url=url, title=title, text=text)
        except Exception as exc:
            logger.warning("Scrape failed for %s: %s", url, exc)
            return None
