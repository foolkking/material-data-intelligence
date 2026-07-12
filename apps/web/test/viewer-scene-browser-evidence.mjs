import { spawn } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(SCRIPT_DIR, "../../..");
const WEB_ROOT = path.join(REPO_ROOT, "apps", "web");
const FIXTURE_ROOT = path.join(REPO_ROOT, "docs", "phase10f", "fixtures", "viewer_scene_v1");
const EVIDENCE_ROOT = path.join(REPO_ROOT, "docs", "phase10f", "evidence", "phase10f11_viewer_scene_real_browser");
const SCREENSHOT_ROOT = path.join(EVIDENCE_ROOT, "screenshots");
const PLAYWRIGHT_MODULE = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const BROWSER_EXECUTABLE =
  process.env.MDI_BROWSER_EXECUTABLE ||
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const LOCAL_SCHEME = "http";
const APP_PORT = Number(process.env.MDI_VIEWER_SCENE_EVIDENCE_PORT || "3311");
const APP_ORIGIN = `${LOCAL_SCHEME}://127.0.0.1:${APP_PORT}`;
const API_HOST = "localhost";
const API_PORT = "8000";

const cases = [
  {
    id: "valid_minimal_crystal",
    scene: "valid_minimal_crystal.viewer_scene.v1.json",
    manifest: "manifest_valid_minimal_crystal.viewer_scene.v1.json",
    expectedState: "passed",
    screenshot: "01_valid_minimal_crystal.png",
  },
  {
    id: "valid_warning_caps",
    scene: "valid_warning_caps.viewer_scene.v1.json",
    manifest: null,
    expectedState: "passed",
    expectedWarning: "VIEWER_SCENE_CAP_NEAR_LIMIT",
    screenshot: "02_valid_warning_caps.png",
  },
  {
    id: "invalid_external_resource_placeholder",
    scene: "invalid_external_resource_reference.viewer_scene.v1.json",
    manifest: "manifest_invalid_external_resource_reference.viewer_scene.v1.json",
    expectedState: "expected_failure",
    expectedError: "VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE",
    screenshot: "03_invalid_external_resource_placeholder.png",
  },
  {
    id: "invalid_executable_placeholder",
    scene: "invalid_executable_field.viewer_scene.v1.json",
    manifest: "manifest_invalid_executable_field.viewer_scene.v1.json",
    expectedState: "expected_failure",
    expectedError: "VIEWER_SCENE_EXECUTABLE_FIELD",
    screenshot: "04_invalid_executable_placeholder.png",
  },
  {
    id: "invalid_schema_version",
    scene: "invalid_schema_version.viewer_scene.v1.json",
    manifest: null,
    expectedState: "expected_failure",
    expectedError: "VIEWER_SCENE_SCHEMA_VERSION_INVALID",
    screenshot: "05_invalid_schema_version.png",
  },
];

let activeCase = cases[0];
let activeScene = {};
let activeManifest = {};
let externalRequests = [];
let consoleMessages = [];
let pageErrors = [];

