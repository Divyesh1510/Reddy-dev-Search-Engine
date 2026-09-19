import pytest
from app.crawler.parser import HTMLCleaner, extract_domain, generate_doc_id
from app.crawler.models import CrawledDocument

def test_generate_doc_id():
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page1"
    url3 = "https://example.com/page2"
    assert generate_doc_id(url1) == generate_doc_id(url2)
    assert generate_doc_id(url1) != generate_doc_id(url3)

def test_extract_domain():
    assert extract_domain("https://www.example.com/path?q=1") == "example.com"
    assert extract_domain("http://sub.domain.org/index.html") == "sub.domain.org"

def test_html_cleaner():
    html_raw = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page Title</title>
        <meta name="description" content="This is a test description for search engines.">
        <link rel="canonical" href="https://example.com/canonical-test">
        <style>body { color: red; }</style>
        <script>console.log('strip this script');</script>
    </head>
    <body>
        <nav><a href="/home">Home</a></nav>
        <main>
            <h1>Main Heading</h1>
            <p>This is the first paragraph with important information about Python search engines.</p>
            <h2>Sub Heading</h2>
            <p>Another paragraph detailing SQLite FTS5 and vector indexing mechanisms.</p>
        </main>
        <footer>Copyright 2026</footer>
    </body>
    </html>
    """

    doc = HTMLCleaner.clean_and_parse(html_raw, "https://example.com/page1")
    assert doc.title == "Test Page Title"
    assert doc.meta_description == "This is a test description for search engines."
    assert doc.canonical_url == "https://example.com/canonical-test"
    assert "strip this script" not in doc.body_text
    assert "body { color: red; }" not in doc.body_text
    assert "Python search engines" in doc.body_text
    assert "Main Heading" in doc.headers
    assert "Sub Heading" in doc.headers
    assert doc.domain == "example.com"
