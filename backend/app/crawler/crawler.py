import asyncio
import logging
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from typing import List, Set, Dict, Optional, Callable, Awaitable
import httpx

from app.config import (
    CRAWLER_USER_AGENT,
    DEFAULT_CRAWL_DELAY,
    DEFAULT_REQUEST_TIMEOUT,
    MAX_CRAWL_RETRIES
)
from app.crawler.models import CrawledDocument
from app.crawler.parser import HTMLCleaner, extract_domain

logger = logging.getLogger("crawler")

class AsyncCrawler:
    def __init__(
        self,
        user_agent: str = CRAWLER_USER_AGENT,
        request_delay: float = DEFAULT_CRAWL_DELAY,
        timeout: float = DEFAULT_REQUEST_TIMEOUT,
        max_retries: int = MAX_CRAWL_RETRIES,
        max_concurrency: int = 5
    ):
        self.user_agent = user_agent
        self.request_delay = request_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.robot_parsers: Dict[str, RobotFileParser] = {}
        self.domain_last_request: Dict[str, float] = {}

    async def _get_robot_parser(self, client: httpx.AsyncClient, domain: str, scheme: str) -> Optional[RobotFileParser]:
        if domain in self.robot_parsers:
            return self.robot_parsers[domain]

        robots_url = f"{scheme}://{domain}/robots.txt"
        rp = RobotFileParser()
        try:
            resp = await client.get(robots_url, timeout=5.0)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                rp.allow_all = True
        except Exception:
            rp.allow_all = True

        self.robot_parsers[domain] = rp
        return rp

    async def is_allowed(self, client: httpx.AsyncClient, url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        rp = await self._get_robot_parser(client, parsed.netloc, parsed.scheme)
        return rp.can_fetch(self.user_agent, url)

    async def fetch_page(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = await client.get(url, headers=headers, follow_redirects=True, timeout=self.timeout)
                if resp.status_code == 200:
                    content_type = resp.headers.get("content-type", "").lower()
                    if "text/html" in content_type or "application/xhtml" in content_type or not content_type:
                        return resp.text
                    else:
                        logger.info(f"Skipping non-HTML content-type '{content_type}' at {url}")
                        return None
                elif resp.status_code in (404, 410, 403):
                    logger.warning(f"Failed {url} with status {resp.status_code}")
                    return None
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt == self.max_retries:
                    logger.warning(f"Error fetching {url} after {attempt} attempts: {e}")
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
        return None

    async def crawl_urls(
        self,
        seed_urls: List[str],
        max_depth: int = 1,
        max_pages: int = 25,
        on_document_crawled: Optional[Callable[[CrawledDocument], Awaitable[None]]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ) -> List[CrawledDocument]:
        visited: Set[str] = set()
        queue: List[tuple[str, int]] = [(url, 0) for url in seed_urls]
        results: List[CrawledDocument] = []

        limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
        async with httpx.AsyncClient(limits=limits, verify=False) as client:
            while queue and len(results) < max_pages:
                url, depth = queue.pop(0)
                norm_url = url.split("#")[0].rstrip("/")
                if not norm_url or norm_url in visited:
                    continue
                visited.add(norm_url)

                async with self.semaphore:
                    # Respect rate-limit delay
                    domain = extract_domain(url)
                    await asyncio.sleep(self.request_delay)

                    # Check robots.txt
                    try:
                        allowed = await self.is_allowed(client, url)
                        if not allowed:
                            msg = f"Disallowed by robots.txt: {url}"
                            logger.info(msg)
                            if on_error:
                                on_error(msg)
                            continue
                    except Exception as e:
                        logger.debug(f"Robots check error for {url}: {e}")

                    # Fetch page
                    try:
                        html = await self.fetch_page(client, url)
                        if not html:
                            continue

                        doc = HTMLCleaner.clean_and_parse(html, url)
                        if len(doc.body_text) < 50:
                            # Too short or empty
                            continue

                        results.append(doc)

                        if on_document_crawled:
                            await on_document_crawled(doc)

                        # Discover links if depth allows
                        if depth < max_depth and len(results) < max_pages:
                            links = self._extract_links(html, url)
                            for link in links:
                                if link not in visited:
                                    queue.append((link, depth + 1))

                    except Exception as e:
                        err_msg = f"Error processing {url}: {str(e)}"
                        logger.error(err_msg)
                        if on_error:
                            on_error(err_msg)

        return results

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        links = []
        base_domain = extract_domain(base_url)

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            full_url = urljoin(base_url, href)
            # Only same-domain links during recursive crawl
            if extract_domain(full_url) == base_domain:
                clean = full_url.split("#")[0].rstrip("/")
                if clean.startswith("http"):
                    links.append(clean)
        return links
