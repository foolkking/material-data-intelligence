import { listProjects, type ProjectSummary } from "./planner-api";
import {
  listWorkspaceAnalysisJobs,
  type WorkspaceAnalysisJobSummary,
} from "./workspace-api";

export type ProductTaskRow = WorkspaceAnalysisJobSummary & {
  projectName: string;
};

export type ProductTaskFeed = {
  projects: ProjectSummary[];
  rows: ProductTaskRow[];
  unavailableProjectCount: number;
  truncated: boolean;
  loadedAt: string;
};

const TASK_FEED_WARM_TTL_MS = 15_000;
let taskFeedRequest:
  | { expiresAt: number; promise: Promise<ProductTaskFeed> }
  | undefined;

export function invalidateProductTaskFeed(): void {
  taskFeedRequest = undefined;
}

export function getProductTaskFeed(
  options: Readonly<{ forceRefresh?: boolean }> = {},
): Promise<ProductTaskFeed> {
  if (
    !options.forceRefresh &&
    taskFeedRequest &&
    taskFeedRequest.expiresAt > Date.now()
  ) {
    return taskFeedRequest.promise;
  }

  const promise = listProjects()
    .then(async (projects) => {
      const outcomes = await Promise.allSettled(
        projects.map(async (project) => {
          const projectId = project.projectId || project.id;
          const result = await listWorkspaceAnalysisJobs(projectId, {
            limit: 50,
          });
          return {
            rows: (result.data?.items || []).map((task) => ({
              ...task,
              projectName: project.name,
            })),
            truncated: Boolean(result.data?.nextCursor),
          };
        }),
      );
      const rows = outcomes.flatMap((outcome) =>
        outcome.status === "fulfilled" ? outcome.value.rows : [],
      );
      rows.sort((left, right) =>
        String(right.updatedAt || right.createdAt || "").localeCompare(
          String(left.updatedAt || left.createdAt || ""),
        ),
      );
      return {
        projects,
        rows,
        unavailableProjectCount: outcomes.filter(
          (outcome) => outcome.status === "rejected",
        ).length,
        truncated: outcomes.some(
          (outcome) => outcome.status === "fulfilled" && outcome.value.truncated,
        ),
        loadedAt: new Date().toISOString(),
      };
    })
    .catch((error) => {
      taskFeedRequest = undefined;
      throw error;
    });

  taskFeedRequest = {
    expiresAt: Date.now() + TASK_FEED_WARM_TTL_MS,
    promise,
  };
  return promise;
}
