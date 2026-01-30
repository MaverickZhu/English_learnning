import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


@dataclass
class NewsSourceConfig:
    name: str
    site_url: str
    list_url: str
    allow_prefixes: tuple[str, ...]


DEFAULT_SOURCES: list[NewsSourceConfig] = [
    NewsSourceConfig(
        name="bbc",
        site_url="https://www.bbc.com/news",
        list_url="https://www.bbc.com/news",
        allow_prefixes=("https://www.bbc.com/news", "https://bbc.com/news"),
    ),
    NewsSourceConfig(
        name="nytimes",
        site_url="https://www.nytimes.com",
        list_url="https://www.nytimes.com",
        allow_prefixes=("https://www.nytimes.com",),
    ),
    NewsSourceConfig(
        name="cnn",
        site_url="https://www.cnn.com",
        list_url="https://www.cnn.com",
        allow_prefixes=("https://www.cnn.com",),
    ),
    NewsSourceConfig(
        name="aljazeera",
        site_url="https://www.aljazeera.com",
        list_url="https://www.aljazeera.com",
        allow_prefixes=("https://www.aljazeera.com",),
    ),
]


def _normalize_url(base: str, href: str) -> str | None:
    if not href:
        return None
    if href.startswith("//"):
        href = "https:" + href
    if href.startswith("/"):
        return urljoin(base, href)
    return href


def _is_article_url(url: str, allow_prefixes: tuple[str, ...]) -> bool:
    if not url or not url.startswith("http"):
        return False
    if not any(url.startswith(prefix) for prefix in allow_prefixes):
        return False
    parsed = urlparse(url)
    if parsed.path in {"", "/"}:
        return False
    if "bbc.com" in parsed.netloc:
        if parsed.path.rstrip("/") == "/news":
            return False
    if "aljazeera.com" in parsed.netloc:
        if not parsed.path.startswith("/news/"):
            return False
        if parsed.path.rstrip("/") == "/news":
            return False
    if "cnn.com" in parsed.netloc:
        segments = [seg for seg in parsed.path.split("/") if seg]
        if len(segments) <= 1:
            return False
    if "nytimes.com" in parsed.netloc:
        if parsed.path.startswith("/section/"):
            return False
    if "/video" in parsed.path or "/live" in parsed.path:
        return False
    return True


def _parse_rss_links(xml_text: str, limit: int) -> list[str]:
    soup = BeautifulSoup(xml_text, "xml")
    links: list[str] = []
    seen = set()
    for item in soup.find_all("item"):
        link_tag = item.find("link")
        if not link_tag or not link_tag.text:
            continue
        url = link_tag.text.strip()
        if not url or url in seen:
            continue
        seen.add(url)
        links.append(url)
        if len(links) >= limit:
            break
    if links:
        return links
    for entry in soup.find_all("entry"):
        link_tag = entry.find("link")
        url = None
        if link_tag is not None:
            url = link_tag.get("href") or link_tag.text
        if not url:
            continue
        url = url.strip()
        if not url or url in seen:
            continue
        seen.add(url)
        links.append(url)
        if len(links) >= limit:
            break
    return links


def _extract_links_from_text(source: NewsSourceConfig, text: str, limit: int) -> list[str]:
    head = text[:200].lower()
    if "<rss" in head or "<feed" in head:
        urls = _parse_rss_links(text, limit)
        return [url for url in urls if _is_article_url(url, source.allow_prefixes)]
    soup = BeautifulSoup(text, "lxml")
    links: list[str] = []
    seen = set()
    for a in soup.find_all("a", href=True):
        url = _normalize_url(source.site_url, a["href"])
        if not url or not _is_article_url(url, source.allow_prefixes):
            continue
        url = re.sub(r"[?#].*$", "", url)
        if url in seen:
            continue
        seen.add(url)
        links.append(url)
        if len(links) >= limit:
            break
    return links


def fetch_top_article_urls(source: NewsSourceConfig, limit: int = 5, timeout: float = 12.0) -> list[str]:
    headers = {"User-Agent": "EnglishLearningBot/1.0"}
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        resp = client.get(source.list_url)
        resp.raise_for_status()
    return _extract_links_from_text(source, resp.text, limit)