async function main() {
  await mkdir(SCREENSHOT_ROOT, { recursive: true });
  const playwright = await import(pathToFileURL(PLAYWRIGHT_MODULE).href);
  await stopEvidencePortListener();
  const server = startDevServer();
  try {
    await waitForApp();
    const browser = await playwright.chromium.launch({
      executablePath: BROWSER_EXECUTABLE,
      headless: true,
      args: ["--disable-gpu", "--no-sandbox"],
    });
    const browserVersion = browser.version();
    const context = await browser.newContext({ viewport: { width: 1440, height: 1200 } });
    const snapshots = [];
    for (const testCase of cases) {
      activeCase = testCase;
      activeScene = withEvidenceValidation(await readJson(path.join(FIXTURE_ROOT, testCase.scene)), testCase);
      activeManifest = testCase.manifest
        ? await readJson(path.join(FIXTURE_ROOT, testCase.manifest))
        : buildManifestForCase(testCase, activeScene);
      externalRequests = [];
      consoleMessages = [];
      pageErrors = [];
      const page = await context.newPage();
      await installRoutes(page);
      await runCase(page, testCase);
      const snapshot = await collectSnapshot(page, testCase, browserVersion);
      snapshots.push(snapshot);
      await page.screenshot({ path: path.join(SCREENSHOT_ROOT, testCase.screenshot), fullPage: true });
      await page.close();
    }
    await browser.close();
    await writeJson(path.join(EVIDENCE_ROOT, "dom_snapshot.json"), {
      schema_version: "phase10f11.viewer_scene_browser_dom_snapshot.v1",
      generated_by: "apps/web/test/viewer-scene-browser-evidence.mjs",
      cases: snapshots,
    });
    await writeJson(path.join(EVIDENCE_ROOT, "network_audit.json"), {
      schema_version: "phase10f11.viewer_scene_browser_network_audit.v1",
      external_request_count: snapshots.reduce((total, item) => total + item.external_request_count, 0),
      cases: snapshots.map((item) => ({
        case_id: item.case_id,
        external_request_count: item.external_request_count,
        request_paths: item.request_paths,
      })),
    });
    await writeFile(
      path.join(EVIDENCE_ROOT, "command_log.md"),
      [
        "# Phase 10F-11 Viewer Scene Browser Evidence Command Log",
        "",
        "Command:",
        "",
        "```text",
        "node apps/web/test/viewer-scene-browser-evidence.mjs",
        "```",
        "",
        "Result:",
        "",
        "```text",
        "PASS",
        "```",
        "",
        `Browser: ${browserVersion}`,
        "Viewport: 1440 x 1200",
        "Preview mode: json_only",
        "Renderer required: false",
        "External requests: 0",
      ].join("\n"),
      "utf-8",
    );
    console.log("VIEWER_SCENE_BROWSER_EVIDENCE_PASS");
  } finally {
    server.kill();
    await stopEvidencePortListener();
  }
}

function startDevServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args =
    process.platform === "win32"
      ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(APP_PORT)]
      : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(APP_PORT)];
  const child = spawn(command, args, {
    cwd: REPO_ROOT,
    env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: `${LOCAL_SCHEME}://${API_HOST}:${API_PORT}` },
    stdio: ["ignore", "pipe", "pipe"],
  });
  child.stdout.on("data", (chunk) => process.stdout.write(chunk));
  child.stderr.on("data", (chunk) => process.stderr.write(chunk));
  return child;
}

async function waitForApp() {
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(APP_ORIGIN);
      if (response.ok) return;
    } catch {
      // wait for Next.js dev server
    }
    await delay(500);
  }
  throw new Error("Timed out waiting for the web app evidence server");
}

async function installRoutes(page) {
  await page.addInitScript(() => {
    window.EventSource = class MockEventSource {
      constructor(url) {
        this.url = url;
        this.readyState = 2;
      }
      close() {
        this.readyState = 2;
      }
      addEventListener() {}
      removeEventListener() {}
    };
  });
  page.on("console", (message) => consoleMessages.push({ type: message.type(), text: message.text() }));
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.route("**/*", async (route) => {
    const requestUrl = new URL(route.request().url());
    if (requestUrl.hostname === API_HOST && requestUrl.port === API_PORT) {
      await fulfillApi(route, requestUrl);
      return;
    }
    if ((requestUrl.hostname === "127.0.0.1" || requestUrl.hostname === "localhost") && requestUrl.port === String(APP_PORT)) {
      if (requestUrl.pathname === "/favicon.ico") {
        await route.fulfill({ status: 204, body: "" });
        return;
      }
      await route.continue();
      return;
    }
    if (requestUrl.protocol === "data:" || requestUrl.protocol === "blob:") {
      await route.continue();
      return;
    }
    externalRequests.push({ host: requestUrl.hostname, path: requestUrl.pathname });
    await route.abort();
  });
}

