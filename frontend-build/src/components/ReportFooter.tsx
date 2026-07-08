import { fmtDateShort } from "../utils/format";

interface ReportFooterProps {
  lastScraped: string | null;
}

export function ReportFooter({ lastScraped }: ReportFooterProps) {
  return (
    <footer className="report-footer">
      <span>AI News Bot</span>
      <span className="footer-sep">·</span>
      <span>Powered by Groq & Mistral</span>
      <span className="footer-sep">·</span>
      <span>{fmtDateShort(lastScraped)}</span>
    </footer>
  );
}
