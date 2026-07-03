/* app.js — AI News Daily Report */

// ── Category style map ────────────────────────────────────────────────────────
const CAT = {
  "Research":       { color: "#c084fc", bg: "rgba(192,132,252,0.1)",  border: "rgba(192,132,252,0.3)" },
  "Product Launch": { color: "#fbbf24", bg: "rgba(251,191,36,0.1)",   border: "rgba(251,191,36,0.3)" },
  "Policy":         { color: "#f87171", bg: "rgba(248,113,113,0.1)",  border: "rgba(248,113,113,0.3)" },
  "Open Source":    { color: "#4ade80", bg: "rgba(74,222,128,0.1)",   border: "rgba(74,222,128,0.3)" },
  "Industry":       { color: "#60a5fa", bg: "rgba(96,165,250,0.1)",   border: "rgba(96,165,250,0.3)" },
  "Tool":           { color: "#f472b6", bg: "rgba(244,114,182,0.1)",  border: "rgba(244,114,182,0.3)" },
};
const DEFAULT_CAT = { color: "#4ade80", bg: "rgba(74,222,128,0.1)", border: "rgba(74,222,128,0.3)" };

function catStyle(cat) { return CAT[cat] || DEFAULT_CAT; }

// ── DOM refs ──────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const loadingState   = $("loading-state");
const articlesList   = $("articles-list");
const articleCount   = $("article-count");
const summarySection = $("summary-section");
const summaryText    = $("summary-text");
const summaryFooter  = $("summary-footer");
const catBreakdown   = $("cat-breakdown");
const sourcesSection = $("sources-section");
const sourcesTable   = $("sources-table");
const sourcesCount   = $("sources-count");
const linksList      = $("links-list");
const statusDot      = $("status-dot");
const statusLabel    = $("status-label");
const refreshBtn     = $("refresh-btn");
const scrollProg     = $("scroll-progress");
const backTop        = $("back-top");
const toast          = $("toast");
const metaCount      = $("meta-count");
const metaSources    = $("meta-sources");
const metaUpdated    = $("meta-updated");
const reportEdition  = $("report-edition");
const footerDate     = $("footer-date");

// Sidebar DOM refs
const detailSidebar  = $("detail-sidebar");
const sidebarOverlay = $("sidebar-overlay");
const sidebarBody    = $("sidebar-body");
const sidebarClose   = $("sidebar-close");

// ── Helpers ───────────────────────────────────────────────────────────────────

function timeAgo(iso) {
  if (!iso) return "";
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60)    return "just now";
  if (s < 3600)  return `${Math.floor(s/60)}m ago`;
  if (s < 86400) return `${Math.floor(s/3600)}h ago`;
  return `${Math.floor(s/86400)}d ago`;
}

function fmtDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("en-US", { weekday:"long", month:"long", day:"numeric", year:"numeric" });
}

function fmtDateShort(iso) {
  if (!iso) return new Date().toLocaleDateString("en-US", { month:"short", day:"numeric", year:"numeric" });
  return new Date(iso).toLocaleDateString("en-US", { month:"short", day:"numeric", year:"numeric" });
}

function domainOf(url) {
  try { return new URL(url).hostname.replace(/^www\./, ""); }
  catch { return ""; }
}

function sourceType(source) {
  if (source.startsWith("r/"))         return "Reddit";
  if (source.includes("Nitter") || source.includes("X (")) return "X / Twitter";
  return "Publication";
}

function showToast(msg, type = "ok") {
  toast.textContent = msg;
  toast.className = `toast show ${type}`;
  setTimeout(() => { toast.className = "toast"; }, 3500);
}

function setStatus(state, msg) {
  statusLabel.textContent = msg;
  statusDot.className = `status-dot ${state}`;
}

