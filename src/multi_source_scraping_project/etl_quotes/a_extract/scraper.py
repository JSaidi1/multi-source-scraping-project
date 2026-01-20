"""
Scraper for the Quotes website.
main functions:
    scrape_all_quotes(): Scrape all the quotes with pagination.
"""

import re
from typing import Optional, Generator
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from config.settings import app_cfg, scraper_config
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.utils_logs import log_message
from etl_quotes.models.raw_models.raw_quote import RawQuote


class QuotesScraper:
    """
    Scraper for the Quotes website.

    Feature:

    - Extract: capture raw data exactly from source and map it to the raw model.
    """
    def __init__(self):
        # === Set log cfg.
        self.debug_mode = app_cfg.debug_mode
        self.console_log = app_cfg.console_log
        self.file_log = app_cfg.file_log
        # === Set scraper cfg.
        self.base_url = scraper_config.base_url_quotes
        self.delay = scraper_config.delay
        self.session = requests.Session()
        self.ua = UserAgent()
        self._setup_session()

    def _setup_session(self) -> None:
        """Configure the HTTP session."""
        self.session.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        })

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _fetch(self, url: str) -> Optional[BeautifulSoup]:
        """
        Retrieve and parse a page.

        Args:
            url: URL to retrieve

        Returns:
            BeautifulSoup or None
        """
        try:
            log_message("info", f"fetching (url={url})", self.file_log, self.console_log, self.debug_mode)

            response = self.session.get(url, timeout=scraper_config.timeout)
            response.raise_for_status()

            # Politeness
            time.sleep(self.delay)

            return BeautifulSoup(response.content, "lxml")

        except requests.RequestException as e:
            log_message("error", f"request error: fetch failed for (url={url}): {e}", self.file_log, self.console_log, self.debug_mode)
        except Exception as e:
            log_message("error", f"unknown error: fetch failed for (url={url}): {e}", self.file_log, self.console_log, self.debug_mode)

    def _parse_quote(self, element) -> Optional[RawQuote]:
        """
        Parses a quote element.

        Args:
            element: BeautifulSoup element

        Returns:
            RawQuote object or None
        """
        try:
            # Quote text
            text_elem = element.find("span", class_="text")
            text = self._clean_text(text_elem.text) if text_elem else ""

            # Author
            author_elem = element.find("small", class_="author")
            author = author_elem.text.strip() if author_elem else "Unknown"

            # URL of the author
            author_link = element.find("a", href=True)
            author_url = ""
            if author_link and "/author/" in author_link["href"]:
                author_url = urljoin(self.base_url, author_link["href"])

            # Tags
            tags = []
            tags_div = element.find("div", class_="tags")
            if tags_div:
                tag_links = tags_div.find_all("a", class_="tag")
                tags = [tag.text.strip() for tag in tag_links]

            return RawQuote(
                text=text,
                author=author,
                author_url=author_url,
                tags=tags
            )

        except Exception as e:
            log_message("error", f"quote parse failed: {e}", self.file_log, self.console_log, self.debug_mode)
            return None

    def _clean_text(self, text: str) -> str:
        """Cleans up the text of a quote."""
        # Remove the decorative quotation marks
        text = text.strip()
        text = re.sub(r'^[""\u201c\u201d]+|[""\u201c\u201d]+$', '', text)
        return text.strip()

    def _get_next_page(self, soup: BeautifulSoup) -> Optional[str]:
        """Find the URL of the next page."""
        next_li = soup.find("li", class_="next")

        if next_li:
            next_link = next_li.find("a", href=True)
            if next_link:
                return urljoin(self.base_url, next_link["href"])

        return None

    def scrape_all_quotes(
            self,
            max_pages: int = None
    ) -> Generator[RawQuote, None, None]:
        """
        Scrape all the quotes with pagination.

        Args:
            max_pages: pages limit (None = all)

        Yields:
            Quote Objets
        """
        max_pages = max_pages or scraper_config.max_pages
        page = 1
        url = self.base_url

        while url and page <= max_pages:
            log_message("info", f"scraping page {page}", self.file_log, self.console_log, self.debug_mode)

            soup = self._fetch(url)
            if not soup:
                break

            # Parse page quotes
            quote_divs = soup.find_all("div", class_="quote")

            for div in quote_divs:
                raw_quote = self._parse_quote(div)
                if raw_quote:
                    # add utl_page
                    raw_quote.utl_page=url
                    # yield raw_quote
                    yield raw_quote

            # Next page
            url = self._get_next_page(soup)
            page += 1

    def close(self) -> None:
        """Close the session."""
        self.session.close()
