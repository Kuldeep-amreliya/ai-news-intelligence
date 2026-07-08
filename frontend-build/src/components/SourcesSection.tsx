import { useMemo } from "react";
import type { Article, SourceInfo } from "../types";
import { domainOf, sourceType } from "../utils/format";

interface SourcesSectionProps {
  articles: Article[];
}

export function SourcesSection({ articles }: SourcesSectionProps) {
  const sortedSources = useMemo(() => {
    const counts: Record<string, SourceInfo> = {};
    articles.forEach((a) => {
      if (!counts[a.source]) {
        counts[a.source] = { count: 0, url: a.url, type: sourceType(a.source) };
      }
      counts[a.source].count++;
    });
    return Object.entries(counts).sort((a, b) => b[1].count - a[1].count);
  }, [articles]);

  if (articles.length === 0) return null;

  return (
    <section id="sources-section" className="sources-section">
      <div className="section-label">
        <span className="section-num">03</span>
        <span className="section-title">All Sources</span>
        <span className="section-count">{sortedSources.length} sources</span>
      </div>

      <p className="sources-intro">
        Every publication, subreddit and account from which today's stories were
        collected.
      </p>

      <div className="sources-table">
        {sortedSources.map(([src, info]) => {
          const domain = domainOf(info.url);
          return (
            <div className="source-row" key={src}>
              <div>
                <div className="source-row-name">{src}</div>
                {domain && <div className="source-row-domain">{domain}</div>}
              </div>
              <span className="source-row-type">{info.type}</span>
              <span className="source-row-count">{info.count}</span>
            </div>
          );
        })}
      </div>

      <div className="section-label" style={{ marginTop: 48 }}>
        <span className="section-num">04</span>
        <span className="section-title">All Article Links</span>
      </div>
      <p className="sources-intro">
        Direct links to every story, in the order they appeared above.
      </p>

      <ol className="links-list">
        {articles.map((a, i) => {
          const domain = domainOf(a.url);
          return (
            <li className="link-item" key={a.url || i}>
              <div className="link-item-content">
                <a
                  href={a.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="link-title"
                >
                  {a.title}
                </a>
                <span className="link-source-label">{a.source}</span>
              </div>
              <a
                href={a.url}
                target="_blank"
                rel="noopener noreferrer"
                className="link-url"
              >
                {domain} ↗
              </a>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
