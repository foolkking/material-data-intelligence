export function RouteLoading({
  embedded = false,
  section = "材料研究",
  variant = "document",
}: Readonly<{
  embedded?: boolean;
  section?: string;
  variant?: "document" | "overview" | "data" | "research" | "reports";
}>) {
  if (embedded && variant !== "document") {
    return (
      <section
        className={`route-loading-workbench route-loading-${variant}`}
        aria-busy="true"
        aria-label={`${section}正在加载`}
      >
        <div className="route-loading-workbench-tabs" aria-hidden="true">
          <i />
          <i />
        </div>
        <aside className="route-loading-workbench-context" aria-hidden="true">
          <span className="route-loading-kicker" />
          <span className="route-loading-heading" />
          <span className="route-loading-line" />
          <span className="route-loading-line route-loading-line-medium" />
          <span className="route-loading-line" />
        </aside>
        <div className="route-loading-workbench-main" aria-hidden="true">
          <span className="route-loading-kicker" />
          <span className="route-loading-heading route-loading-heading-wide" />
          <span className="route-loading-canvas" />
          <span className="route-loading-line route-loading-line-medium" />
        </div>
        <p className="sr-only" role="status">
          正在保留当前科学上下文并打开{section}…
        </p>
      </section>
    );
  }
  return (
    <div className="route-loading-frame" aria-busy="true">
      {!embedded ? <header className="route-loading-bar">
        <span className="product-brand">
          <span className="product-brand-mark" aria-hidden="true">M</span>
          材料智能平台
        </span>
        <span className="route-loading-context">{section}</span>
        <span className="route-loading-actions" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
      </header> : null}
      <main className="document-page route-loading-content">
        <p className="product-kicker">正在切换工作区</p>
        <div className="route-loading-line route-loading-line-short" />
        <div className="route-loading-line" />
        <div className="route-loading-rule" />
        <div className="route-loading-blocks" aria-hidden="true">
          <i />
          <i />
          <i />
        </div>
        <p className="route-loading-status" role="status">
          正在保留当前研究上下文…
        </p>
      </main>
    </div>
  );
}
