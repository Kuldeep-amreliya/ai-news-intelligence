import type { Article } from "../types";
import { ArticleEntry } from "./ArticleEntry";
import { SkeletonArticles } from "./SkeletonArticles";

interface ArticlesSectionProps {
  articles: Article[];
  loading: boolean;
  onKnowMore: (article: Article) => void;
}

export function ArticlesSection({
  articles,
  loading,
  onKnowMore,
}: ArticlesSectionProps) {
  return (
    <section id="articles-section">
      <div className="section-label">
        <span className="section-num">01</span>
        <span className="section-title">Today's Stories</span>
        <span className="section-count">
          {!loading && `${articles.length} total`}
        </span>
      </div>

      {loading && <SkeletonArticles />}

      {!loading && (
        <div id="articles-list">
          {articles.length === 0 ? (
            <div style={{ padding: "60px 0", textAlign: "center", color: "#444" }}>
              No stories collected yet. Click "Fetch latest" to trigger a scrape.
            </div>
          ) : (
            articles.map((article, i) => (
              <ArticleEntry
                key={article.url || i}
                article={article}
                index={i}
                onKnowMore={onKnowMore}
              />
            ))
          )}
        </div>
      )}
    </section>
  );
}
