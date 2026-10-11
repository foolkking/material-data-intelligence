"use client";

import { Component, useEffect, useState, type ComponentProps, type ComponentType, type ReactNode } from "react";

type ViewerFailure = "load" | "timeout" | "render";

function ViewerFailureState({ kind, retry }: { kind: ViewerFailure; retry: () => void }) {
  return <div className="product-state scientific-plot-failure" role="alert">
    <h5>{kind === "timeout" ? "查看器加载超时" : kind === "render" ? "查看器暂时无法显示" : "查看器未能加载"}</h5>
    <p>{kind === "timeout" ? "加载已等待超过 10 秒。" : kind === "render" ? "这项内容未能显示。" : "查看器组件暂时无法读取。"}其他已读取的内容仍可查看。</p>
    <button type="button" className="product-secondary-action" onClick={retry}>重试查看器</button>
  </div>;
}

class ViewerRenderBoundary extends Component<{ children: ReactNode; retry: () => void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    return this.state.failed ? <ViewerFailureState kind="render" retry={this.props.retry} /> : this.props.children;
  }
}

/** Fixed, application-owned imports only. No module is fetched during SSR.
 * Cache code, never scientific props or payloads; each mounted viewer owns its
 * deadline, failure state and retry while concurrent loads share the import. */
export function createDeferredScientificViewer<T extends ComponentType<any>>(
  load: () => Promise<{ default: T }>,
  options: { label?: string; sourceKey?: (props: NoInfer<ComponentProps<T>>) => string } = {},
): ComponentType<ComponentProps<T>> {
  type P = ComponentProps<T>;
  let loaded: ComponentType<P> | null = null;
  let pending: Promise<ComponentType<P>> | null = null;

  const requestComponent = () => {
    if (loaded) return Promise.resolve(loaded);
    if (pending) return pending;
    const request = Promise.resolve().then(load).then((module) => {
      const component = module.default as ComponentType<P>;
      if (pending === request) loaded = component;
      return component;
    }).finally(() => { if (pending === request) pending = null; });
    pending = request;
    return request;
  };

  function DeferredInstance({ viewerProps }: { viewerProps: P }) {
    const [attempt, setAttempt] = useState(0);
    const [state, setState] = useState<{ attempt: number; component?: ComponentType<P>; failure?: ViewerFailure } | null>(null);
    useEffect(() => {
      let active = true;
      const request = requestComponent();
      const timer = setTimeout(() => {
        if (!active) return;
        active = false;
        if (pending === request) pending = null;
        setState({ attempt, failure: "timeout" });
      }, 10_000);
      void request.then((component) => {
        if (active) setState({ attempt, component });
      }, () => {
        if (active) setState({ attempt, failure: "load" });
      }).finally(() => clearTimeout(timer));
      return () => { active = false; clearTimeout(timer); };
    }, [attempt]);

    const current = state?.attempt === attempt ? state : null;
    const retry = () => setAttempt((value) => value + 1);
    if (current?.failure) return <ViewerFailureState kind={current.failure} retry={retry} />;
    const Viewer = current?.component;
    if (!Viewer) return <div className="scientific-viewer-deferred-loading" role="status" aria-live="polite">
      <span aria-hidden="true" /><strong>{options.label || "正在打开科学查看器…"}</strong>
    </div>;
    return <ViewerRenderBoundary key={attempt} retry={retry}><Viewer {...viewerProps} /></ViewerRenderBoundary>;
  }

  return function DeferredScientificViewer(props: P) {
    return <DeferredInstance key={options.sourceKey?.(props) || "viewer"} viewerProps={props} />;
  };
}
