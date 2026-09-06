export const CLIENT_EXCEPTION_EVENT_VERSION = "ClientExceptionEvent/1.0" as const;

type ClientExceptionSource = "window.error" | "unhandledrejection";

export type ClientExceptionEvent = Readonly<{
  schemaVersion: typeof CLIENT_EXCEPTION_EVENT_VERSION;
  source: ClientExceptionSource;
  releaseSha: string;
  route: string;
  errorType: string;
  clientEventId: string;
  correlation: Readonly<{
    projectId?: string;
    researchTurnId?: string;
    jobId?: string;
    contextManifestId?: string;
  }>;
}>;

const SAFE_ID = /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$/u;
const RELEASE_SHA = /^[0-9a-f]{7,64}$/iu;
const ERROR_TYPE = /^[A-Za-z_$][A-Za-z0-9_$.-]{0,63}$/u;

export function normalizeClientReleaseSha(value: string | undefined): string {
  const candidate = value?.trim() || "";
  return RELEASE_SHA.test(candidate) ? candidate.toLowerCase() : "LOCAL_WORKTREE";
}

export function boundedProductRoute(pathname: string): string {
  if (/^\/projects\/[^/]+\/research(?:\/|$)/u.test(pathname)) {
    return "/projects/:projectId/research";
  }
  if (/^\/projects\/[^/]+\/data(?:\/|$)/u.test(pathname)) {
    return "/projects/:projectId/data";
  }
  if (/^\/projects\/[^/]+\/history(?:\/|$)/u.test(pathname)) {
    return "/projects/:projectId/history";
  }
  if (/^\/projects\/[^/]+\/reports(?:\/|$)/u.test(pathname)) {
    return "/projects/:projectId/reports";
  }
  if (/^\/projects\/[^/]+(?:\/|$)/u.test(pathname)) {
    return "/projects/:projectId";
  }
  const topLevel = pathname.split("/").filter(Boolean)[0] || "";
  if (
    [
      "account",
      "admin",
      "analysis",
      "console",
      "notifications",
      "settings",
      "tasks",
      "trash",
    ].includes(topLevel)
  ) {
    return `/${topLevel}`;
  }
  return "/other";
}

function safeId(value: string | null | undefined): string | undefined {
  const candidate = value?.trim() || "";
  return SAFE_ID.test(candidate) ? candidate : undefined;
}

function decodedId(value: string | undefined): string | undefined {
  if (!value) return undefined;
  try {
    return safeId(decodeURIComponent(value));
  } catch {
    return undefined;
  }
}

export function clientCorrelation(location: Pick<Location, "pathname" | "search">) {
  const projectMatch = /^\/projects\/([^/]+)/u.exec(location.pathname);
  const params = new URLSearchParams(location.search);
  return {
    projectId: decodedId(projectMatch?.[1]),
    researchTurnId: safeId(
      params.get("turn") ||
        params.get("turnId") ||
        params.get("researchTurnId"),
    ),
    jobId: safeId(params.get("jobId")),
    contextManifestId: safeId(params.get("contextManifestId")),
  };
}

export function clientErrorType(value: unknown): string {
  const candidate =
    value instanceof Error
      ? value.name
      : typeof value === "object" && value !== null
        ? String((value as { constructor?: { name?: string } }).constructor?.name || "")
        : "UnknownError";
  return ERROR_TYPE.test(candidate) ? candidate : "UnknownError";
}

export function buildClientExceptionEvent(input: {
  source: ClientExceptionSource;
  releaseSha: string | undefined;
  location: Pick<Location, "pathname" | "search">;
  error: unknown;
  clientEventId: string;
}): ClientExceptionEvent {
  return {
    schemaVersion: CLIENT_EXCEPTION_EVENT_VERSION,
    source: input.source,
    releaseSha: normalizeClientReleaseSha(input.releaseSha),
    route: boundedProductRoute(input.location.pathname),
    errorType: clientErrorType(input.error),
    clientEventId: safeId(input.clientEventId) || "client-event",
    correlation: clientCorrelation(input.location),
  };
}

export async function sendClientExceptionEvent(
  event: ClientExceptionEvent,
): Promise<void> {
  await fetch("/api/api/observability/client-exceptions", {
    method: "POST",
    credentials: "include",
    keepalive: true,
    headers: {
      "Content-Type": "application/json",
      "X-Request-ID": event.clientEventId,
    },
    body: JSON.stringify(event),
  });
}
