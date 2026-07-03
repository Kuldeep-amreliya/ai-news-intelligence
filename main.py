# """
# main.py — FastAPI app + APScheduler.

# Routes:
#   GET  /           → dashboard (index.html)
#   GET  /api/news   → returns news.json content
#   GET  /api/status → last scrape time + article count
#   POST /api/trigger → manually trigger a scrape (for testing)
# """

# import logging
# import os
# from contextlib import asynccontextmanager
# from datetime import datetime, timezone

# from apscheduler.schedulers.background import BackgroundScheduler
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles

# load_dotenv()
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
# )
# logger = logging.getLogger(__name__)

# SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
# DIGEST_HOUR = int(os.getenv("DIGEST_HOUR", "8"))
# DIGEST_MINUTE = int(os.getenv("DIGEST_MINUTE", "0"))

# # ── Pipeline ──────────────────────────────────────────────────────────────────

# def run_pipeline():
#     """Full scrape → LLM → save cycle."""
#     from emailer import send_digest
#     from llm import generate_briefing, summarize_articles
#     from scraper import run_scraper
#     from storage import get_existing_urls, load, save

#     logger.info("Pipeline started.")
#     try:
#         existing = get_existing_urls()
#         new_articles = run_scraper(existing)

#         if not new_articles:
#             logger.info("No new articles found.")
#             # Still keep existing data
#             return

#         # Merge new articles with existing (keep last 100)
#         old_data = load()
#         old_articles = old_data.get("articles", [])
#         merged = new_articles + old_articles
#         merged = merged[:100]  # cap total stored

#         # Summarize only the new ones
#         merged = summarize_articles(merged)

#         briefing = generate_briefing(merged)
#         save(merged, briefing)
#         logger.info(f"Pipeline complete. {len(merged)} total articles stored.")
#     except Exception as e:
#         logger.error(f"Pipeline error: {e}", exc_info=True)


# def run_daily_digest():
#     """Send the email digest. Runs on schedule."""
#     from storage import load
#     from emailer import send_digest

#     data = load()
#     articles = data.get("articles", [])
#     briefing = data.get("briefing", "")
#     send_digest(articles, briefing)


# # ── Scheduler ─────────────────────────────────────────────────────────────────

# scheduler = BackgroundScheduler(timezone="UTC")


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Scrape every N hours
#     scheduler.add_job(run_pipeline, "interval", hours=SCRAPE_INTERVAL_HOURS, id="scraper")

#     # Daily email digest
#     scheduler.add_job(
#         run_daily_digest,
#         "cron",
#         hour=DIGEST_HOUR,
#         minute=DIGEST_MINUTE,
#         id="digest",
#     )

#     scheduler.start()
#     logger.info(
#         f"Scheduler started — scraping every {SCRAPE_INTERVAL_HOURS}h, "
#         f"digest at {DIGEST_HOUR:02d}:{DIGEST_MINUTE:02d} UTC"
#     )

#     # Run immediately on startup so dashboard isn't empty
#     import threading
#     t = threading.Thread(target=run_pipeline, daemon=True)
#     t.start()

#     yield

#     scheduler.shutdown()
#     logger.info("Scheduler stopped.")


# # ── App ───────────────────────────────────────────────────────────────────────

# app = FastAPI(title="AI News Bot", lifespan=lifespan)

# STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# @app.get("/", include_in_schema=False)
# async def root():
#     return FileResponse(os.path.join(STATIC_DIR, "index.html"))


# @app.get("/api/news")
# async def get_news():
#     from storage import load
#     data = load()
#     return JSONResponse(content=data)


# @app.get("/api/status")
# async def get_status():
#     from storage import load
#     data = load()
#     return {
#         "last_scraped": data.get("last_scraped"),
#         "total_articles": data.get("total", 0),
#         "next_scrape_in_hours": SCRAPE_INTERVAL_HOURS,
#         "server_time_utc": datetime.now(timezone.utc).isoformat(),
#     }


# @app.post("/api/trigger")
# async def trigger_scrape():
#     """Manually kick off the pipeline. Runs in background thread."""
#     import threading
#     t = threading.Thread(target=run_pipeline, daemon=True)
#     t.start()
#     return {"message": "Scrape triggered. Check /api/status in ~60 seconds."}


























