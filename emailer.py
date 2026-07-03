# """
# emailer.py — Sends a daily HTML digest email via Gmail SMTP.
# Uses EMAIL_ADDRESS + EMAIL_PASSWORD (Gmail App Password) from .env
# """

# import logging
# import os
# import smtplib
# from datetime import datetime, timezone
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# from dotenv import load_dotenv

# load_dotenv()
# logger = logging.getLogger(__name__)

# EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# CATEGORY_COLORS = {
#     "Research":       "#6366f1",
#     "Product Launch": "#f59e0b",
#     "Policy":         "#ef4444",
#     "Open Source":    "#10b981",
#     "Industry":       "#3b82f6",
#     "Tool":           "#8b5cf6",
# }


# def _build_html(articles: list[dict], briefing: str) -> str:
#     today = datetime.now(timezone.utc).strftime("%B %d, %Y")

#     article_cards = ""
#     for a in articles[:15]:  # Cap at 15 in email
#         cat = a.get("category", "")
#         color = CATEGORY_COLORS.get(cat, "#64748b")
#         summary = a.get("summary") or a.get("snippet", "")[:200]
#         article_cards += f"""
#         <div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:12px;background:#fff;">
#             <div style="margin-bottom:6px;">
#                 <span style="background:{color};color:#fff;font-size:11px;padding:2px 8px;border-radius:12px;font-family:monospace;">
#                     {cat or 'AI News'}
#                 </span>
#                 <span style="color:#94a3b8;font-size:11px;margin-left:8px;">{a['source']}</span>
#             </div>
#             <a href="{a['url']}" style="color:#1e293b;font-weight:600;font-size:15px;text-decoration:none;line-height:1.4;display:block;margin-bottom:6px;">
#                 {a['title']}
#             </a>
#             <p style="color:#475569;font-size:13px;margin:0;line-height:1.5;">{summary}</p>
#         </div>
#         """

#     return f"""
#     <!DOCTYPE html>
#     <html>
#     <head><meta charset="UTF-8"></head>
#     <body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
#         <div style="max-width:640px;margin:0 auto;padding:24px 16px;">

#             <!-- Header -->
#             <div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:12px;padding:28px;margin-bottom:20px;text-align:center;">
#                 <div style="font-size:28px;margin-bottom:4px;">🤖</div>
#                 <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700;">AI News Daily</h1>
#                 <p style="color:#a5b4fc;margin:6px 0 0;font-size:13px;">{today}</p>
#             </div>

#             <!-- Briefing -->
#             <div style="background:#eff6ff;border-left:4px solid #3b82f6;border-radius:0 8px 8px 0;padding:16px;margin-bottom:20px;">
#                 <p style="color:#1e3a8a;font-weight:600;margin:0 0 6px;font-size:13px;">TODAY'S BRIEFING</p>
#                 <p style="color:#1e40af;margin:0;font-size:14px;line-height:1.6;">{briefing}</p>
#             </div>

#             <!-- Articles -->
#             <h2 style="color:#1e293b;font-size:16px;font-weight:600;margin:0 0 12px;">Top Stories</h2>
#             {article_cards}

#             <!-- Footer -->
#             <div style="text-align:center;padding:20px 0;color:#94a3b8;font-size:12px;">
#                 AI News Bot · Powered by Groq & Mistral · {today}
#             </div>
#         </div>
#     </body>
#     </html>
#     """


# def send_digest(articles: list[dict], briefing: str):
#     if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
#         logger.warning("Email credentials not set — skipping digest.")
#         return

#     if not articles:
#         logger.info("No articles to send in digest.")
#         return

#     today = datetime.now(timezone.utc).strftime("%B %d, %Y")
#     subject = f"🤖 AI News Daily — {today} ({len(articles)} stories)"

#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = subject
#     msg["From"] = EMAIL_ADDRESS
#     msg["To"] = EMAIL_ADDRESS  # Sending to yourself

#     html_body = _build_html(articles, briefing)
#     msg.attach(MIMEText(html_body, "html"))

