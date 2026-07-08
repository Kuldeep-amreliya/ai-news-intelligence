import type { ToastState } from "../types";

interface ToastProps {
  toast: ToastState;
}

export function Toast({ toast }: ToastProps) {
  return (
    <div className={`toast ${toast.visible ? "show" : ""} ${toast.type}`}>
      {toast.message}
    </div>
  );
}
