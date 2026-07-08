import { useState } from "react";

interface BackToTopProps {
  visible: boolean;
}

export function BackToTop({ visible }: BackToTopProps) {
  const [used, setUsed] = useState(false);

  function handleClick() {
    setUsed(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <button
      className={`back-top ${visible ? "visible" : ""} ${used ? "used" : ""}`}
      title="Back to top"
      onClick={handleClick}
    >
      ↑
    </button>
  );
}
