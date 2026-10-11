import { useCallback, useEffect, useRef, useState, type SetStateAction } from "react";
import { listScientificObjects, type ScientificObjectSummary } from "../../app/lib/scientific-viewer-api";
import { validateManagedObject } from "../../shared/workspace/scientific-object-operations";

type Lifecycle = "ACTIVE" | "ARCHIVED" | "TRASHED";
type Directory = {
  scope: string;
  items: ScientificObjectSummary[];
  nextCursor: string | null;
  state: "loading" | "ready" | "error";
  error: string;
};

export function useScientificObjectDirectory(projectId: string, lifecycle: Lifecycle) {
  const scope = JSON.stringify([projectId, lifecycle]);
  const [directory, setDirectory] = useState<Directory>({ scope, items: [], nextCursor: null, state: "loading", error: "" });
  const pendingRef = useRef(false);
  const cursorRef = useRef<string | undefined>(undefined);
  const cancelRef = useRef<() => void>(() => {});
  const readPage = useCallback((cursor?: string) => {
    cancelRef.current();
    const controller = new AbortController();
    cursorRef.current = cursor;
    pendingRef.current = true;
    setDirectory((previous) => ({
      scope,
      items: previous.scope === scope ? previous.items : [],
      nextCursor: previous.scope === scope ? previous.nextCursor : null,
      state: "loading",
      error: "",
    }));
    const fail = (error: string) => {
      pendingRef.current = false;
      setDirectory((current) => current.scope === scope ? { ...current, state: "error", error } : current);
    };
    const timer = setTimeout(() => {
      controller.abort();
      fail("科研对象目录读取超时，请重试。已打开的数据仍可查看。");
    }, 10_000);
    cancelRef.current = () => { clearTimeout(timer); controller.abort(); };
    void listScientificObjects(projectId, controller.signal, lifecycle, cursor)
      .then((response) => {
        if (controller.signal.aborted) return;
        if (!Array.isArray(response.items) || (response.next_cursor !== null && typeof response.next_cursor !== "string") ||
            new Set(response.items.map((item) => item?.id)).size !== response.items.length) throw new Error("Invalid scientific object directory");
        response.items.forEach((item) => validateManagedObject(item, projectId, item.id, lifecycle));
        pendingRef.current = false;
        setDirectory((current) => ({
          scope,
          items: cursor && current.scope === scope
            ? [...new Map([...current.items, ...response.items].map((item) => [item.id, item])).values()]
            : response.items,
          nextCursor: response.next_cursor,
          state: "ready",
          error: "",
        }));
      })
      .catch(() => { if (!controller.signal.aborted) fail("科研对象目录暂时无法读取。已打开的数据仍可查看，请重新加载目录。"); })
      .finally(() => clearTimeout(timer));
  }, [projectId, lifecycle, scope]);
  useEffect(() => {
    readPage();
    return () => cancelRef.current();
  }, [readPage]);
  const current: Directory = directory.scope === scope ? directory : { scope, items: [], nextCursor: null, state: "loading", error: "" };
  const setItems = useCallback((update: SetStateAction<ScientificObjectSummary[]>) => {
    setDirectory((value) => value.scope === scope ? { ...value, items: typeof update === "function" ? update(value.items) : update } : value);
  }, [scope]);
  return {
    ...current,
    setItems,
    retry: () => { if (!pendingRef.current) readPage(cursorRef.current); },
    loadMore: () => { if (!pendingRef.current && current.state === "ready" && current.nextCursor) readPage(current.nextCursor); },
  };
}
