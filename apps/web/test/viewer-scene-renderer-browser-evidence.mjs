import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(SCRIPT_DIR, "../../..");
const EVIDENCE_ROOT = path.join(REPO_ROOT, "docs", "phase10f", "evidence", "phase10f14_viewer_scene_renderer_foundation");
const SCREENSHOT_ROOT = path.join(EVIDENCE_ROOT, "screenshots");
const BROWSER_ROOT = path.join(EVIDENCE_ROOT, "browser");
const API_ROOT = path.join(EVIDENCE_ROOT, "api");
const PLAYWRIGHT_MODULE = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const BROWSER_EXECUTABLE = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const APP_PORT = Number(process.env.MDI_VIEWER_SCENE_RENDERER_EVIDENCE_PORT || "3314");
const APP_ORIGIN = `http://127.0.0.1:${APP_PORT}`;
const API_HOST = "localhost";
const API_PORT = "8000";

let livePayload = {};
let activeCaseId = "valid_minimal_crystal";
let activeMode = "live";
let externalRequests = [];
let consoleMessages = [];
let pageErrors = [];

async function main() {
  await Promise.all([mkdir(SCREENSHOT_ROOT, { recursive: true }), mkdir(BROWSER_ROOT, { recursive: true }), mkdir(API_ROOT, { recursive: true })]);
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
      args: ["--no-sandbox", "--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--disable-background-networking"],
    });
    const browserVersion = browser.version();
    const context = await browser.newContext({ viewport: { width: 1440, height: 1200 }, reducedMotion: "reduce" });
    const snapshots = [];

    snapshots.push(await runValidInteractionCase(context, browserVersion));
    snapshots.push(await runSimpleRendererCase(context, browserVersion, "multi_species_crystal", "06_multispecies_nacl_renderer.png"));
    snapshots.push(await runSimpleRendererCase(context, browserVersion, "warning_caps", "07_warning_caps_renderer.png"));
    snapshots.push(await runSimpleRendererCase(context, browserVersion, "bonds_disabled", "08_bonds_disabled_renderer.png"));
    snapshots.push(await runInvalidCase(context, browserVersion));
    snapshots.push(await runUnsupportedCase(context, browserVersion));
    snapshots.push(await runContextLossCase(context, browserVersion));

    await browser.close();
    const externalCount = snapshots.reduce((total, item) => total + item.external_request_count, 0);
    if (externalCount !== 0) throw new Error(`Renderer external network requests observed: ${externalCount}`);
    await writeJson(path.join(BROWSER_ROOT, "dom_snapshot.json"), { schema_version: "phase10f14.renderer_dom.v1", cases: snapshots });
    await writeJson(path.join(BROWSER_ROOT, "console_snapshot.json"), { schema_version: "phase10f14.renderer_console.v1", cases: snapshots.map(({ case_id, console_errors, page_errors }) => ({ case_id, console_errors, page_errors })) });
    await writeJson(path.join(BROWSER_ROOT, "network_snapshot.json"), { schema_version: "phase10f14.renderer_network.v1", external_request_count: externalCount, result: "NO_RENDERER_EXTERNAL_NETWORK_REQUESTS", cases: snapshots.map(({ case_id, external_request_count, local_request_paths }) => ({ case_id, external_request_count, local_request_paths })) });
    await writeJson(path.join(BROWSER_ROOT, "renderer_capability_snapshot.json"), { schema_version: "phase10f14.renderer_capability.v1", browser: browserVersion, viewport: [1440, 1200], cases: snapshots.map(({ case_id, renderer }) => ({ case_id, renderer })) });
    await writeJson(path.join(BROWSER_ROOT, "interaction_snapshot.json"), { schema_version: "phase10f14.renderer_interaction.v1", cases: snapshots.map(({ case_id, interactions }) => ({ case_id, interactions })) });
    await writeJson(path.join(BROWSER_ROOT, "lifecycle_snapshot.json"), { schema_version: "phase10f14.renderer_lifecycle.v1", valid_case: snapshots[0].lifecycle, context_loss: snapshots.at(-1).context_loss });
    await writeFile(path.join(EVIDENCE_ROOT, "README.md"), readme(browserVersion), "utf-8");
    await writeJson(path.join(EVIDENCE_ROOT, "evidence_manifest.json"), evidenceManifest(browserVersion, snapshots));
    console.log("NO_RENDERER_EXTERNAL_NETWORK_REQUESTS");
    console.log("VIEWER_SCENE_RENDERER_FOUNDATION_BROWSER_EVIDENCE_PASS");
  } finally {
    server.kill();
    await stopEvidencePortListener();
  }
}

