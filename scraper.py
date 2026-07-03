# """
# scraper.py — Collects AI news from RSS feeds, Reddit, and Nitter (X).
# All sources are free, no API keys required.
# """

# import hashlib
# import logging
# from datetime import datetime, timedelta, timezone
# from typing import Optional

# import feedparser
# import httpx
# from bs4 import BeautifulSoup

# logger = logging.getLogger(__name__)

# # ── Constants ─────────────────────────────────────────────────────────────────

# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/124.0.0.0 Safari/537.36"
#     )
# }

# CUTOFF_HOURS = 24  # Only keep articles from last 24 hours

# RSS_FEEDS = [
#     ("HuggingFace Blog",    "https://huggingface.co/blog/feed.xml"),
#     ("ArXiv cs.AI",         "https://rss.arxiv.org/rss/cs.AI"),
#     ("ArXiv cs.LG",         "https://rss.arxiv.org/rss/cs.LG"),
#     ("TechCrunch AI",       "https://techcrunch.com/category/artificial-intelligence/feed/"),
#     ("VentureBeat AI",      "https://venturebeat.com/category/ai/feed/"),
#     ("MIT News AI",         "https://news.mit.edu/topic/artificial-intelligence2/feed"),
#     ("The Verge AI",        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
#     ("Ars Technica AI",     "https://feeds.arstechnica.com/arstechnica/technology-lab"),
# ]

# REDDIT_SUBS = [
#     "MachineLearning",
#     "LocalLLaMA",
#     "artificial",
# ]

# # Public Nitter instances (tried in order until one works)
# NITTER_INSTANCES = [
#     "https://nitter.privacydev.net",
#     "https://nitter.poast.org",
#     "https://nitter.1d4.us",
# ]

# NITTER_QUERIES = ["AI news", "LLM release", "OpenAI", "Anthropic", "machine learning"]


# # ── Helpers ───────────────────────────────────────────────────────────────────

# def _url_hash(url: str) -> str:
#     return hashlib.md5(url.encode()).hexdigest()


# def _cutoff_dt() -> datetime:
#     return datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)


# def _parse_dt(value) -> Optional[datetime]:
#     """Safely parse a feedparser time struct or ISO string into aware datetime."""
#     if value is None:
#         return None
#     try:
#         import time
#         if hasattr(value, "tm_year"):  # struct_time
#             ts = time.mktime(value)
#             return datetime.fromtimestamp(ts, tz=timezone.utc)
#         if isinstance(value, str):
#             return datetime.fromisoformat(value.replace("Z", "+00:00"))
#     except Exception:
#         return None
#     return None


# def _make_article(title: str, url: str, source: str, published: Optional[datetime] = None, snippet: str = "") -> dict:
#     return {
#         "id": _url_hash(url),
#         "title": title.strip(),
#         "url": url.strip(),
#         "source": source,
#         "published": published.isoformat() if published else datetime.now(timezone.utc).isoformat(),
#         "snippet": snippet.strip()[:300],
#         "summary": "",   # filled by llm.py
#         "category": "",  # filled by llm.py
#     }


# # ── RSS Scraper ───────────────────────────────────────────────────────────────

# def scrape_rss() -> list[dict]:
#     articles = []
#     cutoff = _cutoff_dt()

#     for source_name, url in RSS_FEEDS:
#         try:
#             feed = feedparser.parse(url)
#             for entry in feed.entries:
#                 pub = _parse_dt(getattr(entry, "published_parsed", None))
#                 if pub and pub < cutoff:
#                     continue  # too old

#                 link = getattr(entry, "link", "")
#                 title = getattr(entry, "title", "")
#                 if not link or not title:
#                     continue

#                 snippet = ""
#                 if hasattr(entry, "summary"):
#                     soup = BeautifulSoup(entry.summary, "html.parser")
#                     snippet = soup.get_text(" ", strip=True)

#                 articles.append(_make_article(title, link, source_name, pub, snippet))
#         except Exception as e:
#             logger.warning(f"RSS failed [{source_name}]: {e}")

#     logger.info(f"RSS: {len(articles)} articles")
#     return articles


# # ── Reddit Scraper ────────────────────────────────────────────────────────────

# def scrape_reddit() -> list[dict]:
#     """
#     Uses Reddit's public .json endpoint — no API key needed.
#     Rate limit: ~1 req/sec is safe.
#     """
#     articles = []
#     cutoff = _cutoff_dt()

#     with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
#         for sub in REDDIT_SUBS:
#             try:
#                 url = f"https://old.reddit.com/r/{sub}/hot.json?limit=25"
#                 resp = client.get(url)
#                 resp.raise_for_status()
#                 posts = resp.json()["data"]["children"]

#                 for post in posts:
#                     d = post["data"]
#                     # Filter: must be a link post (not self), not too old
#                     created = datetime.fromtimestamp(d["created_utc"], tz=timezone.utc)
#                     if created < cutoff:
#                         continue
#                     if d.get("is_self"):
#                         continue  # skip text-only posts

