// ── Core domain types ─────────────────────────────────────────────────────

export interface Article {
  title: string;
  url: string;
  source: string;
  category?: string;
  published?: string | null;
  summary?: string;
  snippet?: string;
}

export interface NewsResponse {
  articles: Article[];
  briefing?: string;
  last_scraped?: string | null;
}

export interface ArticleDetail {
  title: string;
  source: string;
  url: string;
  category?: string;
  overview: string;
  key_points: string[];
  context?: string;
  implications?: string;
  fetched_from_source: boolean;
}

export interface ArticleDetailRequest {
  url: string;
  title: string;
  source: string;
  category?: string;
  snippet?: string;
  summary?: string;
}

// ── UI / status types ──────────────────────────────────────────────────────

export type StatusState = "" | "live" | "error";

export interface CategoryStyle {
  color: string;
  bg: string;
  border: string;
}

export type ToastType = "ok" | "err";

export interface ToastState {
  message: string;
  type: ToastType;
  visible: boolean;
}

export interface SourceInfo {
  count: number;
  url: string;
  type: string;
}
