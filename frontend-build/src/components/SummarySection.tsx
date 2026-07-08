import { useMemo } from "react";
import type { Article } from "../types";
import { catStyle } from "../utils/category";
import { fmtDate } from "../utils/format";

interface SummarySectionProps {
  briefing: string;
  articles: Article[];
  lastScraped: string | null;
}

export function SummarySection({
  briefing,
  articles,
  lastScraped,
}: SummarySectionProps) {
  const sortedCategories = useMemo(() => {
    const counts: Record<string, number> = {};
    articles.forEach((a) => {
      const c = a.category || "Other";
      counts[c] = (counts[c] || 0) + 1;
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [articles]);

  if (!briefing && articles.length === 0) return null;

  return (
    <section id="summary-section" className="summary-section">
      <div className="section-label">
        <span className="section-num">02</span>
        <span className="section-title">Daily Briefing</span>
      </div>

      <div className="summary-card">
        <div className="summary-icon">◈</div>
        <p className="summary-text">
          {briefing || "Briefing not yet generated — LLM may still be processing."}
        </p>
        <div className="summary-footer">
          Generated from {articles.length} stories · {fmtDate(lastScraped)}
        </div>
      </div>

      <div className="cat-breakdown">
        {sortedCategories.map(([cat, n]) => {
          const cs = catStyle(cat);
          return (
            <div className="cat-card" key={cat}>
              <span className="cat-card-name" style={{ color: cs.color }}>
                {cat}
              </span>
              <span className="cat-card-count" style={{ color: cs.color }}>
                {n}
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
