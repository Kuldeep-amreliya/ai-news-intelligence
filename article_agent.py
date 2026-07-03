"""
article_agent.py — Two-agent pipeline for sidebar deep-dives.

Agent 1 — Reader:
  Fetches the full article HTML from the URL.
  Extracts clean article text using BeautifulSoup.
  Falls back to the snippet/summary already in storage if fetch fails
  (Reddit JSON API, paywalled sites, Nitter, etc.).

Agent 2 — Writer:
  Receives the full text (or fallback content).
  Calls the LLM (Groq → Mistral fallback) with a structured prompt.
  Returns a parsed dict with: overview, key_points, context, implications.
"""

import json
import logging
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from llm import _call_llm  # reuse existing Groq→Mistral wrapper

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Max characters of article text to pass to LLM (avoid token overflow)
MAX_ARTICLE_CHARS = 6000

# ── Sources that need special handling (skip fetch, use API or fallback) ───────
SKIP_FETCH_PATTERNS = [
    "nitter.",          # Nitter tweet pages — already have full text in snippet
    "reddit.com",       # Reddit links point to the external article, not reddit
    "old.reddit.com",
    "twitter.com",
    "x.com",
]


def _should_skip_fetch(url: str) -> bool:
    return any(p in url.lower() for p in SKIP_FETCH_PATTERNS)


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT 1 — READER
# ═══════════════════════════════════════════════════════════════════════════════

def _extract_article_text(html: str, url: str) -> str:
    """
    Extract main article body text from HTML.
    Strategy:
      1. Try <article> tag (most news sites).
      2. Try common content div selectors.
      3. Fall back to stripping all tags from <body>.
    Always strips nav/header/footer/aside/script/style before extracting.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove boilerplate elements
    for tag in soup(["script", "style", "nav", "header", "footer",
                     "aside", "form", "figure", "figcaption", "iframe",
                     "noscript", "svg", "button", "input"]):
        tag.decompose()

    # Strategy 1: <article> tag
    article_el = soup.find("article")
    if article_el:
        text = article_el.get_text(" ", strip=True)
        if len(text) > 200:
            return _clean_text(text)

    # Strategy 2: common CMS content containers
    selectors = [
        "div.article-body",
        "div.post-content",
        "div.entry-content",
        "div.content-body",
        "div.story-body",
        "div.article__body",
        "div.article-content",
        "div[itemprop='articleBody']",
        "section.article-body",
        "main",
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(" ", strip=True)
            if len(text) > 200:
                return _clean_text(text)

    # Strategy 3: body fallback
    body = soup.find("body")
    if body:
        return _clean_text(body.get_text(" ", strip=True))

    return ""


def _clean_text(text: str) -> str:
    """Collapse whitespace and strip excess blank lines."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def reader_agent(url: str, snippet: str = "", summary: str = "") -> tuple[str, bool]:
    """
    Fetch and extract article text.

    Returns:
        (content: str, fetched_from_source: bool)
        - content: best available text for the LLM writer
        - fetched_from_source: True if we got full article, False if using fallback
    """
    # For tweet-based or Reddit sources, skip fetch — use what we already have
    if _should_skip_fetch(url):
        logger.info(f"Reader: skipping fetch for {url} (known non-article source)")
        return (summary or snippet or "No content available."), False

    try:
        with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if "text/html" not in content_type:
                logger.warning(f"Reader: non-HTML content-type ({content_type}) for {url}")
                return (summary or snippet or "Non-HTML content."), False

            text = _extract_article_text(resp.text, url)

            if len(text) < 150:
                # Extraction failed / paywalled — fall back
                logger.warning(f"Reader: extracted text too short ({len(text)} chars) for {url}")
                return (summary or snippet or "Content unavailable."), False

            # Truncate to avoid LLM token overflow
            truncated = text[:MAX_ARTICLE_CHARS]
            if len(text) > MAX_ARTICLE_CHARS:
                truncated += "\n[...article continues, truncated for analysis...]"

            logger.info(f"Reader: extracted {len(text)} chars from {url}")
            return truncated, True

    except httpx.TimeoutException:
        logger.warning(f"Reader: timeout fetching {url}")
    except httpx.HTTPStatusError as e:
        logger.warning(f"Reader: HTTP {e.response.status_code} for {url}")
    except Exception as e:
        logger.warning(f"Reader: failed to fetch {url}: {e}")

    # All fetch failures → use stored fallback
    fallback = summary or snippet or "Article content could not be retrieved."
    return fallback, False


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT 2 — WRITER
# ═══════════════════════════════════════════════════════════════════════════════

