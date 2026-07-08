import type { Article } from "../types";
import { catStyle } from "../utils/category";
import { timeAgo } from "../utils/format";

interface ArticleEntryProps {
  article: Article;
  index: number;
  onKnowMore: (article: Article) => void;
}

export function ArticleEntry({ article, index, onKnowMore }: ArticleEntryProps) {
  const cs = catStyle(article.category);
  const cat = article.category || "AI News";
  const hasSummary = !!article.summary && article.summary.trim().length > 0;
  const hasSnippet =
    !!article.snippet && article.snippet.trim().length > 0 && !hasSummary;

  return (
    <article className="article-entry" id={`art-${index + 1}`}>
      <div className="ae-meta">
        <span className="ae-num">#{String(index + 1).padStart(2, "0")}</span>
        <span
          className="ae-cat"
          style={{ color: cs.color, background: cs.bg, borderColor: cs.border }}
        >
          {cat}
        </span>
        <span className="ae-source">{article.source}</span>
        <span className="ae-time">{timeAgo(article.published)}</span>
      </div>

      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="ae-title"
      >
        {article.title}
      </a>

      {hasSummary && <p className="ae-summary">{article.summary}</p>}

      {hasSnippet && (
        <div className="ae-snippet">
          <div className="ae-snippet-label">From the source</div>
          <p className="ae-snippet-text">{article.snippet}</p>
        </div>
      )}

      <div className="ae-actions">
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="ae-read"
        >
          Read full story on {article.source}
          <svg
            width="13"
            height="13"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="7" y1="17" x2="17" y2="7" />
            <polyline points="7 7 17 7 17 17" />
          </svg>
        </a>

        <button
          className="ae-know-more"
          title="Get a detailed AI-generated breakdown of this story"
          onClick={() => onKnowMore(article)}
        >
          Know more about this
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        </button>
      </div>
    </article>
  );
}