#                     title = d.get("title", "")
#                     link = d.get("url", "")
#                     if not title or not link:
#                         continue

#                     articles.append(_make_article(
#                         title=title,
#                         url=link,
#                         source=f"r/{sub}",
#                         published=created,
#                         snippet=d.get("selftext", "")[:300],
#                     ))
#             except Exception as e:
#                 logger.warning(f"Reddit failed [r/{sub}]: {e}")

#     logger.info(f"Reddit: {len(articles)} articles")
#     return articles


# # ── Nitter (X) Scraper ────────────────────────────────────────────────────────

# def _get_working_nitter(client: httpx.Client) -> Optional[str]:
#     for instance in NITTER_INSTANCES:
#         try:
#             r = client.get(instance, timeout=8)
#             if r.status_code == 200:
#                 return instance
#         except Exception:
#             continue
#     return None


# def scrape_nitter() -> list[dict]:
#     """
#     Scrapes public Nitter instances for AI-related tweets.
#     Returns tweet-based articles (title = tweet text, url = tweet link).
#     """
#     articles = []

#     with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
#         base = _get_working_nitter(client)
#         if not base:
#             logger.warning("Nitter: no working instance found, skipping.")
#             return []

#         for query in NITTER_QUERIES:
#             try:
#                 url = f"{base}/search?f=tweets&q={query.replace(' ', '+')}&since=1d"
#                 resp = client.get(url, timeout=12)
#                 resp.raise_for_status()
#                 soup = BeautifulSoup(resp.text, "html.parser")

#                 for tweet_div in soup.select(".timeline-item")[:10]:
#                     content_el = tweet_div.select_one(".tweet-content")
#                     link_el = tweet_div.select_one(".tweet-link")
#                     if not content_el or not link_el:
#                         continue

#                     text = content_el.get_text(" ", strip=True)
#                     tweet_url = base + link_el["href"]

#                     # Only keep tweets mentioning AI topics
#                     keywords = ["ai", "llm", "gpt", "model", "openai", "anthropic",
#                                 "gemini", "mistral", "claude", "machine learning"]
#                     if not any(kw in text.lower() for kw in keywords):
#                         continue

#                     articles.append(_make_article(
#                         title=text[:120],
#                         url=tweet_url,
#                         source="X (via Nitter)",
#                         published=datetime.now(timezone.utc),
#                         snippet=text,
#                     ))
#             except Exception as e:
#                 logger.warning(f"Nitter query failed [{query}]: {e}")

#     logger.info(f"Nitter: {len(articles)} articles")
#     return articles


# # ── Deduplication ─────────────────────────────────────────────────────────────

# def deduplicate(articles: list[dict], existing_urls: set[str]) -> list[dict]:
#     seen_ids = set()
#     result = []
#     for a in articles:
#         if a["url"] in existing_urls:
#             continue
#         if a["id"] in seen_ids:
#             continue
#         seen_ids.add(a["id"])
#         result.append(a)
#     return result


# # ── Main entry ────────────────────────────────────────────────────────────────

# def run_scraper(existing_urls: set[str]) -> list[dict]:
#     all_articles = []
#     all_articles.extend(scrape_rss())
#     all_articles.extend(scrape_reddit())
#     all_articles.extend(scrape_nitter())

#     deduped = deduplicate(all_articles, existing_urls)
#     logger.info(f"Scraper total (after dedup): {len(deduped)} new articles")
#     return deduped

























"""
scraper.py — Collects AI news from RSS feeds, Reddit, and Nitter (X).
All sources are free, no API keys required.
"""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

CUTOFF_HOURS = 24  # Only keep articles from last 24 hours

RSS_FEEDS = [
    ("HuggingFace Blog",    "https://huggingface.co/blog/feed.xml"),
    ("ArXiv cs.AI",         "https://rss.arxiv.org/rss/cs.AI"),
    ("ArXiv cs.LG",         "https://rss.arxiv.org/rss/cs.LG"),
    ("TechCrunch AI",       "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI",      "https://venturebeat.com/category/ai/feed/"),
    ("MIT News AI",         "https://news.mit.edu/topic/artificial-intelligence2/feed"),
    ("The Verge AI",        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("Ars Technica AI",     "https://feeds.arstechnica.com/arstechnica/technology-lab"),
]

REDDIT_SUBS = [
    "MachineLearning",
    "LocalLLaMA",
    "artificial",
]

# Public Nitter instances (tried in order until one works)
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.1d4.us",
]

NITTER_QUERIES = ["AI news", "LLM release", "OpenAI", "Anthropic", "machine learning"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _cutoff_dt() -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)


def _parse_dt(value) -> Optional[datetime]:
    """Safely parse a feedparser time struct or ISO string into aware datetime."""
    if value is None:
        return None
    try:
        import time
        if hasattr(value, "tm_year"):  # struct_time
            ts = time.mktime(value)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None
    return None


