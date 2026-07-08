import { fmtDateShort, timeAgo } from "../utils/format";

interface ReportTitleBlockProps {
  articleCount: number;
  sourceCount: number;
  lastScraped: string | null;
}

export function ReportTitleBlock({
  articleCount,
  sourceCount,
  lastScraped,
}: ReportTitleBlockProps) {
  return (
    <div className="report-title-block">
      <div className="report-edition">Edition · {fmtDateShort(lastScraped)}</div>
      <h1 className="report-heading">AI & Tech News</h1>
      <p className="report-subheading">
        Last 24 hours · Sourced from top publications, Reddit & X
      </p>
      <div className="report-meta-row">
        <span className="meta-chip">{articleCount} stories</span>
        <span className="meta-sep">·</span>
        <span className="meta-chip">{sourceCount} sources</span>
        <span className="meta-sep">·</span>
        <span className="meta-chip">Updated {timeAgo(lastScraped)}</span>
      </div>
      <div className="jump-nav">
        <a href="#articles-section" className="jump-link">
          Stories ↓
        </a>
        <a href="#summary-section" className="jump-link">
          Summary ↓
        </a>
        <a href="#sources-section" className="jump-link">
          Sources ↓
        </a>
      </div>
    </div>
  );
}
