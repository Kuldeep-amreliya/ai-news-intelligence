# 🚀 AI News Intelligence

An AI-powered news intelligence platform that automatically collects the latest Artificial Intelligence news from trusted sources, generates intelligent summaries using Large Language Models (LLMs), performs multi-agent article analysis, and presents everything through a modern React dashboard with automated email reports.

---

## 📖 Overview

AI News Intelligence is an end-to-end AI news aggregation platform designed to help users stay up to date with the rapidly evolving AI ecosystem without reading dozens of articles every day.

The platform continuously gathers news from multiple trusted AI sources, removes duplicates, enriches each article using LLMs, categorizes the content, generates a daily AI briefing, and delivers everything through a clean and responsive dashboard.

Instead of simply displaying headlines, the platform provides:

- 🤖 AI-generated summaries
- 🏷 Intelligent article categorization
- 🧠 Multi-agent article analysis
- 📄 Daily AI briefing
- 📧 Automated HTML email digest
- ⚡ Modern React dashboard
- 📊 Source statistics
- 🔄 Automatic news refresh

---

# ✨ Features

## 📰 AI News Aggregation

Collects AI news from multiple trusted public sources including:

- Hugging Face Blog
- ArXiv (AI & Machine Learning)
- TechCrunch AI
- VentureBeat AI
- MIT AI News
- Ars Technica
- Reddit
- X (via Nitter)

The scraper periodically fetches new articles while avoiding duplicates.

---

## 🤖 AI-Powered Summaries

Every collected article is automatically summarized using Large Language Models.

Each summary explains:

- What happened
- Why it matters
- Key insights
- Important takeaways

This allows users to quickly understand articles without reading the full content.

---

## 🏷 Intelligent Categorization

Articles are automatically classified into categories such as:

- Research
- Product Launch
- Open Source
- Industry
- Policy
- AI Tools
- Models
- Infrastructure

---

## 📄 Daily AI Briefing

The system generates a complete AI briefing summarizing the most important developments of the day.

The briefing combines information from all collected articles into one concise report.

---

## 🧠 Multi-Agent Article Analysis

The platform includes a two-agent workflow for deep article exploration.

### 📖 Reader Agent

Responsible for:

- Fetching the original article
- Extracting clean readable content
- Removing unnecessary HTML
- Gracefully handling unavailable pages

---

### ✍ Writer Agent

Uses an LLM to generate:

- Overview
- Key Points
- Background
- Context
- Why It Matters
- Future Implications

This allows users to understand the complete article without visiting the original website.

---

## 🎨 Modern React Dashboard

The frontend is built using **React + TypeScript** and provides:

- Responsive UI
- Component-based architecture
- Interactive article cards
- Daily AI briefing
- Source statistics
- Category badges
- Sidebar article details
- Loading indicators
- Error handling
- Manual refresh
- Automatic refresh
- Modern clean design

---

## 📧 Automated Email Digest

The platform automatically generates beautifully formatted HTML email reports containing:

- Daily AI Briefing
- Top AI Stories
- AI-generated Summaries
- Source Links

Users can receive the latest AI news directly in their inbox.

---

# 🏗 System Architecture

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
                  JSON Storage
                        │
                        ▼
                  FastAPI Backend
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
 React Dashboard    Email Digest   Article API
```

---

# 🧠 Multi-Agent Workflow

```
User clicks "Know More"

        │

        ▼

 Reader Agent

        │

Fetch complete article

        │

Extract clean content

        │

Fallback if unavailable

        │

        ▼

 Writer Agent

        │

Generate:

• Overview

• Key Points

• Context

• Background

• Implications

        │

        ▼

React Sidebar
```

---

# 🛠 Tech Stack

## Frontend

- React
- TypeScript
- Vite
- CSS3

---

## Backend

- Python
- FastAPI
- APScheduler
- HTTPX
- BeautifulSoup
- Feedparser

---

## AI

- Groq API
- Llama 3.3 70B
- Mistral AI

---

## Storage

- JSON

---

## Email

- Gmail SMTP

---

# 📂 Project Structure

```
AI-News-Intelligence/

├── backend/
│
├── article_agent.py
├── emailer.py
├── llm.py
├── scraper.py
├── storage.py
├── main.py
│
├── data/
│   └── news.json
│
├── requirements.txt
│
├── frontend/
│
├── src/
│   ├── components/
│   ├── services/
│   ├── assets/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
│
├── public/
│
├── package.json
├── vite.config.ts
├── tsconfig.json
│
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/Kuldeep-amareliya/ai-news-intelligence.git
```

```
cd ai-news-intelligence
```

---

## Backend Setup

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Frontend Setup

Install packages

```bash
npm install
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
GROQ_API_KEY=YOUR_GROQ_API_KEY

MISTRAL_API_KEY=YOUR_MISTRAL_API_KEY

EMAIL_ADDRESS=YOUR_EMAIL

EMAIL_PASSWORD=YOUR_APP_PASSWORD

SCRAPE_INTERVAL_HOURS=6

DIGEST_HOUR=8

DIGEST_MINUTE=0
```

---

# ▶ Running the Application

## Start Backend

```bash
uvicorn main:app --reload
```

Backend:

```
http://127.0.0.1:8000
```

---

## Start Frontend

```bash
npm run dev
```

Frontend:

```
http://localhost:5173
```

---

# 📡 API Endpoints

## Dashboard

```
GET /
```

Returns frontend dashboard.

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

## Article Deep Dive

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

- PostgreSQL support
- Docker deployment
- Redis caching
- Vector Database
- Semantic Search
- AI Chat with Articles
- RAG-powered Question Answering
- User Authentication
- Saved Articles
- Reading History
- Related Articles
- WebSocket Live Updates
- Mobile Application

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome.

If you'd like to improve the project:

1. Fork the repository.
2. Create your feature branch.
3. Commit your changes.
4. Push to your branch.
5. Open a Pull Request.

---

# 👨‍💻 Author

**Kuldeep Amareliya**

AI/ML Engineer

- GitHub: https://github.com/Kuldeep-amareliya
- LinkedIn: https://www.linkedin.com/in/kuldeep-amareliya/

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It helps others discover the project and supports future development.
