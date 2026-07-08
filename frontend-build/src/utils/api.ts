import type { ArticleDetail, ArticleDetailRequest, NewsResponse } from "../types";

export async function fetchNewsData(): Promise<NewsResponse> {
  const res = await fetch("/api/news");
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function triggerScrape(): Promise<void> {
  await fetch("/api/trigger", { method: "POST" });
}

export async function fetchArticleDetail(
  payload: ArticleDetailRequest
): Promise<ArticleDetail> {
  const res = await fetch("/api/article-detail", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}
