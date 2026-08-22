import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = path.resolve(import.meta.dirname, "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const ORIGIN = process.env.MDI_PHASE4_WEB_ORIGIN || "http://127.0.0.1:3000";
const OUT = path.join(ROOT, "docs/agent2/evidence/phase4");

const history = {
  schemaVersion: "ProjectHistoryView/1.0",
  project: { id: "project_1", name: "电池材料研究", role: "owner" },
  summary: { datasetCount: 1, analysisCount: 0, completedAnalysisCount: 0, artifactCount: 0, workspaceCount: 0, reportCount: 0 },
  datasets: [{
    datasetId: "dataset_1", name: "晶体结构", status: "profile_ready", analysisCount: 0, process: [],
    resultSummary: { artifactCount: 0, workspaceCount: 0, interpretationCount: 0, reportCount: 0, recipeCount: 0, artifactTypes: [] },
    import: { fileCount: 1, files: [], resources: [], parseOutcome: "succeeded" },
    profile: { datasetType: "structure", readyCapabilities: ["structure.xrd"], semanticRoles: {} },
  }],
  analyses: [], activity: [],
};

const progress = {
  contract_version: "1.0", turn_id: "turn-1", status: "RUNNING", plan_title: "实验与理论 XRD 比较",
  steps: [
    { step_id: "step_1", display_name: "生成理论 XRD 图谱", status: "SUCCEEDED", completed_label: "生成理论 XRD 图谱已完成", output_available: true },
    { step_id: "step_2", display_name: "比较实验与理论 XRD 峰", status: "RUNNING", running_label: "正在比较实验与理论 XRD 峰", output_available: false },
  ],
  active_step_ids: ["step_2"], completed_step_count: 1, total_step_count: 2,
  incremental_outputs: [{ output_key: "step_1.output_1", step_id: "step_1", display_label: "理论 XRD 图谱已生成", artifact_id: "artifact-internal", preview_available: true, available_at: "2026-08-23T00:00:00Z" }],
  warnings: [], execution_outcome: null, result_projection_pending: false,
};

function bodyFor(url) {
  const pathname = new URL(url).pathname;
  if (pathname === "/api/auth/me") return { id: "user_1", displayName: "验收研究员", email: "researcher@local.invalid", roles: ["researcher"] };
  if (pathname === "/api/projects/project_1/history") return history;
  if (pathname === "/api/projects/project_1/research-sessions") return [];
  if (pathname === "/api/planner/providers/status") return { status: "ready", provider: "deepseek", model: "deepseek-chat", allowedModels: ["deepseek-chat"] };
  if (pathname === "/api/planner/providers") return { providers: [{ provider: "deepseek", label: "DeepSeek", models: ["deepseek-chat"], allowedModels: ["deepseek-chat"], defaultModel: "deepseek-chat", secretConfigured: true, execution: "live", developerOnly: false }] };
  if (pathname === "/api/api/research/turns/turn-1/progress") return progress;
  return {};
}

async function inspect(page, name, viewport) {
  await page.setViewportSize(viewport);
  await page.goto(`${ORIGIN}/projects/project_1/research?turn=turn-1`, { waitUntil: "domcontentloaded" });
  const activity = page.locator(".research-execution-activity");
  try {
    await activity.waitFor({ state: "visible", timeout: 15000 });
  } catch (error) {
    const body = await page.locator("body").innerText().catch(() => "<body unavailable>");
    throw new Error(`${name}: progress did not render at ${page.url()}\n${body.slice(0, 3000)}\nConsole: ${consoleErrors.join(" | ")}`, { cause: error });
  }
  const metrics = await page.evaluate(() => {
    const activityNode = document.querySelector(".research-execution-activity");
    const stream = document.querySelector(".conversation-stream");
    const cancel = document.querySelector(".research-execution-cancel");
    const timeline = document.querySelector("#research-timeline-panel");
    const workbench = document.querySelector("#research-workbench-panel");
    const cancelRect = cancel?.getBoundingClientRect();
    return {
      activityInsideConversation: Boolean(activityNode && stream?.contains(activityNode)),
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth,
      cancelWidth: cancelRect?.width || 0,
      cancelHeight: cancelRect?.height || 0,
      timelineVisible: timeline ? getComputedStyle(timeline).display !== "none" : false,
      workbenchVisible: workbench ? getComputedStyle(workbench).display !== "none" : false,
      exposedRuntimeIdentity: /job_|tool_call|artifact-internal|worker|queue/i.test(document.body.innerText),
    };
  });
  if (!metrics.activityInsideConversation) throw new Error(`${name}: progress is not owned by the conversation stream`);
  if (metrics.horizontalOverflow) throw new Error(`${name}: horizontal overflow detected`);
  if (metrics.cancelWidth < 44 || metrics.cancelHeight < 44) throw new Error(`${name}: cancel target is smaller than 44px`);
  if (metrics.exposedRuntimeIdentity) throw new Error(`${name}: runtime identity leaked into product copy`);
  if (viewport.width === 390 && (!metrics.timelineVisible || metrics.workbenchVisible)) throw new Error(`${name}: mobile default is not a single conversation panel`);
  await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: true });
  return { name, viewport, ...metrics };
}

await mkdir(OUT, { recursive: true });
const { chromium } = await import(pathToFileURL(PLAYWRIGHT).href);
const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ["--no-sandbox", "--disable-background-networking"] });
const page = await browser.newPage();
const consoleErrors = [];
page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
page.on("pageerror", (error) => consoleErrors.push(error.stack || error.message));
await page.route("**/api/**", async (route) => {
  await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(bodyFor(route.request().url())) });
});
await page.emulateMedia({ reducedMotion: "reduce" });
try {
  const results = [
    await inspect(page, "desktop-1440x900", { width: 1440, height: 900 }),
    await inspect(page, "mobile-390x844", { width: 390, height: 844 }),
  ];
  const evidence = { contract: "agent2-phase4-browser-evidence/1.0", results, consoleErrors };
  if (consoleErrors.length) throw new Error(`browser console errors: ${consoleErrors.join(" | ")}`);
  await writeFile(path.join(OUT, "browser-evidence.json"), `${JSON.stringify(evidence, null, 2)}\n`, "utf8");
  console.log("AGENT2_PHASE4_BROWSER_EVIDENCE_PASS");
} finally {
  await browser.close();
}
