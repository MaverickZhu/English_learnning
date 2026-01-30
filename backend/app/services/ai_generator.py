import json
import re
import time
from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class GeneratedContent:
    level: str | None
    passage: dict
    words: list[dict]
    sentences: list[dict]
    exercises: list[dict]
    tags: list[str]


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def generate_learning_content(title: str, summary: str | None, content: str | None) -> GeneratedContent:
    if not settings.kimi_api_key:
        raise ValueError("KIMI_API_KEY is not configured")
    safe_title = (title or "").strip()[:200]
    safe_summary = (summary or "").strip()[:600]
    safe_content = (content or "").strip()[:2000]
    payload = {
        "model": settings.kimi_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return JSON only. No markdown."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Produce JSON with keys: level, passage, words, sentences, exercises, tags. "
                    "passage includes title, content, summary. "
                    "words items include text, meaning, example, level, tags. "
                    "sentences items include text, meaning, level, tags. "
                    "exercises items include exercise_type, prompt, options, answer, explanation, level, tags. "
                    f"Title: {safe_title}\nSummary: {safe_summary}\nContent: {safe_content}"
                ),
            },
        ],
        "temperature": 1.0,
    }

    headers = {"Authorization": f"Bearer {settings.kimi_api_key}"}
    base = (settings.kimi_base_url or "").rstrip("/")
    if not base:
        raise ValueError("KIMI_BASE_URL is not configured")
    candidates = [f"{base}/chat/completions"]
    if not base.endswith("/v1"):
        candidates.append(f"{base}/v1/chat/completions")

    data = None
    last_resp: httpx.Response | None = None
    with httpx.Client(timeout=60.0, headers=headers) as client:
        for url in candidates:
            for attempt in range(2):
                try:
                    resp = client.post(url, json=payload)
                    last_resp = resp
                    if resp.status_code == 404:
                        break
                    if resp.status_code == 429 and attempt == 0:
                        time.sleep(3.5)
                        continue
                    if resp.status_code >= 400:
                        raise ValueError(f"Kimi API error {resp.status_code}: {resp.text[:500]}")
                    data = resp.json()
                    break
                except httpx.ReadTimeout as exc:
                    if attempt == 0:
                        time.sleep(2.0)
                        continue
                    raise ValueError(f"Kimi API timeout: {exc}") from exc
            if data is not None or (last_resp is not None and last_resp.status_code == 404):
                break
    if data is None:
        if last_resp is not None:
            last_resp.raise_for_status()
        raise ValueError("Kimi API request failed")
    content_text = data["choices"][0]["message"]["content"]
    parsed = _extract_json(content_text)

    return GeneratedContent(
        level=parsed.get("level"),
        passage=parsed.get("passage") or {},
        words=parsed.get("words") or [],
        sentences=parsed.get("sentences") or [],
        exercises=parsed.get("exercises") or [],
        tags=parsed.get("tags") or [],
    )
