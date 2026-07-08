import type { StatusState } from "../types";

interface HeaderProps {
  status: StatusState;
  statusLabel: string;
  refreshing: boolean;
  onRefresh: () => void;
  scrollProgress: number;
}

export function Header({
  status,
  statusLabel,
  refreshing,
  onRefresh,
  scrollProgress,
}: HeaderProps) {
  return (
    <header className="site-header">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-dot"></span>
          <span>
            AI News <span className="logo-dim">Daily Report</span>
          </span>
        </div>
        <div className="header-right">
          <span className="status-pill">
            <span className={`status-dot ${status}`}></span>
            <span>{statusLabel}</span>
          </span>
          <button
            className={`btn-refresh ${refreshing ? "spinning" : ""}`}
            onClick={onRefresh}
          >
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
              <polyline points="23 4 23 10 17 10" />
              <polyline points="1 20 1 14 7 14" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            Fetch latest
          </button>
        </div>
      </div>
      <div
        className="scroll-progress"
        style={{ "--progress": `${scrollProgress}%` } as React.CSSProperties}
      ></div>
    </header>
  );
}
