# import json
# import os
# from datetime import datetime, timezone
# from typing import Any

# DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
# NEWS_FILE = os.path.join(DATA_DIR, "news.json")


# def _ensure_data_dir():
#     os.makedirs(DATA_DIR, exist_ok=True)


# def load() -> dict:
#     _ensure_data_dir()
#     if not os.path.exists(NEWS_FILE):
#         return {"articles": [], "briefing": "", "last_scraped": None, "total": 0}
#     with open(NEWS_FILE, "r", encoding="utf-8") as f:
#         return json.load(f)


# def save(articles: list[dict], briefing: str):
#     _ensure_data_dir()
#     payload = {
#         "articles": articles,
#         "briefing": briefing,
#         "last_scraped": datetime.now(timezone.utc).isoformat(),
#         "total": len(articles),
#     }
#     with open(NEWS_FILE, "w", encoding="utf-8") as f:
#         json.dump(payload, f, indent=2, ensure_ascii=False)


# def get_existing_urls() -> set[str]:
#     data = load()
#     return {a["url"] for a in data.get("articles", [])}













import json
import os
from datetime import datetime, timezone
from typing import Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NEWS_FILE = os.path.join(DATA_DIR, "news.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load() -> dict:
    _ensure_data_dir()
    if not os.path.exists(NEWS_FILE):
        return {"articles": [], "briefing": "", "last_scraped": None, "total": 0}
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save(articles: list[dict], briefing: str):
    _ensure_data_dir()
    payload = {
        "articles": articles,
        "briefing": briefing,
        "last_scraped": datetime.now(timezone.utc).isoformat(),
        "total": len(articles),
    }
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def get_existing_urls() -> set[str]:
    data = load()
    return {a["url"] for a in data.get("articles", [])}