function escHtml(str) {
  if (!str) return "";
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

// ── Scroll progress + back-to-top ────────────────────────────────────────────

window.addEventListener("scroll", () => {
  const total = document.documentElement.scrollHeight - window.innerHeight;
  const pct   = total > 0 ? (window.scrollY / total * 100).toFixed(1) : 0;
  scrollProg.style.setProperty("--progress", `${pct}%`);
  backTop.classList.toggle("visible", window.scrollY > 600);
}, { passive: true });

backTop.addEventListener("click", () => {
  // FIX: add .used so it stays green after first click
  backTop.classList.add("used");
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// ═══════════════════════════════════════════════════════════════════════════════
// SIDEBAR — open / close / fetch / render
// ═══════════════════════════════════════════════════════════════════════════════

// Track active article to avoid re-fetching when re-opening same one
let activeSidebarUrl = null;

function openSidebar() {
  detailSidebar.classList.add("open");
  sidebarOverlay.classList.add("visible");
  document.body.classList.add("sidebar-open");
}

function closeSidebar() {
  detailSidebar.classList.remove("open");
  sidebarOverlay.classList.remove("visible");
  document.body.classList.remove("sidebar-open");
  // Don't reset activeSidebarUrl so re-open is instant from cache
}

sidebarClose.addEventListener("click", closeSidebar);
sidebarOverlay.addEventListener("click", closeSidebar);

// Close on Escape
document.addEventListener("keydown", e => {
  if (e.key === "Escape" && detailSidebar.classList.contains("open")) closeSidebar();
});

// ── Sidebar loading state ─────────────────────────────────────────────────────

function setSidebarLoading(step = "Fetching article...") {
  sidebarBody.innerHTML = `
    <div class="sidebar-loading">
      <div class="sidebar-spinner"></div>
      <span>Analysing story</span>
      <span class="sidebar-loading-step">${escHtml(step)}</span>
    </div>`;
}

function setSidebarError(msg) {
  sidebarBody.innerHTML = `
    <div class="sidebar-error">
      <div class="sidebar-error-icon">⚠</div>
      <p>${escHtml(msg)}</p>
    </div>`;
}

// ── Render sidebar content ────────────────────────────────────────────────────

/*
  Expected shape from /api/article-detail:
  {
    title: string,
    source: string,
    url: string,
    category: string,
    overview: string,           // 2-3 sentence what happened
    key_points: string[],       // bullet list of key facts
    context: string,            // why it matters / background
    implications: string,       // what this means going forward
    fetched_from_source: bool   // whether full text was available
  }
*/
function renderSidebarContent(data) {
  const cs = catStyle(data.category);
  const domain = domainOf(data.url);

  // Build key points list
  const pointsHtml = (data.key_points || []).map(p =>
    `<li>${escHtml(p)}</li>`
  ).join("");

  // Badge showing whether we got the full article or fell back to snippet
  const fetchBadge = data.fetched_from_source
    ? `<span style="font-size:10px;color:var(--green);font-family:var(--font-mono);margin-left:auto;">● Full article</span>`
    : `<span style="font-size:10px;color:var(--gray-3);font-family:var(--font-mono);margin-left:auto;">◌ Summary only</span>`;

  sidebarBody.innerHTML = `
    <!-- Meta row -->
    <div class="sb-meta">
      <span class="sb-cat" style="color:${cs.color};background:${cs.bg};border-color:${cs.border};">${escHtml(data.category || "AI News")}</span>
      <span class="sb-source">${escHtml(data.source)}</span>
      ${fetchBadge}
    </div>

    <!-- Title -->
    <h2 class="sb-title">${escHtml(data.title)}</h2>

    <div class="sb-divider"></div>

    <!-- Overview -->
    <div class="sb-section-heading">Overview</div>
    <div class="sb-content">
      ${data.overview
        ? data.overview.split("\n").filter(Boolean).map(p => `<p>${escHtml(p)}</p>`).join("")
        : "<p>Overview not available.</p>"}
    </div>

    ${pointsHtml ? `
    <div class="sb-divider"></div>
    <div class="sb-section-heading">Key Points</div>
    <ul class="sb-points">${pointsHtml}</ul>
    ` : ""}

    ${data.context ? `
    <div class="sb-divider"></div>
    <div class="sb-section-heading">Background & Context</div>
    <div class="sb-content">
      ${data.context.split("\n").filter(Boolean).map(p => `<p>${escHtml(p)}</p>`).join("")}
    </div>
    ` : ""}

    ${data.implications ? `
    <div class="sb-divider"></div>
    <div class="sb-section-heading">Why It Matters</div>
    <div class="sb-content">
      ${data.implications.split("\n").filter(Boolean).map(p => `<p>${escHtml(p)}</p>`).join("")}
    </div>
    ` : ""}

    <!-- Original source link -->
    <a href="${escHtml(data.url)}" target="_blank" rel="noopener noreferrer" class="sb-source-link">
      <div class="sb-source-link-label">
        Read original article
        <span class="sb-source-link-domain">${escHtml(domain)}</span>
      </div>
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="7" y1="17" x2="17" y2="7"/>
        <polyline points="7 7 17 7 17 17"/>
      </svg>
    </a>
  `;
}

// ── Simple cache to avoid duplicate LLM calls in the same session ─────────────
const sidebarCache = new Map(); // url → rendered data

// ── Open sidebar for a given article ─────────────────────────────────────────

async function openArticleDetail(article) {
  // If same article, just re-open
  if (activeSidebarUrl === article.url && sidebarCache.has(article.url)) {
    renderSidebarContent(sidebarCache.get(article.url));
    openSidebar();
    return;
  }

  activeSidebarUrl = article.url;
  openSidebar();
  setSidebarLoading("Fetching article content...");

  try {
    const res = await fetch("/api/article-detail", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url:      article.url,
        title:    article.title,
        source:   article.source,
        category: article.category,
        snippet:  article.snippet || "",
        summary:  article.summary || "",
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    sidebarCache.set(article.url, data);
    renderSidebarContent(data);

  } catch (err) {
    setSidebarError(`Could not load deep-dive: ${err.message}`);
  }
}

// ── Render articles ───────────────────────────────────────────────────────────

// Keep article data accessible for sidebar clicks (indexed by article index)
let _articlesData = [];

function renderArticles(articles) {
  _articlesData = articles;
  loadingState.style.display = "none";

  if (!articles.length) {
    articlesList.innerHTML = `
      <div style="padding:60px 0;text-align:center;color:#444;">
        No stories collected yet. Click "Fetch latest" to trigger a scrape.
      </div>`;
    return;
  }

  articlesList.innerHTML = articles.map((a, i) => {
    const cs         = catStyle(a.category);
    const cat        = a.category || "AI News";
    const hasSummary = a.summary && a.summary.trim().length > 0;
    const hasSnippet = a.snippet && a.snippet.trim().length > 0 && !hasSummary;

    return `
    <article class="article-entry" id="art-${i+1}">

      <!-- Meta row -->
      <div class="ae-meta">
        <span class="ae-num">#${String(i+1).padStart(2,"0")}</span>
        <span class="ae-cat" style="color:${cs.color};background:${cs.bg};border-color:${cs.border};">${cat}</span>
        <span class="ae-source">${a.source}</span>
        <span class="ae-time">${timeAgo(a.published)}</span>
      </div>

      <!-- Headline — still opens original URL -->
      <a href="${escHtml(a.url)}" target="_blank" rel="noopener noreferrer" class="ae-title">
        ${escHtml(a.title)}
      </a>

      <!-- LLM summary -->
      ${hasSummary ? `<p class="ae-summary">${escHtml(a.summary)}</p>` : ""}

      <!-- Original snippet fallback -->
      ${hasSnippet ? `
        <div class="ae-snippet">
          <div class="ae-snippet-label">From the source</div>
          <p class="ae-snippet-text">${escHtml(a.snippet)}</p>
        </div>` : ""}

      <!-- Actions row: Read link + Know More -->
      <div class="ae-actions">
        <a href="${escHtml(a.url)}" target="_blank" rel="noopener noreferrer" class="ae-read">
          Read full story on ${escHtml(a.source)}
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="7" y1="17" x2="17" y2="7"/>
            <polyline points="7 7 17 7 17 17"/>
          </svg>
        </a>

        <button
          class="ae-know-more"
          data-index="${i}"
          title="Get a detailed AI-generated breakdown of this story"
        >
          Know more about this
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12"/>
            <polyline points="12 5 19 12 12 19"/>
          </svg>
        </button>
      </div>

    </article>`;
  }).join("");

  // Attach click handlers to all "Know more" buttons
  articlesList.querySelectorAll(".ae-know-more").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.dataset.index, 10);
      const article = _articlesData[idx];
      if (article) openArticleDetail(article);
    });
  });
}

