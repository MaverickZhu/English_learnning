import re
from dataclasses import dataclass
from datetime import datetime

import httpx
from bs4 import BeautifulSoup


@dataclass
class ArticleContent:
    url: str
    title: str
    summary: str | None
    content: str | None
    image_url: str | None
    published_at: datetime | None


def _extract_meta(soup: BeautifulSoup, prop: str, attr: str = "property") -> str | None:
    tag = soup.find("meta", attrs={attr: prop})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_article_text(soup: BeautifulSoup) -> str | None:
    article = soup.find("article")
    if article:
        paragraphs = [p.get_text(" ", strip=True) for p in article.find_all("p")]
    else:
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = " ".join([p for p in paragraphs if p])
    text = _clean_text(text)
    return text or None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def extract_article(url: str, timeout: float = 12.0) -> ArticleContent:
    headers = {"User-Agent": "EnglishLearningBot/1.0"}
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        resp = client.get(url)
        resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    title = _extract_meta(soup, "og:title") or (soup.title.string.strip() if soup.title else url)
    summary = _extract_meta(soup, "og:description") or _extract_meta(soup, "description", attr="name")
    image_url = _extract_meta(soup, "og:image")
    published_at = _parse_datetime(_extract_meta(soup, "article:published_time"))

    content = _extract_article_text(soup)
    return ArticleContent(
        url=url,
        title=title,
        summary=_clean_text(summary) if summary else None,
        content=content,
        image_url=image_url,
        published_at=published_at,
    )
