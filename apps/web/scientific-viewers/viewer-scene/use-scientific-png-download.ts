"use client";

import { useEffect, useRef, useState } from "react";

export function useScientificPngDownload(identity: unknown) {
  const identityRef = useRef(identity);
  identityRef.current = identity;
  const tokenRef = useRef<symbol | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    tokenRef.current = null;
    setBusy(false);
    return () => { tokenRef.current = null; };
  }, [identity]);

  const download = async (createImage: () => Promise<Blob>, filename: string, onError: () => void) => {
    if (tokenRef.current) return;
    const token = Symbol();
    tokenRef.current = token;
    setBusy(true);
    const current = () => tokenRef.current === token && identityRef.current === identity;
    try {
      const blob = await createImage();
      if (!current()) return;
      const url = URL.createObjectURL(blob);
      try {
        const link = document.createElement("a");
        link.href = url; link.download = filename; link.click();
      } finally { setTimeout(() => URL.revokeObjectURL(url), 0); }
    } catch { if (current()) onError(); }
    finally { if (current()) { tokenRef.current = null; setBusy(false); } }
  };
  return { busy, download };
}