def _make_article(title: str, url: str, source: str, published: Optional[datetime] = None, snippet: str = "") -> dict:
    return {
        "id": _url_hash(url),
        "title": title.strip(),
        "url": url.strip(),
        "source": source,
        "published": published.isoformat() if published else datetime.now(timezone.utc).isoformat(),
        "snippet": snippet.strip()[:300],
        "summary": "",   # filled by llm.py
        "category": "",  # filled by llm.py
    }


# ── RSS Scraper ───────────────────────────────────────────────────────────────

def scrape_rss() -> list[dict]:
    articles = []
    cutoff = _cutoff_dt()

    for source_name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                pub = _parse_dt(getattr(entry, "published_parsed", None))
                if pub and pub < cutoff:
                    continue  # too old

                link = getattr(entry, "link", "")
                title = getattr(entry, "title", "")
                if not link or not title:
                    continue

                snippet = ""
                if hasattr(entry, "summary"):
                    soup = BeautifulSoup(entry.summary, "html.parser")
                    snippet = soup.get_text(" ", strip=True)

                articles.append(_make_article(title, link, source_name, pub, snippet))
        except Exception as e:
            logger.warning(f"RSS failed [{source_name}]: {e}")

    logger.info(f"RSS: {len(articles)} articles")
    return articles


# ── Reddit Scraper ────────────────────────────────────────────────────────────

def scrape_reddit() -> list[dict]:
    """
    Uses Reddit's public .json endpoint — no API key needed.
    Rate limit: ~1 req/sec is safe.
    """
    articles = []
    cutoff = _cutoff_dt()

    with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        for sub in REDDIT_SUBS:
            try:
                url = f"https://old.reddit.com/r/{sub}/hot.json?limit=25"
                resp = client.get(url)
                resp.raise_for_status()
                posts = resp.json()["data"]["children"]

                for post in posts:
                    d = post["data"]
                    # Filter: must be a link post (not self), not too old
                    created = datetime.fromtimestamp(d["created_utc"], tz=timezone.utc)
                    if created < cutoff:
                        continue
                    if d.get("is_self"):
                        continue  # skip text-only posts

                    title = d.get("title", "")
                    link = d.get("url", "")
                    if not title or not link:
                        continue

                    articles.append(_make_article(
                        title=title,
                        url=link,
                        source=f"r/{sub}",
                        published=created,
                        snippet=d.get("selftext", "")[:300],
                    ))
            except Exception as e:
                logger.warning(f"Reddit failed [r/{sub}]: {e}")

    logger.info(f"Reddit: {len(articles)} articles")
    return articles


# ── Nitter (X) Scraper ────────────────────────────────────────────────────────

def _get_working_nitter(client: httpx.Client) -> Optional[str]:
    for instance in NITTER_INSTANCES:
        try:
            r = client.get(instance, timeout=8)
            if r.status_code == 200:
                return instance
        except Exception:
            continue
    return None


def scrape_nitter() -> list[dict]:
    """
    Scrapes public Nitter instances for AI-related tweets.
    Returns tweet-based articles (title = tweet text, url = tweet link).
    """
    articles = []

    with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        base = _get_working_nitter(client)
        if not base:
            logger.warning("Nitter: no working instance found, skipping.")
            return []

        for query in NITTER_QUERIES:
            try:
                url = f"{base}/search?f=tweets&q={query.replace(' ', '+')}&since=1d"
                resp = client.get(url, timeout=12)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                for tweet_div in soup.select(".timeline-item")[:10]:
                    content_el = tweet_div.select_one(".tweet-content")
                    link_el = tweet_div.select_one(".tweet-link")
                    if not content_el or not link_el:
                        continue

                    text = content_el.get_text(" ", strip=True)
                    tweet_url = base + link_el["href"]

                    # Only keep tweets mentioning AI topics
                    keywords = ["ai", "llm", "gpt", "model", "openai", "anthropic",
                                "gemini", "mistral", "claude", "machine learning"]
                    if not any(kw in text.lower() for kw in keywords):
                        continue

                    articles.append(_make_article(
                        title=text[:120],
                        url=tweet_url,
                        source="X (via Nitter)",
                        published=datetime.now(timezone.utc),
                        snippet=text,
                    ))
            except Exception as e:
                logger.warning(f"Nitter query failed [{query}]: {e}")

    logger.info(f"Nitter: {len(articles)} articles")
    return articles


# ── Deduplication ─────────────────────────────────────────────────────────────

def deduplicate(articles: list[dict], existing_urls: set[str]) -> list[dict]:
    seen_ids = set()
    result = []
    for a in articles:
        if a["url"] in existing_urls:
            continue
        if a["id"] in seen_ids:
            continue
        seen_ids.add(a["id"])
        result.append(a)
    return result


# ── Main entry ────────────────────────────────────────────────────────────────

def run_scraper(existing_urls: set[str]) -> list[dict]:
    all_articles = []
    all_articles.extend(scrape_rss())
    all_articles.extend(scrape_reddit())
    all_articles.extend(scrape_nitter())

    deduped = deduplicate(all_articles, existing_urls)
    logger.info(f"Scraper total (after dedup): {len(deduped)} new articles")
    return deduped