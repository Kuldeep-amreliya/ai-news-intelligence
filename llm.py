# """
# llm.py — LLM processing using Groq (primary) and Mistral (fallback).

# Rate limit strategy:
#   - Groq free:   6,000 tokens/min, 30 req/min
#   - Mistral free: 1 req/sec, ~500k tokens/month
#   - Batch 5 articles per prompt to minimize API calls
#   - Skip articles that already have summaries
# """

# import logging
# import os
# import time

# from dotenv import load_dotenv

# load_dotenv()
# logger = logging.getLogger(__name__)

# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# GROQ_MODEL = "llama-3.3-70b-versatile"
# MISTRAL_MODEL = "mistral-small-latest"

# BATCH_SIZE = 5  # articles per LLM call


# # ── Client init ───────────────────────────────────────────────────────────────

# def _groq_client():
#     from groq import Groq
#     return Groq(api_key=GROQ_API_KEY)


# def _mistral_client():
#     from mistralai import Mistral
#     return Mistral(api_key=MISTRAL_API_KEY)


# # ── Core LLM call with fallback ───────────────────────────────────────────────

# def _call_llm(prompt: str) -> str:
#     """
#     Try Groq first. On rate-limit (429) or any error, fall back to Mistral.
#     Returns the raw text response.
#     """
#     # ── Groq ──
#     if GROQ_API_KEY:
#         try:
#             client = _groq_client()
#             resp = client.chat.completions.create(
#                 model=GROQ_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.3,
#                 max_tokens=1024,
#             )
#             return resp.choices[0].message.content.strip()
#         except Exception as e:
#             err = str(e)
#             if "429" in err or "rate" in err.lower():
#                 logger.warning("Groq rate-limited, falling back to Mistral.")
#             else:
#                 logger.warning(f"Groq error: {e}, falling back to Mistral.")

#     # ── Mistral fallback ──
#     if MISTRAL_API_KEY:
#         try:
#             time.sleep(1)  # Mistral: 1 req/sec safe limit
#             client = _mistral_client()
#             resp = client.chat.complete(
#                 model=MISTRAL_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.3,
#                 max_tokens=1024,
#             )
#             return resp.choices[0].message.content.strip()
#         except Exception as e:
#             logger.error(f"Mistral error: {e}")

#     raise RuntimeError("Both Groq and Mistral failed or no API keys set.")


# # ── Summarize articles in batches ─────────────────────────────────────────────

# SUMMARY_PROMPT = """\
# You are an AI news analyst. For each article below, provide:
# 1. A 1-2 sentence plain English summary (what happened, why it matters).
# 2. A single category tag from: [Research, Product Launch, Policy, Open Source, Industry, Tool]

# Respond ONLY as a JSON array. Each element: {{"id": "...", "summary": "...", "category": "..."}}
# Do not add any explanation outside the JSON.

# Articles:
# {articles_block}
# """


# def _build_articles_block(batch: list[dict]) -> str:
#     lines = []
#     for a in batch:
#         lines.append(f'ID: {a["id"]}\nTitle: {a["title"]}\nSnippet: {a["snippet"][:200]}')
#         lines.append("---")
#     return "\n".join(lines)


# def summarize_articles(articles: list[dict]) -> list[dict]:
#     """
#     Fills 'summary' and 'category' fields in-place for articles missing them.
#     Returns the updated list.
#     """
#     import json

#     to_process = [a for a in articles if not a.get("summary")]
#     logger.info(f"LLM: summarizing {len(to_process)} articles in batches of {BATCH_SIZE}")

#     # Build an id→article map for fast lookup
#     id_map = {a["id"]: a for a in articles}

#     for i in range(0, len(to_process), BATCH_SIZE):
#         batch = to_process[i : i + BATCH_SIZE]
#         prompt = SUMMARY_PROMPT.format(articles_block=_build_articles_block(batch))

#         try:
#             raw = _call_llm(prompt)

#             # Strip markdown fences if present
#             clean = raw.strip()
#             if clean.startswith("```"):
#                 clean = clean.split("```")[1]
#                 if clean.startswith("json"):
#                     clean = clean[4:]
#             clean = clean.strip()

#             results = json.loads(clean)
#             for item in results:
#                 art_id = item.get("id")
#                 if art_id in id_map:
#                     id_map[art_id]["summary"] = item.get("summary", "")
#                     id_map[art_id]["category"] = item.get("category", "")

#         except Exception as e:
#             logger.error(f"LLM batch {i//BATCH_SIZE + 1} failed: {e}")
#             # Don't crash — leave summary blank for this batch

#         # Respect Groq's 30 req/min: sleep 2s between batches
#         if i + BATCH_SIZE < len(to_process):
#             time.sleep(2)

#     return articles


# # ── Daily briefing ────────────────────────────────────────────────────────────

# BRIEFING_PROMPT = """\
# You are an expert AI industry analyst writing a concise daily briefing.
# Based on these article titles and sources, write a 3-4 sentence paragraph 
# summarizing the most important trends and developments in AI today.
# Be specific. Mention key players, models, or themes if visible.
# Write in a professional but accessible tone.

# Headlines:
# {headlines}
# """


