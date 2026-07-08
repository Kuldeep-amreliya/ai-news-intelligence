import type { ArticleDetail } from "../types";
import { catStyle } from "../utils/category";
import { domainOf } from "../utils/format";

interface DetailSidebarProps {
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
  detail: ArticleDetail | null;
  onClose: () => void;
}

export function DetailSidebar({
  isOpen,
  isLoading,
  error,
  detail,
  onClose,
}: DetailSidebarProps) {
  return (
    <>
      <div
        className={`sidebar-overlay ${isOpen ? "visible" : ""}`}
        onClick={onClose}
      ></div>

      <aside
        className={`detail-sidebar ${isOpen ? "open" : ""}`}
        role="complementary"
        aria-label="Article deep-dive"
      >
        <div className="sidebar-header">
          <div className="sidebar-header-left">
            <span className="sidebar-label">Deep Dive</span>
          </div>
          <button
            className="sidebar-close"
            title="Close (Esc)"
            aria-label="Close sidebar"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        <div className="sidebar-body">
          {isLoading && (
            <div className="sidebar-loading">
              <div className="sidebar-spinner"></div>
              <span>Analysing story</span>
              <span className="sidebar-loading-step">
                Fetching article content...
              </span>
            </div>
          )}

          {!isLoading && error && (
            <div className="sidebar-error">
              <div className="sidebar-error-icon">⚠</div>
              <p>{error}</p>
            </div>
          )}

          {!isLoading && !error && detail && <SidebarContent detail={detail} />}
        </div>
      </aside>
    </>
  );
}

function SidebarContent({ detail }: { detail: ArticleDetail }) {
  const cs = catStyle(detail.category);
  const domain = domainOf(detail.url);
  const overviewParas = (detail.overview || "").split("\n").filter(Boolean);
  const contextParas = (detail.context || "").split("\n").filter(Boolean);
  const implicationParas = (detail.implications || "").split("\n").filter(Boolean);

  return (
    <>
      <div className="sb-meta">
        <span
          className="sb-cat"
          style={{ color: cs.color, background: cs.bg, borderColor: cs.border }}
        >
          {detail.category || "AI News"}
        </span>
        <span className="sb-source">{detail.source}</span>
        {detail.fetched_from_source ? (
          <span
            style={{
              fontSize: 10,
              color: "var(--green)",
              fontFamily: "var(--font-mono)",
              marginLeft: "auto",
            }}
          >
            ● Full article
          </span>
        ) : (
          <span
            style={{
              fontSize: 10,
              color: "var(--gray-3)",
              fontFamily: "var(--font-mono)",
              marginLeft: "auto",
            }}
          >
            ◌ Summary only
          </span>
        )}
      </div>

      <h2 className="sb-title">{detail.title}</h2>

      <div className="sb-divider"></div>

      <div className="sb-section-heading">Overview</div>
      <div className="sb-content">
        {overviewParas.length > 0 ? (
          overviewParas.map((p, i) => <p key={i}>{p}</p>)
        ) : (
          <p>Overview not available.</p>
        )}
      </div>

      {detail.key_points && detail.key_points.length > 0 && (
        <>
          <div className="sb-divider"></div>
          <div className="sb-section-heading">Key Points</div>
          <ul className="sb-points">
            {detail.key_points.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </>
      )}

      {contextParas.length > 0 && (
        <>
          <div className="sb-divider"></div>
          <div className="sb-section-heading">Background & Context</div>
          <div className="sb-content">
            {contextParas.map((p, i) => (
              <p key={i}>{p}</p>
            ))}
          </div>
        </>
      )}

      {implicationParas.length > 0 && (
        <>
          <div className="sb-divider"></div>
          <div className="sb-section-heading">Why It Matters</div>
          <div className="sb-content">
            {implicationParas.map((p, i) => (
              <p key={i}>{p}</p>
            ))}
          </div>
        </>
      )}

      <a
        href={detail.url}
        target="_blank"
        rel="noopener noreferrer"
        className="sb-source-link"
      >
        <div className="sb-source-link-label">
          Read original article
          <span className="sb-source-link-domain">{domain}</span>
        </div>
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
    </>
  );
}