#     try:
#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#             server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#             server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
#         logger.info(f"Digest sent to {EMAIL_ADDRESS}")
#     except smtplib.SMTPAuthenticationError:
#         logger.error(
#             "Gmail auth failed. Make sure EMAIL_PASSWORD is a Gmail App Password, "
#             "not your regular password. Generate at: "
#             "https://myaccount.google.com/apppasswords"
#         )
#     except Exception as e:
#         logger.error(f"Email send failed: {e}")


















"""
emailer.py — Sends a daily HTML digest email via Gmail SMTP.
Uses EMAIL_ADDRESS + EMAIL_PASSWORD (Gmail App Password) from .env
"""

import logging
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

CATEGORY_COLORS = {
    "Research":       "#6366f1",
    "Product Launch": "#f59e0b",
    "Policy":         "#ef4444",
    "Open Source":    "#10b981",
    "Industry":       "#3b82f6",
    "Tool":           "#8b5cf6",
}


def _build_html(articles: list[dict], briefing: str) -> str:
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    article_cards = ""
    for a in articles[:15]:  # Cap at 15 in email
        cat = a.get("category", "")
        color = CATEGORY_COLORS.get(cat, "#64748b")
        summary = a.get("summary") or a.get("snippet", "")[:200]
        article_cards += f"""
        <div style="border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin-bottom:12px;background:#fff;">
            <div style="margin-bottom:6px;">
                <span style="background:{color};color:#fff;font-size:11px;padding:2px 8px;border-radius:12px;font-family:monospace;">
                    {cat or 'AI News'}
                </span>
                <span style="color:#94a3b8;font-size:11px;margin-left:8px;">{a['source']}</span>
            </div>
            <a href="{a['url']}" style="color:#1e293b;font-weight:600;font-size:15px;text-decoration:none;line-height:1.4;display:block;margin-bottom:6px;">
                {a['title']}
            </a>
            <p style="color:#475569;font-size:13px;margin:0;line-height:1.5;">{summary}</p>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
        <div style="max-width:640px;margin:0 auto;padding:24px 16px;">

            <!-- Header -->
            <div style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:12px;padding:28px;margin-bottom:20px;text-align:center;">
                <div style="font-size:28px;margin-bottom:4px;">🤖</div>
                <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700;">AI News Daily</h1>
                <p style="color:#a5b4fc;margin:6px 0 0;font-size:13px;">{today}</p>
            </div>

            <!-- Briefing -->
            <div style="background:#eff6ff;border-left:4px solid #3b82f6;border-radius:0 8px 8px 0;padding:16px;margin-bottom:20px;">
                <p style="color:#1e3a8a;font-weight:600;margin:0 0 6px;font-size:13px;">TODAY'S BRIEFING</p>
                <p style="color:#1e40af;margin:0;font-size:14px;line-height:1.6;">{briefing}</p>
            </div>

            <!-- Articles -->
            <h2 style="color:#1e293b;font-size:16px;font-weight:600;margin:0 0 12px;">Top Stories</h2>
            {article_cards}

            <!-- Footer -->
            <div style="text-align:center;padding:20px 0;color:#94a3b8;font-size:12px;">
                AI News Bot · Powered by Groq & Mistral · {today}
            </div>
        </div>
    </body>
    </html>
    """


def send_digest(articles: list[dict], briefing: str):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logger.warning("Email credentials not set — skipping digest.")
        return

    if not articles:
        logger.info("No articles to send in digest.")
        return

    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    subject = f"🤖 AI News Daily — {today} ({len(articles)} stories)"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS  # Sending to yourself

    html_body = _build_html(articles, briefing)
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
        logger.info(f"Digest sent to {EMAIL_ADDRESS}")
    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Gmail auth failed. Make sure EMAIL_PASSWORD is a Gmail App Password, "
            "not your regular password. Generate at: "
            "https://myaccount.google.com/apppasswords"
        )
    except Exception as e:
        logger.error(f"Email send failed: {e}")