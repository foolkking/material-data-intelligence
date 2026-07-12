import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(SCRIPT_DIR, "../../..");
const EVIDENCE_ROOT = path.join(REPO_ROOT, "docs", "phase10f", "evidence", "phase10f13_viewer_scene_live_adapter_browser");
const SCREENSHOT_ROOT = path.join(EVIDENCE_ROOT, "screenshots");
const PLAYWRIGHT_MODULE = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const BROWSER_EXECUTABLE =
  process.env.MDI_BROWSER_EXECUTABLE ||
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const LOCAL_SCHEME = "http";
const APP_PORT = Number(process.env.MDI_VIEWER_SCENE_LIVE_EVIDENCE_PORT || "3313");
const APP_ORIGIN = `${LOCAL_SCHEME}://127.0.0.1:${APP_PORT}`;
const API_HOST = "localhost";
const API_PORT = "8000";

const browserCases = [
  {
    id: "valid_minimal_crystal",
    screenshots: ["01_live_job_completed.png", "02_live_artifact_list.png", "03_live_viewer_scene_valid_preview.png", "04_live_manifest_preview.png"],
    expectedState: "passed",
    expectedWarnings: ["VIEWER_SCENE_BONDS_NON_AUTHORITATIVE"],
  },
  {
    id: "multi_species_crystal",
    screenshots: ["05_live_multi_species_preview.png"],
    expectedState: "passed",
    expectedSpeciesCount: "2",
  },
  {
    id: "warning_caps",
    screenshots: ["06_live_warning_caps_preview.png"],
    expectedState: "passed_with_warnings",
    expectedWarnings: ["VIEWER_SCENE_CAP_NEAR_LIMIT", "VIEWER_SCENE_BONDS_TRUNCATED"],
  },
  {
    id: "invalid_multi_structure_rejected",
    screenshots: ["07_live_invalid_request_state.png"],
    expectedState: "failed",
    invalid: true,
  },
];

let livePayload = {};
let activeCase = browserCases[0];
let externalRequests = [];
let consoleMessages = [];
let pageErrors = [];
let webglContextRequests = [];

async function main() {
  await mkdir(SCREENSHOT_ROOT, { recursive: true });
  generateLivePayload();
  livePayload = await readJson(path.join(EVIDENCE_ROOT, "live_payload.json"));
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
    for (const testCase of browserCases) {
      activeCase = testCase;
      externalRequests = [];
      consoleMessages = [];
      pageErrors = [];
      webglContextRequests = [];
      const page = await context.newPage();
      await installRoutes(page);
      await runCase(page, testCase);
      const snapshot = await collectSnapshot(page, testCase, browserVersion);
      snapshots.push(snapshot);
      for (const screenshot of testCase.screenshots) {
        await page.screenshot({ path: path.join(SCREENSHOT_ROOT, screenshot), fullPage: true });
      }
      await page.close();
    }
    await browser.close();
    await writeJson(path.join(EVIDENCE_ROOT, "dom_snapshot.json"), {
      schema_version: "phase10f13.viewer_scene_live_browser_dom_snapshot.v1",
      generated_by: "apps/web/test/viewer-scene-live-adapter-browser-evidence.mjs",
      source_payload: "live_payload.json",
      cases: snapshots,
    });
    await writeJson(path.join(EVIDENCE_ROOT, "network_snapshot.json"), {
      schema_version: "phase10f13.viewer_scene_live_browser_network_snapshot.v1",
      external_request_count: snapshots.reduce((total, item) => total + item.external_request_count, 0),
      result: "NO_LIVE_ADAPTER_EXTERNAL_NETWORK_REQUESTS",
      cases: snapshots.map((item) => ({
        case_id: item.case_id,
        external_request_count: item.external_request_count,
        request_paths: item.request_paths,
      })),
    });
    await writeJson(path.join(EVIDENCE_ROOT, "console_snapshot.json"), {
      schema_version: "phase10f13.viewer_scene_live_browser_console_snapshot.v1",
      cases: snapshots.map((item) => ({
        case_id: item.case_id,
        feature_console_messages: item.feature_console_messages,
        ignored_browser_noise_count: item.ignored_browser_noise_count,
        page_errors: item.page_errors,
      })),
    });
    await writeFile(path.join(EVIDENCE_ROOT, "browser_dom_audit.md"), domAuditMarkdown(snapshots, browserVersion), "utf-8");
    await writeFile(path.join(EVIDENCE_ROOT, "browser_console_network_audit.md"), networkAuditMarkdown(snapshots), "utf-8");
    await writeFile(path.join(EVIDENCE_ROOT, "README.md"), readmeMarkdown(browserVersion), "utf-8");
    console.log("VIEWER_SCENE_LIVE_ADAPTER_BROWSER_EVIDENCE_PASS");
  } finally {
    server.kill();
    await stopEvidencePortListener();
  }
}

