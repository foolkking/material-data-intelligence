"use client";

import { useEffect, useState, type ReactNode } from "react";

export const MAX_ACTIVE_HEAVY_VIEWERS = 1;

class HeavyViewerLeaseManager {
  private activeOwner: string | null = null;

  acquire(owner: string): (() => void) | null {
    if (!owner || (this.activeOwner !== null && this.activeOwner !== owner)) return null;
    if (this.activeOwner === owner) return () => this.release(owner);
    this.activeOwner = owner;
    return () => this.release(owner);
  }

  release(owner: string): void {
    if (this.activeOwner === owner) this.activeOwner = null;
  }

  snapshot(): Readonly<{ activeOwner: string | null; activeCount: number; cap: number }> {
    return Object.freeze({ activeOwner: this.activeOwner, activeCount: this.activeOwner ? 1 : 0, cap: MAX_ACTIVE_HEAVY_VIEWERS });
  }
}

export const workspaceHeavyViewerLeases = new HeavyViewerLeaseManager();

export function WorkspaceHeavyViewerLease({ owner, children }: Readonly<{ owner: string; children: ReactNode }>) {
  const [heldOwner, setHeldOwner] = useState<string | null>(null);
  useEffect(() => {
    const release = workspaceHeavyViewerLeases.acquire(owner);
    if (!release) {
      setHeldOwner(null);
      return;
    }
    setHeldOwner(owner);
    return () => {
      release();
    };
  }, [owner]);
  if (heldOwner !== owner) return <div className="workspace-gallery-state" role="status"><strong>Heavy Viewer busy</strong><span>HEAVY_VIEWER_BUSY: another active scientific viewer is being released.</span></div>;
  return <>{children}</>;
}
