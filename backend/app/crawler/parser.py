import re
import hashlib
from urllib.parse import urlparse
from typing import Optional, List
from bs4 import BeautifulSoup
from app.crawler.models import CrawledDocument

def generate_doc_id(url: str) -> str:
    return hashlib.sha256(url.strip().encode("utf-8")).hexdigest()[:16]

def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc

class HTMLCleaner:
    @staticmethod
    def clean_and_parse(html_content: str, source_url: str) -> CrawledDocument:
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Remove unwanted tags
        for unwanted in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "aside", "form"]):
            unwanted.decompose()

        # 2. Extract Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        if not title:
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
        if not title:
            title = source_url

        # 3. Extract Meta Description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        # 4. Extract Canonical URL
        canonical_url = None
        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag and canonical_tag.get("href"):
            canonical_url = canonical_tag["href"].strip()

        # 5. Extract Headings (h1-h6)
        headers = []
        for h in soup.find_all(re.compile(r"^h[1-6]$")):
            text = h.get_text(strip=True)
            if text and len(text) < 200:
                headers.append(text)

        # 6. Extract Main Body Text
        # Try finding main article container
        main_container = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|body|post", re.I))
        if not main_container:
            main_container = soup.body or soup

        # Extract text preserving line breaks
        text = main_container.get_text(separator=" ", strip=True)
        # Collapse multiple spaces and line breaks
        cleaned_text = re.sub(r"\s+", " ", text).strip()

        doc_id = generate_doc_id(source_url)
        domain = extract_domain(source_url)

        return CrawledDocument(
            id=doc_id,
            url=source_url,
            domain=domain,
            title=title,
            meta_description=meta_desc,
            canonical_url=canonical_url or source_url,
            body_text=cleaned_text,
            headers=headers[:10],
            raw_html_length=len(html_content)
        )

def parse_local_document(file_path: str, source_url: Optional[str] = None) -> CrawledDocument:
    """Parses local .txt, .md, or .pdf files"""
    import os
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document at {file_path} not found.")

    ext = os.path.splitext(file_path)[1].lower()
    title = os.path.basename(file_path)
    url = source_url or f"file:///{file_path.replace(os.sep, '/')}"
    body = ""

    if ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            body = f.read()
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            pages_text = [page.extract_text() or "" for page in reader.pages]
            body = " ".join(pages_text)
        except Exception as e:
            body = f"PDF read error: {str(e)}"

    body = re.sub(r"\s+", " ", body).strip()
    doc_id = generate_doc_id(url)
    domain = "local.docs"

    return CrawledDocument(
        id=doc_id,
        url=url,
        domain=domain,
        title=title,
        body_text=body,
        raw_html_length=len(body)
    )