DEEP_DIVE_PROMPT = """\
You are an expert AI/tech journalist. A user clicked "Know more" on a news story \
and wants a thorough understanding without visiting the original site.

Article title: {title}
Source: {source}
Article content:
---
{content}
---

Write a structured deep-dive. Respond ONLY with a valid JSON object — no markdown fences, \
no explanation outside the JSON.

JSON schema:
{{
  "overview": "2-3 sentence plain-English summary of exactly what happened.",
  "key_points": [
    "Specific fact or detail #1",
    "Specific fact or detail #2",
    "Specific fact or detail #3",
    "Specific fact or detail #4"
  ],
  "context": "1-2 sentences of background — who the key players are, why this space matters, \
what led to this.",
  "implications": "1-2 sentences on what this means going forward — impact on industry, \
users, or technology."
}}

Rules:
- Be specific. Name models, companies, numbers, dates where present in the content.
- Do not make up facts not present in the content.
- key_points must be an array of 3-5 strings (plain text, no markdown bullets).
- All values must be strings (overview, context, implications) or array of strings (key_points).
- Return ONLY the JSON object.
"""


def writer_agent(
    title: str,
    source: str,
    content: str,
) -> dict:
    """
    Generate a structured deep-dive using the LLM.

    Returns a dict with keys: overview, key_points, context, implications.
    Falls back to a minimal dict if LLM or JSON parsing fails.
    """
    prompt = DEEP_DIVE_PROMPT.format(
        title=title,
        source=source,
        content=content[:MAX_ARTICLE_CHARS],  # safety truncation
    )

    try:
        raw = _call_llm(prompt)

        # Strip markdown fences if the LLM ignored instructions
        clean = raw.strip()
        if clean.startswith("```"):
            clean = re.sub(r"^```[a-z]*\n?", "", clean)
            clean = re.sub(r"\n?```$", "", clean)
        clean = clean.strip()

        result = json.loads(clean)

        # Validate expected keys — fill missing ones gracefully
        return {
            "overview":     result.get("overview", ""),
            "key_points":   result.get("key_points", []),
            "context":      result.get("context", ""),
            "implications": result.get("implications", ""),
        }

    except json.JSONDecodeError as e:
        logger.error(f"Writer: JSON parse failed: {e}\nRaw: {raw[:300]}")
        # Return whatever we got as a plain overview
        return {
            "overview": raw[:500] if raw else "Analysis unavailable.",
            "key_points": [],
            "context": "",
            "implications": "",
        }
    except Exception as e:
        logger.error(f"Writer: LLM call failed: {e}")
        return {
            "overview": "Could not generate analysis — LLM unavailable.",
            "key_points": [],
            "context": "",
            "implications": "",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def get_article_detail(
    url: str,
    title: str,
    source: str,
    category: str = "",
    snippet: str = "",
    summary: str = "",
) -> dict:
    """
    Full two-agent pipeline.
    Called by the FastAPI route /api/article-detail.

    Returns the complete response dict ready to serialize as JSON.
    """
    logger.info(f"Article detail pipeline: {title[:60]}")

    # Agent 1: fetch full article text
    content, fetched_from_source = reader_agent(url, snippet=snippet, summary=summary)

    # Agent 2: generate deep-dive
    deep_dive = writer_agent(title=title, source=source, content=content)

    return {
        "title":               title,
        "source":              source,
        "url":                 url,
        "category":            category,
        "fetched_from_source": fetched_from_source,
        **deep_dive,  # overview, key_points, context, implications
    }