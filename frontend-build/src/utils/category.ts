import type { CategoryStyle } from "../types";

// ── Category style map ────────────────────────────────────────────────────
const CAT: Record<string, CategoryStyle> = {
  Research: {
    color: "#c084fc",
    bg: "rgba(192,132,252,0.1)",
    border: "rgba(192,132,252,0.3)",
  },
  "Product Launch": {
    color: "#fbbf24",
    bg: "rgba(251,191,36,0.1)",
    border: "rgba(251,191,36,0.3)",
  },
  Policy: {
    color: "#f87171",
    bg: "rgba(248,113,113,0.1)",
    border: "rgba(248,113,113,0.3)",
  },
  "Open Source": {
    color: "#4ade80",
    bg: "rgba(74,222,128,0.1)",
    border: "rgba(74,222,128,0.3)",
  },
  Industry: {
    color: "#60a5fa",
    bg: "rgba(96,165,250,0.1)",
    border: "rgba(96,165,250,0.3)",
  },
  Tool: {
    color: "#f472b6",
    bg: "rgba(244,114,182,0.1)",
    border: "rgba(244,114,182,0.3)",
  },
};

const DEFAULT_CAT: CategoryStyle = {
  color: "#4ade80",
  bg: "rgba(74,222,128,0.1)",
  border: "rgba(74,222,128,0.3)",
};

export function catStyle(cat?: string): CategoryStyle {
  if (!cat) return DEFAULT_CAT;
  return CAT[cat] || DEFAULT_CAT;
}