# def generate_briefing(articles: list[dict]) -> str:
#     if not articles:
#         return "No AI news collected in the last 24 hours."

#     headlines = "\n".join(
#         f"- [{a['source']}] {a['title']}" for a in articles[:30]
#     )
#     prompt = BRIEFING_PROMPT.format(headlines=headlines)

#     try:
#         briefing = _call_llm(prompt)
#         return briefing
#     except Exception as e:
#         logger.error(f"Briefing generation failed: {e}")
#         return "Briefing unavailable — LLM quota may be exhausted."















"""
llm.py — LLM processing using Groq (primary) and Mistral (fallback).

Rate limit strategy:
  - Groq free:   6,000 tokens/min, 30 req/min
  - Mistral free: 1 req/sec, ~500k tokens/month
  - Batch 5 articles per prompt to minimize API calls
  - Skip articles that already have summaries
"""

import logging
import os
import time

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

GROQ_MODEL = "llama-3.3-70b-versatile"
MISTRAL_MODEL = "mistral-small-latest"

BATCH_SIZE = 5  # articles per LLM call


# ── Client init ───────────────────────────────────────────────────────────────

def _groq_client():
    from groq import Groq
    return Groq(api_key=GROQ_API_KEY)


def _mistral_client():
    from mistralai import Mistral
    return Mistral(api_key=MISTRAL_API_KEY)


# ── Core LLM call with fallback ───────────────────────────────────────────────

def _call_llm(prompt: str) -> str:
    """
    Try Groq first. On rate-limit (429) or any error, fall back to Mistral.
    Returns the raw text response.
    """
    # ── Groq ──
    if GROQ_API_KEY:
        try:
            client = _groq_client()
            resp = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower():
                logger.warning("Groq rate-limited, falling back to Mistral.")
            else:
                logger.warning(f"Groq error: {e}, falling back to Mistral.")

    # ── Mistral fallback ──
    if MISTRAL_API_KEY:
        try:
            time.sleep(1)  # Mistral: 1 req/sec safe limit
            client = _mistral_client()
            resp = client.chat.complete(
                model=MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Mistral error: {e}")

    raise RuntimeError("Both Groq and Mistral failed or no API keys set.")


# ── Summarize articles in batches ─────────────────────────────────────────────

SUMMARY_PROMPT = """\
You are an AI news analyst. For each article below, provide:
1. A 1-2 sentence plain English summary (what happened, why it matters).
2. A single category tag from: [Research, Product Launch, Policy, Open Source, Industry, Tool]

Respond ONLY as a JSON array. Each element: {{"id": "...", "summary": "...", "category": "..."}}
Do not add any explanation outside the JSON.

Articles:
{articles_block}
"""


def _build_articles_block(batch: list[dict]) -> str:
    lines = []
    for a in batch:
        lines.append(f'ID: {a["id"]}\nTitle: {a["title"]}\nSnippet: {a["snippet"][:200]}')
        lines.append("---")
    return "\n".join(lines)


def summarize_articles(articles: list[dict]) -> list[dict]:
    """
    Fills 'summary' and 'category' fields in-place for articles missing them.
    Returns the updated list.
    """
    import json

    to_process = [a for a in articles if not a.get("summary")]
    logger.info(f"LLM: summarizing {len(to_process)} articles in batches of {BATCH_SIZE}")

    # Build an id→article map for fast lookup
    id_map = {a["id"]: a for a in articles}

    for i in range(0, len(to_process), BATCH_SIZE):
        batch = to_process[i : i + BATCH_SIZE]
        prompt = SUMMARY_PROMPT.format(articles_block=_build_articles_block(batch))

        try:
            raw = _call_llm(prompt)

            # Strip markdown fences if present
            clean = raw.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            clean = clean.strip()

            results = json.loads(clean)
            for item in results:
                art_id = item.get("id")
                if art_id in id_map:
                    id_map[art_id]["summary"] = item.get("summary", "")
                    id_map[art_id]["category"] = item.get("category", "")

        except Exception as e:
            logger.error(f"LLM batch {i//BATCH_SIZE + 1} failed: {e}")
            # Don't crash — leave summary blank for this batch

        # Respect Groq's 30 req/min: sleep 2s between batches
        if i + BATCH_SIZE < len(to_process):
            time.sleep(2)

    return articles


# ── Daily briefing ────────────────────────────────────────────────────────────

BRIEFING_PROMPT = """\
You are an expert AI industry analyst writing a concise daily briefing.
Based on these article titles and sources, write a 3-4 sentence paragraph 
summarizing the most important trends and developments in AI today.
Be specific. Mention key players, models, or themes if visible.
Write in a professional but accessible tone.

Headlines:
{headlines}
"""


def generate_briefing(articles: list[dict]) -> str:
    if not articles:
        return "No AI news collected in the last 24 hours."

    headlines = "\n".join(
        f"- [{a['source']}] {a['title']}" for a in articles[:30]
    )
    prompt = BRIEFING_PROMPT.format(headlines=headlines)

    try:
        briefing = _call_llm(prompt)
        return briefing
    except Exception as e:
        logger.error(f"Briefing generation failed: {e}")
        return "Briefing unavailable — LLM quota may be exhausted."