async function runValidInteractionCase(context, browserVersion) {
  const page = await newEvidencePage(context);
  activeCaseId = "valid_minimal_crystal";
  activeMode = "live";
  await runProductFlow(page);
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "01_live_job_artifacts.png"), fullPage: true });
  const initializationMs = await openRenderer(page);
  const initial = await rendererEvidence(page);
  const canvas = page.getByTestId("viewer-scene-renderer-canvas");
  const initialPixels = await canvas.screenshot();
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "02_valid_si_renderer.png"), fullPage: true });

  const box = await canvas.boundingBox();
  if (!box) throw new Error("Renderer canvas has no bounding box");
  await page.mouse.move(box.x + box.width * 0.62, box.y + box.height * 0.52);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.38, box.y + box.height * 0.34, { steps: 12 });
  await page.mouse.up();
  await page.waitForTimeout(200);
  const rotated = await rendererEvidence(page);
  assertVectorChanged(initial.cameraPosition, rotated.cameraPosition, "rotation");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "03_valid_si_rotated.png"), fullPage: true });

  await canvas.hover();
  await page.mouse.wheel(0, -560);
  await page.waitForTimeout(200);
  const zoomed = await rendererEvidence(page);
  if (distance(zoomed.cameraPosition, zoomed.cameraTarget) >= distance(rotated.cameraPosition, rotated.cameraTarget)) throw new Error("Zoom interaction did not move camera toward target");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "04_valid_si_zoomed.png"), fullPage: true });

  await page.getByTestId("viewer-scene-renderer-reset").click();
  await page.waitForTimeout(150);
  const reset = await rendererEvidence(page);
  assertVectorClose(initial.cameraPosition, reset.cameraPosition, "reset camera");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "05_valid_si_reset.png"), fullPage: true });

  await page.getByTestId("viewer-scene-renderer-toggle-bonds").click();
  const bondsHidden = await rendererEvidence(page);
  if (bondsHidden.bondCount !== 0) throw new Error("Bond toggle did not hide rendered bonds");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "09_bonds_hidden.png"), fullPage: true });
  await page.getByTestId("viewer-scene-renderer-toggle-cell").click();
  const cellHidden = await rendererEvidence(page);
  if (cellHidden.latticeEdgeCount !== 0) throw new Error("Cell toggle did not hide lattice edges");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "10_unit_cell_hidden.png"), fullPage: true });

  await page.getByRole("tab", { name: "Scene JSON" }).click();
  if (await page.locator("canvas").count()) throw new Error("Renderer canvas survived JSON tab disposal");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "11_json_fallback.png"), fullPage: true });
  await page.getByRole("tab", { name: "3D Renderer" }).click();
  await page.waitForSelector('[data-testid="viewer-scene-renderer-canvas"]');
  if ((await page.locator("canvas").count()) !== 1) throw new Error("Renderer remount produced duplicate canvas elements");
  const remounted = await rendererEvidence(page);
  const finalPixels = await page.getByTestId("viewer-scene-renderer-canvas").screenshot();
  const snapshot = await browserAudit(page, browserVersion, {
    initial,
    rotated,
    zoomed,
    reset,
    bondsHidden,
    cellHidden,
    remounted,
    pixel_hash_initial: hash(initialPixels),
    pixel_hash_remounted: hash(finalPixels),
    initialization_ms: initializationMs,
  });
  snapshot.lifecycle = { canvas_after_json_tab: 0, canvas_after_remount: 1, remount_state: remounted.state, duplicate_canvas: false };
  await page.close();
  return snapshot;
}