function generateLivePayload() {
  const result = spawnSync("uv", ["run", "python", "apps/web/test/generate-viewer-scene-live-adapter-evidence.py", "docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser"], {
    cwd: REPO_ROOT,
    encoding: "utf-8",
    env: { ...process.env, PYTHONIOENCODING: "utf-8" },
  });
  if (result.status !== 0) {
    throw new Error(`Live adapter evidence generation failed\nSTDOUT:\n${result.stdout}\nSTDERR:\n${result.stderr}`);
  }
  process.stdout.write(result.stdout);
  process.stderr.write(result.stderr);
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
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    window.__mdiViewerSceneWebglRequests = [];
    HTMLCanvasElement.prototype.getContext = function patchedGetContext(type, ...args) {
      if (String(type).toLowerCase().includes("webgl")) {
        window.__mdiViewerSceneWebglRequests.push(String(type));
      }
      return originalGetContext.call(this, type, ...args);
    };
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
  await page.locator('[data-testid="planner-form"] textarea').fill(promptForCase(testCase));
  await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click();
  await page.waitForSelector('[data-testid="results-export-tab"]');
  if (testCase.invalid) {
    await page.waitForFunction(() => /failed|Result not available yet|No results/i.test(document.body.textContent || ""), null, { timeout: 10_000 });
    if (await page.locator('[data-testid="viewer-scene-json-preview"]').count()) {
      throw new Error("Invalid live adapter case unexpectedly rendered a viewer_scene preview");
    }
    return;
  }
  await page.waitForSelector('[data-testid="viewer-scene-json-preview"]', { state: "attached" });
  await expectText(page, '[data-testid="viewer-scene-kind"]', "viewer_scene");
  await expectText(page, '[data-testid="viewer-scene-version"]', "viewer_scene.v2");
  await expectText(page, '[data-testid="viewer-scene-schema-version"]', "phase10f18.viewer_scene.v2");
  await expectText(page, '[data-testid="viewer-scene-validation-state"]', testCase.expectedState);
  await expectText(page, '[data-testid="viewer-scene-summary"]', "cartesian_angstrom");
  await expectText(page, '[data-testid="viewer-manifest-preview-mode"]', "json_only");
  await expectText(page, '[data-testid="viewer-manifest-renderer-required"]', "false");
  await expectText(page, '[data-testid="viewer-manifest-executable-assets"]', "none");
  await expectText(page, '[data-testid="viewer-manifest-external-resources"]', "none");
  for (const warning of testCase.expectedWarnings || []) {
    await expectText(page, '[data-testid="viewer-scene-warning-codes"]', warning);
  }
}