// ── Render summary section ────────────────────────────────────────────────────

function renderSummary(briefing, articles, lastScraped) {
  if (!briefing && !articles.length) return;

  summarySection.style.display = "block";
  summaryText.textContent = briefing || "Briefing not yet generated — LLM may still be processing.";
  summaryFooter.innerHTML = `Generated from ${articles.length} stories · ${fmtDate(lastScraped)}`;

  const counts = {};
  articles.forEach(a => { const c = a.category || "Other"; counts[c] = (counts[c]||0)+1; });
  const sorted = Object.entries(counts).sort((a,b) => b[1]-a[1]);

  catBreakdown.innerHTML = sorted.map(([cat, n]) => {
    const cs = catStyle(cat);
    return `
    <div class="cat-card">
      <span class="cat-card-name" style="color:${cs.color};">${cat}</span>
      <span class="cat-card-count" style="color:${cs.color};">${n}</span>
    </div>`;
  }).join("");
}

// ── Render sources section ────────────────────────────────────────────────────

function renderSources(articles) {
  if (!articles.length) return;
  sourcesSection.style.display = "block";

  const counts = {};
  articles.forEach(a => {
    if (!counts[a.source]) counts[a.source] = { count: 0, url: a.url, type: sourceType(a.source) };
    counts[a.source].count++;
  });

  const sorted = Object.entries(counts).sort((a,b) => b[1].count - a[1].count);
  sourcesCount.textContent = `${sorted.length} sources`;

  sourcesTable.innerHTML = sorted.map(([src, info]) => {
    const domain = domainOf(info.url);
    return `
    <div class="source-row">
      <div>
        <div class="source-row-name">${escHtml(src)}</div>
        ${domain ? `<div class="source-row-domain">${domain}</div>` : ""}
      </div>
      <span class="source-row-type">${info.type}</span>
      <span class="source-row-count">${info.count}</span>
    </div>`;
  }).join("");

  linksList.innerHTML = articles.map((a, i) => {
    const domain = domainOf(a.url);
    return `
    <li class="link-item">
      <div class="link-item-content">
        <a href="${escHtml(a.url)}" target="_blank" rel="noopener noreferrer" class="link-title">
          ${escHtml(a.title)}
        </a>
        <span class="link-source-label">${escHtml(a.source)}</span>
      </div>
      <a href="${escHtml(a.url)}" target="_blank" rel="noopener noreferrer" class="link-url">
        ${domain} ↗
      </a>
    </li>`;
  }).join("");
}

