import type { SessionMemoryController } from "./use-session-memory";

export function SessionMemoryNotice({ context }: { context: SessionMemoryController }) {
  if (!context.error && !context.reading && !context.updating) return null;
  return <div className="research-memory-error research-session-memory-notice" role="status">
    {context.error ? <p>{context.error}</p> : null}
    {context.error ? <button type="button" className="product-secondary-action" disabled={context.reading || context.updating} onClick={() => void context.refresh()}>
      {context.reading ? "正在读取上下文…" : "重新读取上下文"}
    </button> : context.reading ? <p>正在读取上下文…</p> : null}
    {context.updating ? <p>正在更新上下文…</p> : null}
  </div>;
}