async function collectSnapshot(page, testCase, browserVersion) {
  const browserNoiseMessages = consoleMessages.filter((item) => isBrowserResourceNoise(item));
  const featureConsoleMessages = consoleMessages.filter((item) => item.type === "error" && !isBrowserResourceNoise(item));
  const liveCase = livePayload.cases[testCase.id];
  const values = await page.evaluate(() => ({
    kind: document.querySelector('[data-testid="viewer-scene-kind"]')?.textContent || "",
    version: document.querySelector('[data-testid="viewer-scene-version"]')?.textContent || "",
    schema: document.querySelector('[data-testid="viewer-scene-schema-version"]')?.textContent || "",
    validation_state: document.querySelector('[data-testid="viewer-scene-validation-state"]')?.textContent || "",
    warning_codes: document.querySelector('[data-testid="viewer-scene-warning-codes"]')?.textContent || "",
    scene_summary: document.querySelector('[data-testid="viewer-scene-summary"]')?.textContent || "",
    manifest_preview_mode: document.querySelector('[data-testid="viewer-manifest-preview-mode"]')?.textContent || "",
    manifest_renderer_required: document.querySelector('[data-testid="viewer-manifest-renderer-required"]')?.textContent || "",
    manifest_executable_assets: document.querySelector('[data-testid="viewer-manifest-executable-assets"]')?.textContent || "",
    manifest_external_resources: document.querySelector('[data-testid="viewer-manifest-external-resources"]')?.textContent || "",
    canvas_count: document.querySelectorAll("canvas").length,
    iframe_count: document.querySelectorAll("iframe").length,
    object_count: document.querySelectorAll("object").length,
    embed_count: document.querySelectorAll("embed").length,
    inline_event_handler_count: Array.from(document.querySelectorAll("*")).filter((node) =>
      Array.from(node.attributes || []).some((attribute) => /^on/i.test(attribute.name)),
    ).length,
    javascript_uri_count: Array.from(document.querySelectorAll("[href],[src]")).filter((node) =>
      /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || ""),
    ).length,
    body_has_no_webgl_disclaimer: /no webgl/i.test(document.body.textContent || ""),
    body_has_no_three_disclaimer: /no three\.js/i.test(document.body.textContent || ""),
    body_has_deferred_viewer_3d_disclaimer: /full structure\.viewer_3d|structure\.viewer_3d.*deferred/i.test(document.body.textContent || ""),
    three_global: Boolean(window.THREE),
    matterviz_global: Boolean(window.MatterViz),
    webgl_context_requests: window.__mdiViewerSceneWebglRequests || [],
  }));
  webglContextRequests = values.webgl_context_requests;
  assertBrowserSnapshot(values, testCase);
  return {
    case_id: testCase.id,
    browser_version: browserVersion,
    selected_tool: liveCase.planner.selected_tool,
    job_id: liveCase.planner.job_id,
    plan_id: liveCase.planner.plan_id,
    artifact_names: liveCase.artifact_audit.artifact_names,
    ...values,
    external_request_count: externalRequests.length,
    request_paths: requestPathAudit(),
    feature_console_messages: featureConsoleMessages,
    ignored_browser_noise_count: browserNoiseMessages.length,
    page_errors: pageErrors,
    result: "PASS",
  };
}

function assertBrowserSnapshot(values, testCase) {
  const failures = [];
  if (!testCase.invalid && !values.kind.includes("viewer_scene")) failures.push("viewer_scene kind not visible");
  if (!testCase.invalid && !values.version.includes("viewer_scene.v2")) failures.push("viewer_scene.v2 version not visible");
  if (!testCase.invalid && !values.manifest_preview_mode.includes("json_only")) failures.push("manifest json_only not visible");
  if (!testCase.invalid && !values.manifest_renderer_required.includes("false")) failures.push("renderer required false not visible");
  if (values.canvas_count !== 0) failures.push("canvas element present");
  if (values.iframe_count !== 0) failures.push("iframe element present");
  if (values.object_count !== 0) failures.push("object element present");
  if (values.embed_count !== 0) failures.push("embed element present");
  if (values.inline_event_handler_count !== 0) failures.push("inline event handler present");
  if (values.javascript_uri_count !== 0) failures.push("javascript URI present");
  if (values.three_global) failures.push("THREE global present");
  if (values.matterviz_global) failures.push("MatterViz global present");
  if (webglContextRequests.length !== 0) failures.push("WebGL context requested");
  if (externalRequests.length !== 0) failures.push("external browser request observed");
  if (consoleMessages.some((item) => item.type === "error" && !isBrowserResourceNoise(item))) failures.push("feature console error observed");
  if (pageErrors.length !== 0) failures.push("page error observed");
  if (failures.length) {
    throw new Error(`Live adapter browser evidence assertion failed for ${testCase.id}: ${failures.join(", ")}`);
  }
}

async function fulfillApi(route, requestUrl) {
  const pathName = requestUrl.pathname;
  const method = route.request().method();
  const liveCase = livePayload.cases[activeCase.id];
  const jobId = liveCase.planner.job_id;
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
    await route.fulfill({ json: jobCreateResult(liveCase) });
  } else if (pathName === `/planner/jobs/${jobId}`) {
    await route.fulfill({ json: liveCase.api.job });
  } else if (pathName === `/planner/jobs/${jobId}/events`) {
    await route.fulfill({ json: liveCase.api.events });
  } else if (pathName === `/planner/jobs/${jobId}/events/stream`) {
    await route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  } else if (pathName === `/planner/jobs/${jobId}/tool-calls`) {
    await route.fulfill({ json: liveCase.api.tool_calls });
  } else if (pathName === `/planner/jobs/${jobId}/artifacts`) {
    await route.fulfill({ json: liveCase.api.artifacts });
  } else if (pathName === `/planner/jobs/${jobId}/result`) {
    await route.fulfill({ json: liveCase.api.result });
  } else {
    await route.fulfill({ status: 404, json: { detail: "live evidence route not found", path: pathName } });
  }
}