"""
main.py — FastAPI app + APScheduler.

Routes:
  GET  /                    → dashboard (index.html)
  GET  /api/news            → returns news.json content
  GET  /api/status          → last scrape time + article count
  POST /api/trigger         → manually trigger a scrape (for testing)
  POST /api/article-detail  → two-agent deep-dive for sidebar panel
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))
DIGEST_HOUR           = int(os.getenv("DIGEST_HOUR", "8"))
DIGEST_MINUTE         = int(os.getenv("DIGEST_MINUTE", "0"))

# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline():
    """Full scrape → LLM → save cycle."""
    from emailer import send_digest
    from llm import generate_briefing, summarize_articles
    from scraper import run_scraper
    from storage import get_existing_urls, load, save

    logger.info("Pipeline started.")
    try:
        existing = get_existing_urls()
        new_articles = run_scraper(existing)

        if not new_articles:
            logger.info("No new articles found.")
            return

        old_data = load()
        old_articles = old_data.get("articles", [])
        merged = new_articles + old_articles
        merged = merged[:100]

        merged = summarize_articles(merged)

        briefing = generate_briefing(merged)
        save(merged, briefing)
        logger.info(f"Pipeline complete. {len(merged)} total articles stored.")
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)


def run_daily_digest():
    """Send the email digest. Runs on schedule."""
    from storage import load
    from emailer import send_digest

    data = load()
    articles = data.get("articles", [])
    briefing = data.get("briefing", "")
    send_digest(articles, briefing)


# ── Scheduler ─────────────────────────────────────────────────────────────────

scheduler = BackgroundScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(run_pipeline, "interval", hours=SCRAPE_INTERVAL_HOURS, id="scraper")
    scheduler.add_job(
        run_daily_digest,
        "cron",
        hour=DIGEST_HOUR,
        minute=DIGEST_MINUTE,
        id="digest",
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — scraping every {SCRAPE_INTERVAL_HOURS}h, "
        f"digest at {DIGEST_HOUR:02d}:{DIGEST_MINUTE:02d} UTC"
    )

    import threading
    t = threading.Thread(target=run_pipeline, daemon=True)
    t.start()

    yield

    scheduler.shutdown()
    logger.info("Scheduler stopped.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="AI News Bot", lifespan=lifespan)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/news")
async def get_news():
    from storage import load
    data = load()
    return JSONResponse(content=data)


@app.get("/api/status")
async def get_status():
    from storage import load
    data = load()
    return {
        "last_scraped": data.get("last_scraped"),
        "total_articles": data.get("total", 0),
        "next_scrape_in_hours": SCRAPE_INTERVAL_HOURS,
        "server_time_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/trigger")
async def trigger_scrape():
    """Manually kick off the pipeline. Runs in background thread."""
    import threading
    t = threading.Thread(target=run_pipeline, daemon=True)
    t.start()
    return {"message": "Scrape triggered. Check /api/status in ~60 seconds."}


# ── Article Detail — two-agent sidebar endpoint ───────────────────────────────

class ArticleDetailRequest(BaseModel):
    url:      str
    title:    str
    source:   str
    category: str  = ""
    snippet:  str  = ""
    summary:  str  = ""


@app.post("/api/article-detail")
async def article_detail(req: ArticleDetailRequest):
    """
    Two-agent pipeline:
      Agent 1 (Reader)  — fetches and extracts full article text from URL.
      Agent 2 (Writer)  — LLM generates overview / key_points / context / implications.

    Falls back gracefully to stored snippet/summary if URL is unreachable
    (paywalled, Reddit, Nitter, etc.).

    Response shape:
    {
        title:               str,
        source:              str,
        url:                 str,
        category:            str,
        fetched_from_source: bool,
        overview:            str,
        key_points:          list[str],
        context:             str,
        implications:        str
    }
    """
    if not req.url or not req.title:
        raise HTTPException(status_code=400, detail="url and title are required.")

    try:
        from article_agent import get_article_detail
        result = get_article_detail(
            url=req.url,
            title=req.title,
            source=req.source,
            category=req.category,
            snippet=req.snippet,
            summary=req.summary,
        )
        return JSONResponse(content=result)

    except RuntimeError as e:
        # Both Groq and Mistral unavailable
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"article-detail error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during analysis.")