import { useCallback, useRef, useState } from "react";
import type { ToastState, ToastType } from "../types";

const DEFAULT_STATE: ToastState = { message: "", type: "ok", visible: false };

export function useToast() {
  const [toast, setToast] = useState<ToastState>(DEFAULT_STATE);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showToast = useCallback((message: string, type: ToastType = "ok") => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setToast({ message, type, visible: true });
    timerRef.current = setTimeout(() => {
      setToast((prev) => ({ ...prev, visible: false }));
    }, 3500);
  }, []);

  return { toast, showToast };
}
