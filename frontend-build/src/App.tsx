import { useMemo } from "react";
import { Header } from "./components/Header";
import { ReportTitleBlock } from "./components/ReportTitleBlock";
import { ArticlesSection } from "./components/ArticlesSection";
import { SummarySection } from "./components/SummarySection";
import { SourcesSection } from "./components/SourcesSection";
import { ReportFooter } from "./components/ReportFooter";
import { BackToTop } from "./components/BackToTop";
import { Toast } from "./components/Toast";
import { DetailSidebar } from "./components/DetailSidebar";
import { ErrorState } from "./components/ErrorState";

import { useNews } from "./hooks/useNews";
import { useScrollProgress } from "./hooks/useScrollProgress";
import { useArticleSidebar } from "./hooks/useArticleSidebar";
import { useToast } from "./hooks/useToast";

// Cap the report to the top N stories — keeps this a "daily digest",
// not a dump of everything scraped.
const MAX_ARTICLES = 15;

function App() {
  const {
    articles: allArticles,
    briefing,
    lastScraped,
    loading,
    errored,
    status,
    statusLabel,
    refreshing,
    refresh,
  } = useNews();

  const { progress, showBackTop } = useScrollProgress();
  const sidebar = useArticleSidebar();
  const { toast, showToast } = useToast();

  // Every section (articles, summary, sources, links) uses this same
  // trimmed list so counts stay consistent across the page.
  const articles = useMemo(
    () => allArticles.slice(0, MAX_ARTICLES),
    [allArticles]
  );

  const sourceCount = useMemo(
    () => new Set(articles.map((a) => a.source)).size,
    [articles]
  );

  async function handleRefresh() {
    showToast("Scrape started — new stories appear in ~60s", "ok");
    await refresh();
  }

  return (
    <>
      <Header
        status={status}
        statusLabel={statusLabel}
        refreshing={refreshing}
        onRefresh={handleRefresh}
        scrollProgress={progress}
      />

      <div className="report-wrap">
        <ReportTitleBlock
          articleCount={articles.length}
          sourceCount={sourceCount}
          lastScraped={lastScraped}
        />

        {errored ? (
          <ErrorState />
        ) : (
          <>
            <ArticlesSection
              articles={articles}
              loading={loading}
              onKnowMore={sidebar.openArticle}
            />

            <SummarySection
              briefing={briefing}
              articles={articles}
              lastScraped={lastScraped}
            />

            <SourcesSection articles={articles} />
          </>
        )}

        <ReportFooter lastScraped={lastScraped} />
      </div>

      <BackToTop visible={showBackTop} />
      <Toast toast={toast} />

      <DetailSidebar
        isOpen={sidebar.isOpen}
        isLoading={sidebar.isLoading}
        error={sidebar.error}
        detail={sidebar.detail}
        onClose={sidebar.close}
      />
    </>
  );
}

export default App;