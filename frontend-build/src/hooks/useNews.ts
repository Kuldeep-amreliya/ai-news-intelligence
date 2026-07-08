import { useCallback, useEffect, useRef, useState } from "react";
import type { Article, StatusState } from "../types";
import { fetchNewsData, triggerScrape } from "../utils/api";
import { timeAgo } from "../utils/format";

const AUTO_REFRESH_MS = 5 * 60 * 1000;

interface UseNewsResult {
  articles: Article[];
  briefing: string;
  lastScraped: string | null;
  loading: boolean;
  errored: boolean;
  status: StatusState;
  statusLabel: string;
  refreshing: boolean;
  refresh: () => Promise<void>;
}

export function useNews(): UseNewsResult {
  const [articles, setArticles] = useState<Article[]>([]);
  const [briefing, setBriefing] = useState("");
  const [lastScraped, setLastScraped] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [errored, setErrored] = useState(false);
  const [status, setStatus] = useState<StatusState>("");
  const [statusLabel, setStatusLabel] = useState("Loading...");
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setStatus("");
    setStatusLabel("Loading...");
    try {
      const data = await fetchNewsData();
      const items = data.articles || [];
      setArticles(items);
      setBriefing(data.briefing || "");
      setLastScraped(data.last_scraped || null);
      setErrored(false);

      if (items.length > 0) {
        setStatus("live");
        setStatusLabel(`Live · ${timeAgo(data.last_scraped)}`);
      } else {
        setStatus("");
        setStatusLabel("Awaiting first scrape");
      }
    } catch {
      setErrored(true);
      setStatus("error");
      setStatusLabel("Failed to load");
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    if (refreshing) return;
    setRefreshing(true);
    setStatus("");
    setStatusLabel("Triggering scrape...");
    try {
      await triggerScrape();
      setTimeout(load, 15000);
    } finally {
      setTimeout(() => setRefreshing(false), 2500);
    }
  }, [load, refreshing]);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    load();
    intervalRef.current = setInterval(load, AUTO_REFRESH_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [load]);

  return {
    articles,
    briefing,
    lastScraped,
    loading,
    errored,
    status,
    statusLabel,
    refreshing,
    refresh,
  };
}