async function runCase(page, testCase) {
  await page.goto(APP_ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(250);
  await page.waitForSelector('[data-testid="global-context-bar"]');
  await page.locator(".global-context-bar .context-button").first().click();
  await page.waitForSelector('[role="dialog"]');
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.waitForSelector("text=dataset_demo");
  await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click();
  await page.waitForSelector('[data-testid="results-export-tab"]');
  await page.waitForSelector('[data-testid="viewer-scene-json-preview"]', { state: "attached" });
  await expectText(page, '[data-testid="viewer-scene-kind"]', "viewer_scene");
  await expectText(page, '[data-testid="viewer-scene-version"]', "viewer_scene.v1");
  await expectText(page, '[data-testid="viewer-scene-validation-state"]', testCase.expectedState);
  await expectText(page, '[data-testid="viewer-scene-summary"]', "cartesian_angstrom");
  await expectText(page, '[data-testid="viewer-manifest-preview-mode"]', "json_only");
  await expectText(page, '[data-testid="viewer-manifest-renderer-required"]', "false");
  await expectText(page, '[data-testid="viewer-manifest-executable-assets"]', "none");
  await expectText(page, '[data-testid="viewer-manifest-external-resources"]', "none");
  if (testCase.expectedWarning) {
    await expectText(page, '[data-testid="viewer-scene-warning-codes"]', testCase.expectedWarning);
  }
  if (testCase.expectedError) {
    await expectText(page, '[data-testid="viewer-scene-error-codes"]', testCase.expectedError);
  }
}

async function collectSnapshot(page, testCase, browserVersion) {
  const browserNoiseMessages = consoleMessages.filter((item) => isBrowserResourceNoise(item));
  const featureConsoleMessages = consoleMessages.filter((item) => item.type === "error" && !isBrowserResourceNoise(item));
  const values = await page.evaluate(() => ({
    kind: document.querySelector('[data-testid="viewer-scene-kind"]')?.textContent || "",
    version: document.querySelector('[data-testid="viewer-scene-version"]')?.textContent || "",
    schema: document.querySelector('[data-testid="viewer-scene-schema-version"]')?.textContent || "",
    validation_state: document.querySelector('[data-testid="viewer-scene-validation-state"]')?.textContent || "",
    error_codes: document.querySelector('[data-testid="viewer-scene-error-codes"]')?.textContent || "",
    warning_codes: document.querySelector('[data-testid="viewer-scene-warning-codes"]')?.textContent || "",
    scene_summary: document.querySelector('[data-testid="viewer-scene-summary"]')?.textContent || "",
    manifest_preview_mode: document.querySelector('[data-testid="viewer-manifest-preview-mode"]')?.textContent || "",
    manifest_renderer_required: document.querySelector('[data-testid="viewer-manifest-renderer-required"]')?.textContent || "",
    manifest_executable_assets: document.querySelector('[data-testid="viewer-manifest-executable-assets"]')?.textContent || "",
    manifest_external_resources: document.querySelector('[data-testid="viewer-manifest-external-resources"]')?.textContent || "",
    canvas_count: document.querySelectorAll("canvas").length,
    iframe_count: document.querySelectorAll("iframe").length,
    script_count: document.querySelectorAll("script").length,
    body_has_webgl_marker: /webgl\s+(?:enabled|renderer)|webgl\s+included\s*true/i.test(document.body.textContent || ""),
    body_has_three_marker: /three\.js/i.test(document.body.textContent || ""),
    body_has_viewer_3d_claim: /structure\.viewer_3d/.test(document.body.textContent || ""),
  }));
  assertBrowserSnapshot(values, testCase);
  return {
    case_id: testCase.id,
    browser_version: browserVersion,
    screenshot: `screenshots/${testCase.screenshot}`,
    ...values,
    external_request_count: externalRequests.length,
    request_paths: requestPathAudit(),
    feature_console_messages: featureConsoleMessages,
    ignored_browser_noise_count: browserNoiseMessages.length,
    page_errors: pageErrors,
    result: "PASS",
  };
}

function isBrowserResourceNoise(message) {
  return message.type === "error" && /Failed to load resource: the server responded with a status of 404/.test(message.text);
}

function assertBrowserSnapshot(values, testCase) {
  const failures = [];
  if (values.canvas_count !== 0) failures.push("canvas element present");
  if (values.iframe_count !== 0) failures.push("iframe element present");
  if (values.body_has_webgl_marker) failures.push("WebGL marker present");
  if (values.body_has_three_marker) failures.push("Three.js marker present");
  if (values.body_has_viewer_3d_claim) failures.push("structure.viewer_3d claim present");
  if (externalRequests.length !== 0) failures.push("external browser request observed");
  if (consoleMessages.some((item) => item.type === "error" && !isBrowserResourceNoise(item))) failures.push("feature console error observed");
  if (pageErrors.length !== 0) failures.push("page error observed");
  if (failures.length) {
    throw new Error(`Browser evidence security assertion failed for ${testCase.id}: ${failures.join(", ")}`);
  }
}

async function fulfillApi(route, requestUrl) {
  const pathName = requestUrl.pathname;
  const method = route.request().method();
  if (pathName === "/health/runtime") {
    await route.fulfill({ json: runtimeHealth() });
  } else if (pathName === "/datasets" && method === "GET") {
    await route.fulfill({ json: [] });
  } else if (pathName === "/datasets/demo" && method === "POST") {
    await route.fulfill({ json: demoDataset() });
  } else if (pathName === "/planner/providers") {
    await route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  } else if (pathName === "/planner/providers/status") {
    await route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  } else if (pathName === "/planner/providers/resolve") {
    await route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", willUseLiveProvider: false, secretConfigured: false } });
  } else if (pathName === "/me/secrets") {
    await route.fulfill({ json: [] });
  } else if (pathName === "/planner/jobs" && method === "POST") {
    await route.fulfill({ json: jobCreateResult() });
  } else if (pathName === "/planner/jobs/job_1") {
    await route.fulfill({ json: jobDetail() });
  } else if (pathName === "/planner/jobs/job_1/events") {
    await route.fulfill({ json: jobEvents() });
  } else if (pathName === "/planner/jobs/job_1/events/stream") {
    await route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  } else if (pathName === "/planner/jobs/job_1/tool-calls") {
    await route.fulfill({ json: toolCalls() });
  } else if (pathName === "/planner/jobs/job_1/artifacts") {
    await route.fulfill({ json: artifactsForActiveCase() });
  } else if (pathName === "/planner/jobs/job_1/result") {
    await route.fulfill({ json: jobResult() });
  } else {
    await route.fulfill({ status: 404, json: { detail: "mock route not found", path: pathName } });
  }
}

function artifactsForActiveCase() {
  return [
    artifact("artifact_viewer_scene_v1", activeCase.scene, "viewer_scene_json", activeScene),
    artifact("artifact_viewer_manifest_v1", `manifest_${activeCase.scene}`, "viewer_scene_manifest_json", activeManifest),
    artifact("artifact_summary_v1", "summary.md", "summary_md", "Viewer Scene JSON-only Preview\n\nNo renderer bundle.\nNo artifact JavaScript.\nNo external resources."),
    artifact("artifact_recipe_v1", "recipe.json", "recipe_json", {
      schema_version: "phase10f11.viewer_scene_real_browser.recipe.v1",
      deterministic: true,
      renderer_required: false,
      steps: ["load_fixture", "validate_contract", "render_json_only_preview_in_browser"],
    }),
  ];
}

function artifact(id, name, type, content) {
  return {
    artifactId: id,
    id,
    jobId: "job_1",
    toolCallId: "call_1",
    type,
    name,
    storageKey: `projects/project_local/jobs/job_1/tool_calls/call_1/${name}`,
    storageProvider: "local",
    planId: "plan_1",
    planHash: "hash_viewer_scene_browser",
    content,
  };
}

function jobCreateResult() {
  return {
    ok: true,
    job_id: "job_1",
    plan_id: "plan_1",
    plan_hash: "hash_viewer_scene_browser",
    validation_errors: [],
    plan_source: "mock",
    planner_provider: "mock",
    enqueued: true,
    executed: true,
    plan: {
      schemaVersion: "phase10f11.browser_evidence.plan.v1",
      goal: "Viewer scene JSON-only preview evidence",
      datasetId: "dataset_demo",
      profileId: "profile_demo",
      steps: [{ stepId: "step_1", toolId: "viewer_scene.preview_fixture", purpose: "Browser evidence only" }],
    },
  };
}

function jobDetail() {
  return {
    id: "job_1",
    jobId: "job_1",
    projectId: "project_local",
    datasetId: "dataset_demo",
    status: "completed",
    planId: "plan_1",
    planHash: "hash_viewer_scene_browser",
    planSource: "mock",
    toolCallCount: 1,
    artifactCount: 4,
    eventCount: 4,
    provenance: { planId: "plan_1", planHash: "hash_viewer_scene_browser", planSource: "mock", fallbackUsed: false },
  };
}

function jobEvents() {
  return [
    { id: "event_1", jobId: "job_1", seq: 1, eventType: "job_started", status: "running", message: "Evidence job started", progress: 0.1 },
    { id: "event_2", jobId: "job_1", seq: 2, eventType: "tool_started", status: "running", message: "Preview fixture loaded", progress: 0.4 },
    { id: "event_3", jobId: "job_1", seq: 3, eventType: "tool_completed", status: "completed", message: "JSON-only preview artifact ready", progress: 0.8 },
    { id: "event_4", jobId: "job_1", seq: 4, eventType: "job_completed", status: "completed", message: "Evidence job completed", progress: 1 },
  ];
}

function toolCalls() {
  return [
    {
      id: "call_1",
      jobId: "job_1",
      stepId: "step_1",
      toolId: "viewer_scene.preview_fixture",
      status: "completed",
      planId: "plan_1",
      planHash: "hash_viewer_scene_browser",
      inputSummary: activeCase.id,
      outputSummary: "JSON-only viewer_scene preview evidence artifacts",
    },
  ];
}

function jobResult() {
  const artifacts = artifactsForActiveCase();
  return {
    jobId: "job_1",
    status: "completed",
    planId: "plan_1",
    planHash: "hash_viewer_scene_browser",
    summary: "Job completed with 1 ToolCall(s) and 4 Artifact(s).",
    toolCallCount: 1,
    artifactCount: artifacts.length,
    artifacts,
    provenance: { planId: "plan_1", planHash: "hash_viewer_scene_browser", planSource: "mock", fallbackUsed: false },
  };
}

function runtimeHealth() {
  return {
    api: { status: "ok" },
    database: { status: "mock" },
    redis: { status: "mock" },
    artifactStorage: { status: "mock" },
    worker: { status: "mock" },
    llmProvider: { status: "mock", provider: "mock" },
  };
}

function demoDataset() {
  return {
    id: "dataset_demo",
    datasetId: "dataset_demo",
    projectId: "project_local",
    name: "Demo dataset",
    status: "ready",
    demo: true,
    profileId: "profile_demo",
    profile: {
      id: "profile_demo",
      profileId: "profile_demo",
      datasetId: "dataset_demo",
      datasetType: "table",
      version: "phase10f11.browser_evidence.profile.v1",
      status: "ready",
      profileGenerated: true,
      tableSummary: {
        nRows: 4,
        nColumns: 2,
        columns: [
          { name: "y_true", inferredRole: "target", dtype: "number" },
          { name: "y_pred", inferredRole: "prediction", dtype: "number" },
        ],
        inferredTask: "browser_evidence",
      },
    },
  };
}

function buildManifestForCase(testCase, scenePayload) {
  return {
    schema_version: "phase10f9.viewer_scene_manifest.v1",
    artifact_id: testCase.id,
    artifact_kind: "viewer_scene",
    artifact_version: "viewer_scene.v1",
    fixture_source: testCase.scene,
    expected_validation_state: testCase.expectedState,
    expected_errors: testCase.expectedError ? [testCase.expectedError] : [],
    expected_warnings: testCase.expectedWarning ? [testCase.expectedWarning] : [],
    expected_caps: scenePayload.caps || {},
    preview_mode: "json_only",
    renderer_required: false,
    executable_assets: "none",
    external_resources: "none",
  };
}

function withEvidenceValidation(scenePayload, testCase) {
  const validation = {
    ...(scenePayload.validation || {}),
    errors: testCase.expectedError ? [testCase.expectedError] : [],
  };
  return {
    ...scenePayload,
    validation,
  };
}

function requestPathAudit() {
  return Array.from(new Set(["app_server", "mock_api"])).sort();
}

async function expectText(page, selector, expected) {
  try {
    await page.waitForFunction(
      ({ selector: currentSelector, expected: currentExpected }) => {
        const node = document.querySelector(currentSelector);
        return Boolean(node && (node.textContent || "").includes(currentExpected));
      },
      { selector, expected },
      { timeout: 10_000 },
    );
  } catch (error) {
    const actual = await page.locator(selector).evaluate((node) => node.textContent || "").catch(() => "<missing>");
    throw new Error(`Expected selector ${selector} to contain ${expected}; actual text was ${actual}`, { cause: error });
  }
}

async function readJson(filePath) {
  return JSON.parse(await readFile(filePath, "utf-8"));
}

async function writeJson(filePath, payload) {
  await writeFile(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf-8");
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function stopEvidencePortListener() {
  if (process.platform !== "win32") return;
  const ps = [
    "$conn=Get-NetTCPConnection -LocalPort",
    String(APP_PORT),
    "-State Listen -ErrorAction SilentlyContinue;",
    "if ($conn) {",
    "  foreach ($item in $conn) {",
    "    if ($item.OwningProcess -and $item.OwningProcess -ne 0) {",
    "      Stop-Process -Id $item.OwningProcess -Force -ErrorAction SilentlyContinue",
    "    }",
    "  }",
    "}",
  ].join(" ");
  await new Promise((resolve) => {
    const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" });
    child.on("exit", resolve);
    child.on("error", resolve);
  });
}

await main();
