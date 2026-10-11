import {
  listWorkspaceTaskFeed,
  type WorkspaceAnalysisJobSummary,
} from "./workspace-api";
import { taskStatusLabel } from "./task-display";

export type ProductTaskRow = WorkspaceAnalysisJobSummary & {
  projectName: string;
};

export type ProductTaskFeed = {
  projectCount: number;
  rows: ProductTaskRow[];
  unavailableProjectCount: number;
  truncated: boolean;
  nextCursor: string | null;
  loadedAt: string;
};

export type ProductTaskSortOrder = "recent" | "oldest";
type ProductTaskFeedOptions = Readonly<{
  forceRefresh?: boolean;
  signal?: AbortSignal;
}>;
export type ProductTaskFeedPageOptions = Readonly<{
  cursor?: string;
  signal?: AbortSignal;
}>;

export function productTaskSearchText(
  task: Pick<
    ProductTaskRow,
    "projectName" | "researchQuestion" | "jobId" | "jobStatus" | "workspaceProjectionStatus" | "sourceDatasets"
  >,
): string {
  return [
    task.projectName,
    task.researchQuestion,
    ...(task.sourceDatasets || []).map((source) => source.name),
    task.jobId,
    task.jobStatus,
    task.workspaceProjectionStatus,
    taskStatusLabel(task.jobStatus),
  ]
    .filter(Boolean)
    .join(" ")
    .toLocaleLowerCase("zh-CN");
}

export function sortProductTaskRows<
  T extends Pick<ProductTaskRow, "createdAt" | "updatedAt">,
>(rows: readonly T[], order: ProductTaskSortOrder = "recent"): T[] {
  return [...rows].sort((left, right) => {
    const leftTime = Date.parse(String(left.updatedAt || left.createdAt || "")) || 0;
    const rightTime = Date.parse(String(right.updatedAt || right.createdAt || "")) || 0;
    return order === "oldest" ? leftTime - rightTime : rightTime - leftTime;
  });
}

const TASK_FEED_WARM_TTL_MS = 15_000;
let taskFeedRequest:
  | { expiresAt: number; promise: Promise<ProductTaskFeed> }
  | undefined;
let taskFeedInFlight:
  | {
      promise: Promise<ProductTaskFeed>;
      controller: AbortController;
      consumers: Set<symbol>;
      hasUnabortableConsumer: boolean;
      settled: boolean;
    }
  | undefined;

export function invalidateProductTaskFeed(): void {
  taskFeedRequest = undefined;
}

function projectTaskFeed(
  result: Awaited<ReturnType<typeof listWorkspaceTaskFeed>>,
): ProductTaskFeed {
  const feed = result.data;
  if (!feed) throw new Error("任务中心没有返回可用数据。");
  return {
    projectCount: feed.projectCount,
    rows: feed.items,
    unavailableProjectCount: 0,
    truncated: feed.truncated,
    nextCursor: feed.nextCursor,
    loadedAt: new Date().toISOString(),
  };
}

export async function getProductTaskFeedPage(
  options: ProductTaskFeedPageOptions = {},
): Promise<ProductTaskFeed> {
  const result = await listWorkspaceTaskFeed({
    limit: 100,
    ...(options.cursor ? { cursor: options.cursor } : {}),
    signal: options.signal,
  });
  return projectTaskFeed(result);
}

function abortError(): DOMException {
  return new DOMException("Task feed request was aborted.", "AbortError");
}

function consumeProductTaskFeed(
  request: NonNullable<typeof taskFeedInFlight>,
  signal?: AbortSignal,
): Promise<ProductTaskFeed> {
  if (!signal) {
    request.hasUnabortableConsumer = true;
    return request.promise;
  }
  if (signal.aborted) return Promise.reject(abortError());

  const consumer = Symbol("product-task-feed-consumer");
  request.consumers.add(consumer);
  return new Promise<ProductTaskFeed>((resolve, reject) => {
    let finished = false;
    const release = () => {
      if (finished) return;
      finished = true;
      signal.removeEventListener("abort", onAbort);
      request.consumers.delete(consumer);
      if (
        !request.settled &&
        !request.hasUnabortableConsumer &&
        request.consumers.size === 0
      ) {
        request.controller.abort();
      }
    };
    const onAbort = () => {
      release();
      reject(abortError());
    };
    signal.addEventListener("abort", onAbort, { once: true });
    request.promise.then(
      (feed) => {
        release();
        resolve(feed);
      },
      (error) => {
        release();
        reject(error);
      },
    );
  });
}

function observeCachedProductTaskFeed(
  promise: Promise<ProductTaskFeed>,
  signal?: AbortSignal,
): Promise<ProductTaskFeed> {
  if (!signal) return promise;
  if (signal.aborted) return Promise.reject(abortError());
  return new Promise<ProductTaskFeed>((resolve, reject) => {
    const onAbort = () => reject(abortError());
    signal.addEventListener("abort", onAbort, { once: true });
    promise.then(resolve, reject).finally(() => {
      signal.removeEventListener("abort", onAbort);
    });
  });
}

export function getProductTaskFeed(
  options: ProductTaskFeedOptions = {},
): Promise<ProductTaskFeed> {
  // A manual refresh may bypass warm data, but it must still join an
  // authoritative request that is already in flight.
  if (taskFeedInFlight?.controller.signal.aborted) {
    if (taskFeedRequest?.promise === taskFeedInFlight.promise) {
      taskFeedRequest = undefined;
    }
    taskFeedInFlight = undefined;
  }
  if (taskFeedInFlight) {
    return consumeProductTaskFeed(taskFeedInFlight, options.signal);
  }
  if (
    !options.forceRefresh &&
    taskFeedRequest &&
    taskFeedRequest.expiresAt > Date.now()
  ) {
    return observeCachedProductTaskFeed(taskFeedRequest.promise, options.signal);
  }

  const controller = new AbortController();
  const request = {
    promise: Promise.resolve({} as ProductTaskFeed),
    controller,
    consumers: new Set<symbol>(),
    hasUnabortableConsumer: false,
    settled: false,
  };
  const promise = listWorkspaceTaskFeed({ limit: 100, signal: controller.signal })
    .then(projectTaskFeed)
    .catch((error) => {
      if (taskFeedRequest?.promise === promise) taskFeedRequest = undefined;
      throw error;
    })
    .finally(() => {
      request.settled = true;
      if (taskFeedInFlight === request) taskFeedInFlight = undefined;
    });

  request.promise = promise;
  taskFeedInFlight = request;
  taskFeedRequest = {
    expiresAt: Date.now() + TASK_FEED_WARM_TTL_MS,
    promise,
  };
  return consumeProductTaskFeed(request, options.signal);
}