async function runSimpleRendererCase(context, browserVersion, caseId, screenshot) {
  const page = await newEvidencePage(context);
  activeCaseId = caseId;
  activeMode = "live";
  await runProductFlow(page);
  const initializationMs = await openRenderer(page);
  const renderer = await rendererEvidence(page);
  if (renderer.canvasCount !== 1 || renderer.atomCount < 1 || renderer.latticeEdgeCount !== 12) throw new Error(`Renderer object audit failed for ${caseId}`);
  if (caseId === "bonds_disabled" && renderer.bondCount !== 0) throw new Error("Bonds-disabled live artifact rendered synthetic bonds");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, screenshot), fullPage: true });
  const snapshot = await browserAudit(page, browserVersion, { rendered: renderer, initialization_ms: initializationMs });
  await page.close();
  return snapshot;
}

async function runInvalidCase(context, browserVersion) {
  const page = await newEvidencePage(context);
  activeCaseId = "valid_minimal_crystal";
  activeMode = "invalid";
  await runProductFlow(page);
  await page.getByRole("tab", { name: "3D Renderer" }).click();
  await page.waitForSelector('[data-testid="viewer-scene-renderer-invalid"]');
  if (await page.locator("canvas").count()) throw new Error("Invalid scene initialized a renderer canvas");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "12_invalid_scene_rejected.png"), fullPage: true });
  const snapshot = await browserAudit(page, browserVersion, { validation_failed: true });
  await page.close();
  return snapshot;
}

async function runUnsupportedCase(context, browserVersion) {
  activeCaseId = "valid_minimal_crystal";
  activeMode = "unsupported";
  const page = await newEvidencePage(context, true);
  await runProductFlow(page);
  await page.getByRole("tab", { name: "3D Renderer" }).click();
  await page.waitForSelector('[data-testid="viewer-scene-renderer-unavailable"]');
  if (await page.locator("canvas").count()) throw new Error("Unsupported renderer created a canvas");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "13_renderer_unavailable_fallback.png"), fullPage: true });
  const snapshot = await browserAudit(page, browserVersion, { unsupported: true });
  await page.close();
  return snapshot;
}

async function runContextLossCase(context, browserVersion) {
  const page = await newEvidencePage(context);
  activeCaseId = "valid_minimal_crystal";
  activeMode = "context_loss";
  await runProductFlow(page);
  const initializationMs = await openRenderer(page);
  const supported = await page.evaluate(() => {
    const canvas = document.querySelector('[data-testid="viewer-scene-renderer-canvas"]');
    const gl = canvas?.getContext("webgl2") || canvas?.getContext("webgl");
    const extension = gl?.getExtension("WEBGL_lose_context");
    extension?.loseContext();
    return Boolean(extension);
  });
  if (!supported) throw new Error("WEBGL_lose_context is unavailable for context-loss evidence");
  await page.waitForSelector('[data-testid="viewer-scene-renderer-fallback"]');
  await page.waitForTimeout(100);
  if (await page.locator("canvas").count()) throw new Error("Context-lost renderer canvas was not cleaned up");
  await page.screenshot({ path: path.join(SCREENSHOT_ROOT, "14_context_loss_fallback.png"), fullPage: true });
  const snapshot = await browserAudit(page, browserVersion, { context_lost: true, initialization_ms: initializationMs });
  snapshot.context_loss = { extension_available: true, safe_fallback: true, canvas_after_cleanup: 0 };
  await page.close();
  return snapshot;
}

async function newEvidencePage(context, forceUnsupported = false) {
  externalRequests = [];
  consoleMessages = [];
  pageErrors = [];
  const page = await context.newPage();
  await page.addInitScript(({ unsupported }) => {
    const original = HTMLCanvasElement.prototype.getContext;
    window.__mdiRendererContextRequests = [];
    HTMLCanvasElement.prototype.getContext = function patched(type, ...args) {
      const name = String(type).toLowerCase();
      if (name.includes("webgl")) window.__mdiRendererContextRequests.push(name);
      if (unsupported && name.includes("webgl")) return null;
      return original.call(this, type, ...args);
    };
    window.EventSource = class MockEventSource { constructor(url) { this.url = url; this.readyState = 2; } close() { this.readyState = 2; } addEventListener() {} removeEventListener() {} };
  }, { unsupported: forceUnsupported });
  page.on("console", (message) => consoleMessages.push({ type: message.type(), text: message.text() }));
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === API_HOST && url.port === API_PORT) return fulfillApi(route, url);
    if ((url.hostname === "127.0.0.1" || url.hostname === "localhost") && url.port === String(APP_PORT)) {
      if (url.pathname === "/favicon.ico") return route.fulfill({ status: 204, body: "" });
      return route.continue();
    }
    if (url.protocol === "data:" || url.protocol === "blob:") return route.continue();
    externalRequests.push({ host: url.hostname, path: url.pathname });
    return route.abort();
  });
  return page;
}

