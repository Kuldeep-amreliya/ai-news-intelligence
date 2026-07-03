# 🚀 AI News Intelligence

> An AI-powered news intelligence platform that automatically collects the latest AI news, generates intelligent summaries, performs multi-agent article analysis, and delivers a clean daily news dashboard with email reports.

---

## 📖 Overview

AI News Intelligence is an end-to-end AI news aggregation platform that continuously collects the latest Artificial Intelligence news from trusted public sources, enriches each article using Large Language Models (LLMs), and presents everything in a modern interactive dashboard.

Instead of simply displaying news headlines, the platform provides:

- AI-generated summaries
- Intelligent categorization
- Daily AI briefing
- Multi-agent article analysis
- Interactive article deep dives
- Automated email reports

The goal is to save users from reading dozens of news articles while still understanding everything important happening in the AI ecosystem.

---

# ✨ Features

### 📰 AI News Aggregation

Collects AI news from multiple sources including:

- Hugging Face Blog
- ArXiv
- TechCrunch AI
- VentureBeat AI
- MIT AI News
- Ars Technica
- Reddit
- X (via Nitter)

---

### 🤖 AI-Powered Summaries

Every article is automatically summarized using LLMs.

The summary explains:

- What happened
- Why it matters
- Key information

---

### 🏷 Intelligent Categorization

Articles are automatically classified into categories such as:

- Research
- Product Launch
- Industry
- Policy
- Open Source
- Tools

---

### 📄 Daily AI Briefing

Generates a complete daily briefing summarizing the most important developments across all collected articles.

---

### 🧠 Multi-Agent Article Analysis

The project includes a two-agent workflow for article exploration.

#### Agent 1 — Reader

- Fetches the complete article
- Extracts the readable content
- Falls back gracefully if the article cannot be retrieved

#### Agent 2 — Writer

Uses an LLM to generate:

- Overview
- Key Points
- Background & Context
- Why It Matters

This allows users to understand an article without visiting the original website.

---

### 📧 Daily Email Digest

Automatically sends a beautifully formatted HTML email containing:

- Daily briefing
- Top AI stories
- AI summaries

---

### 🎨 Interactive Dashboard

Modern dashboard built with:

- Responsive layout
- Dark theme
- Scroll progress
- Category badges
- Daily briefing
- Source statistics
- Interactive sidebar
- Manual refresh
- Auto refresh

---

# 🏗 Project Architecture

```
                    Scheduler
                        │
                        ▼
               News Collection
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
     RSS Feeds       Reddit         X (Nitter)
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                Article Deduplication
                        │
                        ▼
              AI Summarization (LLM)
                        │
                        ▼
            Daily Briefing Generation
                        │
                        ▼
                 Local JSON Storage
                        │
        ┌───────────────┼─────────────────┐
        ▼               ▼                 ▼
    Dashboard      Email Digest     Deep Dive API
```

---

# 🧠 Two-Agent Workflow

```
User clicks "Know More"

        │

        ▼

Reader Agent

↓

Fetch article

↓

Extract clean text

↓

Fallback if unavailable

        │

        ▼

Writer Agent

↓

Overview

↓

Key Points

↓

Context

↓

Implications

        │

        ▼

Interactive Sidebar
```

---

# 🛠 Tech Stack

## Backend

- Python
- FastAPI
- APScheduler
- HTTPX
- BeautifulSoup
- Feedparser

## AI

- Groq
- Mistral AI
- Llama 3.3 70B

## Frontend

- HTML
- CSS
- JavaScript

## Storage

- JSON

## Email

- Gmail SMTP

---

# 📂 Project Structure

```
AI-News-Intelligence/

│
├── article_agent.py
├── emailer.py
├── llm.py
├── main.py
├── scraper.py
├── storage.py
│
├── data/
│   └── news.json
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-news-intelligence.git
```

Move into the project

```bash
cd ai-news-intelligence
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file.

```
GROQ_API_KEY=YOUR_GROQ_KEY

MISTRAL_API_KEY=YOUR_MISTRAL_KEY

EMAIL_ADDRESS=your_email@gmail.com

EMAIL_PASSWORD=your_gmail_app_password

SCRAPE_INTERVAL_HOURS=6

DIGEST_HOUR=8

DIGEST_MINUTE=0
```

---

# ▶ Running the Application

Start the server

```bash
uvicorn main:app --reload
```

Open

```
http://127.0.0.1:8000
```

---

# 📡 API Endpoints

## Dashboard

```
GET /
```

---

## Get News

```
GET /api/news
```

Returns

```json
{
    "articles": [],
    "briefing": "",
    "last_scraped": ""
}
```

---

## Status

```
GET /api/status
```

Returns current scraper status.

---

## Trigger Scraper

```
POST /api/trigger
```

Starts the scraping pipeline manually.

---

## Deep Dive

```
POST /api/article-detail
```

Returns

```json
{
    "title": "",
    "overview": "",
    "key_points": [],
    "context": "",
    "implications": ""
}
```

---

# 🚀 Future Improvements

- Search functionality
- Category filtering
- Semantic duplicate detection
- Related articles
- Article embeddings
- PostgreSQL support
- User authentication
- AI chat with articles
- Bookmarking
- Reading history
- Vector search
- RAG-powered question answering
- Docker deployment

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome.

Feel free to fork the repository and submit a pull request.

----

# 👨‍💻 Author

**Kuldeep Amareliya**

- LinkedIn: https://www.linkedin.com/in/kuldeep-amareliya/

---

## ⭐ If you found this project useful, consider giving it a star!
