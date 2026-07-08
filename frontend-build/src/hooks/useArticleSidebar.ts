import { useCallback, useEffect, useRef, useState } from "react";
import type { Article, ArticleDetail } from "../types";
import { fetchArticleDetail } from "../utils/api";

interface UseArticleSidebarResult {
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
  detail: ArticleDetail | null;
  openArticle: (article: Article) => void;
  close: () => void;
}

export function useArticleSidebar(): UseArticleSidebarResult {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<ArticleDetail | null>(null);

  const cacheRef = useRef<Map<string, ArticleDetail>>(new Map());
  const activeUrlRef = useRef<string | null>(null);

  const openArticle = useCallback((article: Article) => {
    // Re-open instantly from cache if it's the same article
    if (activeUrlRef.current === article.url && cacheRef.current.has(article.url)) {
      setDetail(cacheRef.current.get(article.url)!);
      setError(null);
      setIsLoading(false);
      setIsOpen(true);
      return;
    }

    activeUrlRef.current = article.url;
    setIsOpen(true);
    setIsLoading(true);
    setError(null);
    setDetail(null);

    fetchArticleDetail({
      url: article.url,
      title: article.title,
      source: article.source,
      category: article.category,
      snippet: article.snippet || "",
      summary: article.summary || "",
    })
      .then((data) => {
        cacheRef.current.set(article.url, data);
        setDetail(data);
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(`Could not load deep-dive: ${err.message}`);
        setIsLoading(false);
      });
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    // Keep activeUrlRef / cache so re-opening the same article is instant
  }, []);

  // Close on Escape key
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && isOpen) close();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [isOpen, close]);

  // Toggle body class for layout shift
  useEffect(() => {
    document.body.classList.toggle("sidebar-open", isOpen);
    return () => {
      document.body.classList.remove("sidebar-open");
    };
  }, [isOpen]);

  return { isOpen, isLoading, error, detail, openArticle, close };
}