async function runProductFlow(page) {
  await page.goto(APP_ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill("Build an inert viewer scene artifact for this structure");
  await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click();
  await page.waitForSelector('[data-testid="viewer-scene-json-preview"]', { state: "attached" });
}

async function openRenderer(page) {
  const started = Date.now();
  await page.getByRole("tab", { name: "3D Renderer" }).click();
  await page.waitForFunction(() => {
    const state = document.querySelector('[data-testid="viewer-scene-renderer-state"]')?.textContent;
    return state && !["ready", "initializing_renderer"].includes(state);
  }, null, { timeout: 20_000 });
  if (!(await page.locator('[data-testid="viewer-scene-renderer-canvas"]').count())) {
    const state = await page.locator('[data-testid="viewer-scene-renderer-state"]').textContent().catch(() => "missing");
    const fallback = await page.locator('[data-testid="viewer-scene-renderer-fallback"],[data-testid="viewer-scene-renderer-unavailable"],[data-testid="viewer-scene-renderer-invalid"]').textContent().catch(() => "none");
    const canvasCount = await page.locator("canvas").count();
    throw new Error(`Renderer did not create an evidence canvas: state=${state}, canvasCount=${canvasCount}, fallback=${fallback}, console=${JSON.stringify(consoleMessages)}`);
  }
  await page.waitForFunction(() => document.querySelector('[data-testid="viewer-scene-renderer-state"]')?.textContent === "rendered", null, { timeout: 20_000 });
  return Date.now() - started;
}

async function rendererEvidence(page) {
  return page.evaluate(() => window.__mdiViewerSceneRendererEvidence || null).then((value) => {
    if (!value) throw new Error("Renderer evidence snapshot is unavailable");
    return value;
  });
}

async function browserAudit(page, browserVersion, interactions) {
  const dom = await page.evaluate(() => {
    const canvas = document.querySelector('[data-testid="viewer-scene-renderer-canvas"]');
    let graphics = null;
    if (canvas) {
      const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
      const debug = gl?.getExtension("WEBGL_debug_renderer_info");
      graphics = gl ? {
        version: gl.getParameter(gl.VERSION),
        vendor: debug ? gl.getParameter(debug.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR),
        renderer: debug ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
        drawing_buffer: [gl.drawingBufferWidth, gl.drawingBufferHeight],
        context_attributes: gl.getContextAttributes(),
      } : null;
    }
    return {
      canvas_count: document.querySelectorAll("canvas").length,
      iframe_count: document.querySelectorAll("iframe").length,
      object_embed_count: document.querySelectorAll("object,embed").length,
      script_count: document.querySelectorAll("script").length,
      external_script_count: [...document.querySelectorAll("script[src]")].filter((node) => {
        const url = new URL(node.src, window.location.href);
        return url.origin !== window.location.origin;
      }).length,
      inline_handler_count: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length,
      javascript_uri_count: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
      three_global: Boolean(window.THREE),
      matterviz_global: Boolean(window.MatterViz),
      context_requests: window.__mdiRendererContextRequests || [],
      renderer_state: document.querySelector('[data-testid="viewer-scene-renderer-state"]')?.textContent || "",
      graphics,
    };
  });
  if (dom.iframe_count || dom.object_embed_count || dom.external_script_count || dom.inline_handler_count || dom.javascript_uri_count || dom.three_global || dom.matterviz_global) throw new Error(`Renderer inertness audit failed for ${activeCaseId}`);
  const errors = consoleMessages.filter((message) => message.type === "error" && !/404/.test(message.text));
  if (errors.length || pageErrors.length || externalRequests.length) throw new Error(`Browser audit failed for ${activeCaseId}: console=${errors.length}, page=${pageErrors.length}, external=${externalRequests.length}`);
  return {
    case_id: `${activeCaseId}:${activeMode}`,
    browser: browserVersion,
    selected_tool: livePayload.cases[activeCaseId]?.planner?.selected_tool || "structure.viewer_scene",
    renderer: dom,
    interactions,
    console_errors: errors,
    page_errors: [...pageErrors],
    external_request_count: externalRequests.length,
    local_request_paths: ["next_app", "captured_live_planner_api", "local_renderer_chunk"],
  };
}

async function fulfillApi(route, requestUrl) {
  const method = route.request().method();
  const liveCase = livePayload.cases[activeCaseId];
  const jobId = liveCase.planner.job_id;
  const pathName = requestUrl.pathname;
  if (pathName === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock", provider: "mock" } } });
  if (pathName === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (pathName === "/datasets/demo" && method === "POST") return route.fulfill({ json: demoDataset() });
  if (pathName === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (pathName === "/planner/providers/status") return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (pathName === "/planner/providers/resolve") return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", willUseLiveProvider: false, secretConfigured: false } });
  if (pathName === "/me/secrets") return route.fulfill({ json: [] });
  if (pathName === "/planner/jobs" && method === "POST") return route.fulfill({ json: jobCreateResult(liveCase) });
  if (pathName === `/planner/jobs/${jobId}`) return route.fulfill({ json: liveCase.api.job });
  if (pathName === `/planner/jobs/${jobId}/events`) return route.fulfill({ json: liveCase.api.events });
  if (pathName === `/planner/jobs/${jobId}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (pathName === `/planner/jobs/${jobId}/tool-calls`) return route.fulfill({ json: liveCase.api.tool_calls });
  if (pathName === `/planner/jobs/${jobId}/artifacts`) return route.fulfill({ json: artifactResponse(liveCase.api.artifacts) });
  if (pathName === `/planner/jobs/${jobId}/result`) return route.fulfill({ json: { ...liveCase.api.result, artifacts: artifactResponse(liveCase.api.result.artifacts || liveCase.api.artifacts) } });
  return route.fulfill({ status: 404, json: { detail: "renderer evidence route not found", path: pathName } });
}

function artifactResponse(artifacts) {
  const copy = structuredClone(artifacts);
  if (activeMode === "invalid") {
    const scene = copy.find((artifact) => artifact.name === "viewer_scene.json");
    scene.content.invalid_external_resource_reference = "EXTERNAL_RESOURCE_PLACEHOLDER_REJECTED_BY_CONTRACT";
  }
  return copy;
}

function jobCreateResult(liveCase) {
  return { ok: true, job_id: liveCase.planner.job_id, plan_id: liveCase.planner.plan_id, plan_hash: liveCase.planner.plan_hash, validation_errors: [], plan: liveCase.api.analysis_plan.analysisPlan, plan_source: "mock", planner_provider: "MockLLMProvider", enqueued: true, executed: true };
}

function demoDataset() {
  return { id: "dataset_demo", datasetId: "dataset_demo", projectId: "project_10f14", name: "Viewer renderer evidence dataset", status: "ready", demo: true, profileId: "profile_demo", profile: { id: "profile_demo", profileId: "profile_demo", datasetId: "dataset_demo", datasetType: "structure_collection", version: "phase10f14.renderer.profile.v1", status: "ready", profileGenerated: true, objects: [{ objectType: "Structure", count: 1, source: "live_adapter_evidence" }] } };
}

function generateLivePayload() {
  const result = spawnSync("uv", ["run", "python", "apps/web/test/generate-viewer-scene-live-adapter-evidence.py", "docs/phase10f/evidence/phase10f14_viewer_scene_renderer_foundation"], { cwd: REPO_ROOT, encoding: "utf-8", env: { ...process.env, PYTHONIOENCODING: "utf-8", MDI_INCLUDE_RENDERER_CASES: "1" } });
  if (result.status !== 0) throw new Error(`Live renderer evidence generation failed\n${result.stdout}\n${result.stderr}`);
  process.stdout.write(result.stdout);
}

function startDevServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(APP_PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(APP_PORT)];
  const child = spawn(command, args, { cwd: REPO_ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: `http://${API_HOST}:${API_PORT}` }, stdio: ["ignore", "pipe", "pipe"] });
  child.stdout.on("data", (chunk) => process.stdout.write(chunk));
  child.stderr.on("data", (chunk) => process.stderr.write(chunk));
  return child;
}

async function waitForApp() {
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    try { if ((await fetch(APP_ORIGIN)).ok) return; } catch {}
    await delay(500);
  }
  throw new Error("Timed out waiting for renderer evidence app");
}

function assertVectorChanged(before, after, label) {
  if (distance(before, after) < 0.01) throw new Error(`${label} did not change camera position`);
}

function assertVectorClose(expected, actual, label) {
  if (distance(expected, actual) > 0.001) throw new Error(`${label} did not return to deterministic camera position`);
}

function distance(left, right) { return Math.hypot(left[0] - right[0], left[1] - right[1], left[2] - right[2]); }
function hash(buffer) { return createHash("sha256").update(buffer).digest("hex"); }
function delay(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }
async function readJson(filePath) { return JSON.parse(await readFile(filePath, "utf-8")); }
async function writeJson(filePath, value) { await writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf-8"); }

function readme(browserVersion) {
  return `# Phase 10F-14 Viewer Scene Renderer Foundation Evidence\n\nCommand: \`node apps/web/test/viewer-scene-renderer-browser-evidence.mjs\`\n\nBrowser: ${browserVersion}\nRenderer: Three.js 0.185.1\nSource: live \`structure.viewer_scene\` adapter job artifacts\nNetwork: NO_RENDERER_EXTERNAL_NETWORK_REQUESTS\nResult: VIEWER_SCENE_RENDERER_FOUNDATION_BROWSER_EVIDENCE_PASS\n`;
}

function evidenceManifest(browserVersion, snapshots) {
  const artifactHashes = Object.fromEntries(Object.entries(livePayload.cases).flatMap(([caseId, item]) => (item.api?.artifacts || []).map((artifact) => [`${caseId}/${artifact.name}`, artifact.sha256 || artifact.contentHash || "unavailable"])));
  return { schema_version: "phase10f14.viewer_scene_renderer_evidence_manifest.v1", phase: "10F-14", baseline_head: "7477433c971c5fe93017386636bfbf2b532b018f", final_head: "git_commit_containing_this_manifest", generated_at: new Date().toISOString(), browser: browserVersion, viewport: [1440, 1200], renderer_dependency: { package: "three", version: "0.185.1" }, generation_command: "node apps/web/test/viewer-scene-renderer-browser-evidence.mjs", cases: snapshots.map((item) => item.case_id), screenshots: ["01_live_job_artifacts.png", "02_valid_si_renderer.png", "03_valid_si_rotated.png", "04_valid_si_zoomed.png", "05_valid_si_reset.png", "06_multispecies_nacl_renderer.png", "07_warning_caps_renderer.png", "08_bonds_disabled_renderer.png", "09_bonds_hidden.png", "10_unit_cell_hidden.png", "11_json_fallback.png", "12_invalid_scene_rejected.png", "13_renderer_unavailable_fallback.png", "14_context_loss_fallback.png"], artifact_hashes: artifactHashes, network_result: "NO_RENDERER_EXTERNAL_NETWORK_REQUESTS", console_result: "PASS", security_result: "PASS", test_result: "VIEWER_SCENE_RENDERER_FOUNDATION_BROWSER_EVIDENCE_PASS", redaction_status: "sanitized_no_secrets_no_private_paths" };
}

async function stopEvidencePortListener() {
  if (process.platform !== "win32") return;
  const ps = `$conn=Get-NetTCPConnection -LocalPort ${APP_PORT} -State Listen -ErrorAction SilentlyContinue; if ($conn) { foreach ($item in $conn) { if ($item.OwningProcess -and $item.OwningProcess -ne 0) { Stop-Process -Id $item.OwningProcess -Force -ErrorAction SilentlyContinue } } }`;
  await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); });
}

await main();