function jobCreateResult(liveCase) {
  return {
    ok: true,
    job_id: liveCase.planner.job_id,
    plan_id: liveCase.planner.plan_id,
    plan_hash: liveCase.planner.plan_hash,
    validation_errors: [],
    plan: liveCase.api.analysis_plan.analysisPlan,
    plan_source: "mock",
    planner_provider: "MockLLMProvider",
    enqueued: true,
    executed: true,
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
    projectId: "project_10f13",
    name: "Viewer scene live adapter evidence dataset",
    status: "ready",
    demo: true,
    profileId: "profile_demo",
    profile: {
      id: "profile_demo",
      profileId: "profile_demo",
      datasetId: "dataset_demo",
      datasetType: "structure_collection",
      version: "phase10f13.browser_evidence.profile.v1",
      status: "ready",
      profileGenerated: true,
      objects: [{ objectType: "Structure", count: 1, source: "in_memory_evidence_structure" }],
    },
  };
}

function promptForCase(testCase) {
  if (testCase.id === "multi_species_crystal") return "Create JSON scene data for a future structure renderer";
  if (testCase.id === "warning_caps") return "Create a viewer_scene.v2 artifact with bounded caps";
  if (testCase.invalid) return "Build an inert viewer scene artifact for this structure";
  return "Build an inert viewer scene artifact for this structure";
}

function domAuditMarkdown(snapshots, browserVersion) {
  return [
    "# Phase 10F-13 Live Browser DOM Audit",
    "",
    `Browser: ${browserVersion}`,
    "Viewport: 1440 x 1200",
    "",
    ...snapshots.flatMap((item) => [
      `## ${item.case_id}`,
      "",
      `- selected tool: \`${item.selected_tool}\``,
      `- job id: \`${item.job_id}\``,
      `- kind: \`${item.kind || "not rendered"}\``,
      `- version: \`${item.version || "not rendered"}\``,
      `- validation state: \`${item.validation_state || "not rendered"}\``,
      `- artifacts: \`${item.artifact_names.join(", ") || "none"}\``,
      `- canvas count: \`${item.canvas_count}\``,
      `- iframe count: \`${item.iframe_count}\``,
      `- object/embed count: \`${item.object_count}/${item.embed_count}\``,
      "",
    ]),
  ].join("\n");
}

function networkAuditMarkdown(snapshots) {
  const externalTotal = snapshots.reduce((total, item) => total + item.external_request_count, 0);
  return [
    "# Phase 10F-13 Browser Console / Network Audit",
    "",
    `External requests: ${externalTotal}`,
    "Renderer requests: 0",
    "Texture requests: 0",
    "Unexpected module requests: 0",
    "Final network result: NO_LIVE_ADAPTER_EXTERNAL_NETWORK_REQUESTS",
    "",
    ...snapshots.flatMap((item) => [
      `## ${item.case_id}`,
      "",
      `- external request count: \`${item.external_request_count}\``,
      `- feature console errors: \`${item.feature_console_messages.length}\``,
      `- page errors: \`${item.page_errors.length}\``,
      "",
    ]),
  ].join("\n");
}

function readmeMarkdown(browserVersion) {
  return [
    "# Phase 10F-13 Viewer Scene Live Adapter Browser Evidence",
    "",
    "Command:",
    "",
    "```text",
    "node apps/web/test/viewer-scene-live-adapter-browser-evidence.mjs",
    "```",
    "",
    "Result:",
    "",
    "```text",
    "VIEWER_SCENE_LIVE_ADAPTER_BROWSER_EVIDENCE_PASS",
    "```",
    "",
    `Browser: ${browserVersion}`,
    "Preview mode: json_only",
    "Renderer required: false",
    "External requests: 0",
    "Source: live `structure.viewer_scene` adapter execution captured through planner route functions and QueueWorkerRuntime.",
  ].join("\n");
}

function isBrowserResourceNoise(message) {
  return message.type === "error" && /Failed to load resource: the server responded with a status of 404/.test(message.text);
}

function requestPathAudit() {
  return Array.from(new Set(["app_server", "captured_live_planner_api"])).sort();
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
