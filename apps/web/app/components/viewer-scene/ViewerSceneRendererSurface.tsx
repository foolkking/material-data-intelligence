"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { mapViewerSceneForRenderer } from "./viewerSceneRendererMapper";
import type { ViewerRendererEngine, ViewerRendererEngineFactory, ViewerRendererSnapshot, ViewerRendererState } from "./viewerSceneRendererTypes";

export type ViewerSceneRendererSurfaceProps = {
  readonly payload: unknown;
  readonly capabilityOverride?: boolean;
  readonly engineFactory?: ViewerRendererEngineFactory;
};

const defaultEngineFactory: ViewerRendererEngineFactory = async (args) => {
  const module = await import("./viewerSceneRendererEngine");
  return module.createThreeViewerEngine(args);
};

export function ViewerSceneRendererSurface({ payload, capabilityOverride, engineFactory = defaultEngineFactory }: ViewerSceneRendererSurfaceProps) {
  const mapping = useMemo(() => mapViewerSceneForRenderer(payload), [payload]);
  const containerRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<ViewerRendererEngine | null>(null);
  const [state, setState] = useState<ViewerRendererState>(mapping.ok ? "ready" : "validation_failed");
  const [showCell, setShowCell] = useState(true);
  const [showBonds, setShowBonds] = useState(true);
  const [snapshot, setSnapshot] = useState<ViewerRendererSnapshot | null>(null);

  useEffect(() => {
    setState(mapping.ok ? "ready" : "validation_failed");
    setSnapshot(null);
    if (!mapping.ok) return;
    const supported = capabilityOverride ?? supportsWebGL();
    if (!supported) {
      setState("unsupported");
      return;
    }
    const container = containerRef.current;
    if (!container) return;
    let cancelled = false;
    setState("initializing_renderer");
    void engineFactory({
      container,
      scene: mapping.scene,
      pixelRatioCap: 2,
      onContextLost: () => {
        setState("context_lost");
        queueMicrotask(() => {
          engineRef.current?.dispose();
          engineRef.current = null;
        });
      },
    }).then((engine) => {
      if (cancelled) {
        engine.dispose();
        return;
      }
      engineRef.current = engine;
      engine.setCellVisible(showCell);
      engine.setBondsVisible(showBonds);
      setSnapshot(engine.snapshot());
      setState("rendered");
    }).catch(() => {
      if (!cancelled) setState("renderer_failed");
    });
    return () => {
      cancelled = true;
      const engine = engineRef.current;
      engineRef.current = null;
      if (engine) {
        try { engine.dispose(); } catch { /* disposal is best-effort after the surface is detached */ }
      }
    };
  }, [capabilityOverride, engineFactory, mapping]);

  const applyVisibility = (kind: "cell" | "bonds", visible: boolean) => {
    if (kind === "cell") {
      setShowCell(visible);
      engineRef.current?.setCellVisible(visible);
    } else {
      setShowBonds(visible);
      engineRef.current?.setBondsVisible(visible);
    }
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  };
  const reset = () => {
    engineRef.current?.resetCamera();
    if (engineRef.current) setSnapshot(engineRef.current.snapshot());
  };

  return (
    <section className="viewer-renderer-surface" aria-label="Experimental validated scene renderer" data-testid="viewer-scene-renderer-surface">
      <div className="viewer-renderer-toolbar">
        <div>
          <strong>Experimental validated scene renderer</strong>
          <span data-testid="viewer-scene-renderer-state">{state}</span>
        </div>
        <div className="viewer-renderer-controls" aria-label="Viewer controls">
          <button type="button" className="compact secondary" data-testid="viewer-scene-renderer-reset" onClick={reset} disabled={state !== "rendered"}>Reset camera</button>
          <button type="button" className={`compact ${showCell ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-cell" aria-pressed={showCell} onClick={() => applyVisibility("cell", !showCell)}>Unit cell</button>
          <button type="button" className={`compact ${showBonds ? "active" : "secondary"}`} data-testid="viewer-scene-renderer-toggle-bonds" aria-pressed={showBonds} onClick={() => applyVisibility("bonds", !showBonds)}>Bonds</button>
        </div>
      </div>

      {!mapping.ok ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-invalid">
          <strong>Scene validation failed</strong>
          <p>The renderer was not initialized. Review the inert JSON preview for contract errors.</p>
          <code>{mapping.validation.errors.join(", ")}</code>
        </div>
      ) : null}
      {mapping.ok && state === "unsupported" ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-unavailable">
          <strong>Interactive renderer unavailable</strong>
          <p>This browser did not provide a usable WebGL context. The Scene JSON and Manifest views remain available.</p>
        </div>
      ) : null}
      {mapping.ok && (state === "renderer_failed" || state === "context_lost") ? (
        <div className="viewer-renderer-fallback" data-testid="viewer-scene-renderer-fallback">
          <strong>{state === "context_lost" ? "Graphics context lost" : "Renderer initialization failed"}</strong>
          <p>The artifact remains available as validated JSON. No artifact content was executed.</p>
        </div>
      ) : null}
      {mapping.ok && state === "initializing_renderer" ? <p className="viewer-renderer-loading">Initializing local renderer...</p> : null}
      {mapping.ok && !["unsupported", "renderer_failed", "context_lost"].includes(state) ? <div ref={containerRef} className="viewer-renderer-canvas-host" data-testid="viewer-scene-renderer-valid" /> : null}
      {mapping.ok ? (
        <dl className="mini-grid viewer-renderer-audit" data-testid="viewer-scene-renderer-audit">
          <div><dt>sites</dt><dd>{mapping.scene.atoms.length}</dd></div>
          <div><dt>species</dt><dd>{new Set(mapping.scene.atoms.map((atom) => atom.species)).size}</dd></div>
          <div><dt>bonds</dt><dd>{snapshot?.bondCount ?? mapping.scene.bonds.length}</dd></div>
          <div><dt>cell edges</dt><dd>{snapshot?.latticeEdgeCount ?? 12}</dd></div>
          <div><dt>graphics</dt><dd>{snapshot?.graphicsContext ?? "pending"}</dd></div>
          <div><dt>renderer</dt><dd>{snapshot?.rendererVersion ? `Three r${snapshot.rendererVersion}` : "pending"}</dd></div>
        </dl>
      ) : null}
    </section>
  );
}

function supportsWebGL() {
  if (typeof window === "undefined" || typeof document === "undefined") return false;
  if (/jsdom/i.test(window.navigator.userAgent)) return false;
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}