// ── Render header meta ────────────────────────────────────────────────────────

function renderMeta(articles, lastScraped) {
  const uniqueSources = new Set(articles.map(a => a.source)).size;
  reportEdition.textContent = `Edition · ${fmtDateShort(lastScraped)}`;
  metaCount.textContent     = `${articles.length} stories`;
  metaSources.textContent   = `${uniqueSources} sources`;
  metaUpdated.textContent   = `Updated ${timeAgo(lastScraped)}`;
  footerDate.textContent    = fmtDateShort(lastScraped);
  articleCount.textContent  = `${articles.length} total`;
}

// ── Main fetch ────────────────────────────────────────────────────────────────

async function fetchNews() {
  setStatus("", "Loading...");
  try {
    const res  = await fetch("/api/news");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    const articles    = data.articles    || [];
    const briefing    = data.briefing    || "";
    const lastScraped = data.last_scraped || null;

    renderMeta(articles, lastScraped);
    renderArticles(articles);
    renderSummary(briefing, articles, lastScraped);
    renderSources(articles);

    if (articles.length > 0) {
      setStatus("live", `Live · ${timeAgo(lastScraped)}`);
    } else {
      setStatus("", "Awaiting first scrape");
    }

  } catch (err) {
    loadingState.style.display = "none";
    setStatus("error", "Failed to load");
    articlesList.innerHTML = `
      <div style="padding:60px 0;text-align:center;">
        <p style="color:#f87171;font-size:14px;margin-bottom:8px;">Could not reach the server.</p>
        <p style="color:#444;font-size:12px;">Make sure the FastAPI server is running on port 8000.</p>
      </div>`;
  }
}

// ── Manual trigger ────────────────────────────────────────────────────────────

refreshBtn.addEventListener("click", async () => {
  if (refreshBtn.classList.contains("spinning")) return;
  refreshBtn.classList.add("spinning");
  setStatus("", "Triggering scrape...");
  showToast("Scrape started — new stories appear in ~60s", "ok");

  try {
    await fetch("/api/trigger", { method: "POST" });
    setTimeout(fetchNews, 15000);
  } catch {
    showToast("Could not trigger scrape", "err");
  } finally {
    setTimeout(() => refreshBtn.classList.remove("spinning"), 2500);
  }
});

// ── Auto-refresh every 5 min ──────────────────────────────────────────────────

fetchNews();
setInterval(fetchNews, 5 * 60 * 1000);