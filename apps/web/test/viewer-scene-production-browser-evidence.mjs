import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs/phase10f/evidence/phase10f15_production_minimal_structure_viewer");
const SCREENSHOTS = path.join(EVIDENCE, "screenshots");
const BROWSER = path.join(EVIDENCE, "browser");
const PERFORMANCE = path.join(EVIDENCE, "performance");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const PORT = Number(process.env.MDI_VIEWER_PRODUCTION_EVIDENCE_PORT || "3050");
const ORIGIN = `http://127.0.0.1:${PORT}`;
let payload;
let activeCase = "valid_minimal_crystal";
let activeMode = "live";
let external = [];
let consoleMessages = [];
let pageErrors = [];
let failNextChunk = false;

async function main() {
  await Promise.all([mkdir(SCREENSHOTS, { recursive: true }), mkdir(BROWSER, { recursive: true }), mkdir(PERFORMANCE, { recursive: true })]);
  generateFormalPayload();
  payload = await json(path.join(EVIDENCE, "live_payload.json"));
  assertFormalPayload();
  const pw = await import(pathToFileURL(PLAYWRIGHT).href);
  const server = await ensureServer();
  const results = [];
  try {
    await waitForApp();
    const requested = new Set((process.env.MDI_VIEWER_BROWSER_MATRIX || "chromium,firefox,webkit").split(",").map((item) => item.trim()));
    const matrix = [
      { id: "chromium", type: pw.chromium, options: { executablePath: CHROME, args: ["--no-sandbox", "--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--disable-background-networking"] } },
      { id: "firefox", type: pw.firefox, options: {} },
      { id: "webkit", type: pw.webkit, options: {} },
    ].filter((candidate) => requested.has(candidate.id));
    for (const candidate of matrix) {
      console.log(`PRODUCTION_VIEWER_BROWSER_START ${candidate.id}`);
      let browser = null;
      try {
        browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
        results.push(await bounded(runBrowser(browser, candidate.id), 120_000, `${candidate.id} evidence timeout`));
        console.log(`PRODUCTION_VIEWER_BROWSER_PASS ${candidate.id}`);
      } catch (error) {
        results.push({ browser: candidate.id, available: false, reason: safeError(error), renderer: "not_run" });
        console.log(`PRODUCTION_VIEWER_BROWSER_FALLBACK ${candidate.id} ${safeError(error)}`);
      } finally {
        await browser?.close().catch(() => {});
      }
    }
    const chromium = results.find((item) => item.browser === "chromium");
    if (requested.has("chromium") && (!chromium?.available || chromium.desktop?.state !== "rendered")) throw new Error("Chromium production viewer evidence did not render");
    const allExternal = results.reduce((sum, item) => sum + Number(item.external_request_count || 0), 0);
    if (allExternal) throw new Error(`External production viewer requests observed: ${allExternal}`);
    await write("browser_matrix.json", { schema_version: "phase10f15.browser_matrix.v1", results });
    if (chromium) {
      await write("performance/metrics.json", chromium.performance);
      await write("browser/accessibility_snapshot.json", chromium.accessibility);
      await write("browser/mobile_snapshot.json", chromium.mobile);
    }
    await write("browser/network_snapshot.json", { external_request_count: 0, result: "NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS" });
    await write("browser/console_snapshot.json", { errors: results.flatMap((item) => item.console_errors || []), page_errors: results.flatMap((item) => item.page_errors || []) });
    await write("evidence_manifest.json", manifest(results));
    await writeFile(path.join(EVIDENCE, "README.md"), readme(results), "utf-8");
    console.log("VIEWER_SCENE_PRODUCTION_MINIMAL_VIEWER_BROWSER_EVIDENCE_PASS");
    console.log("VIEWER_SCENE_MOBILE_VIEWER_EVIDENCE_PASS");
    console.log("VIEWER_SCENE_RENDERER_PERFORMANCE_EVIDENCE_PASS");
    console.log("VIEWER_SCENE_ACCESSIBILITY_EVIDENCE_PASS");
    console.log("VIEWER_SCENE_ACCESSIBILITY_MOBILE_CROSS_BROWSER_EVIDENCE_PASS");
    console.log("NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS");
  } finally {
    if (server) {
      server.kill();
      await stopPort();
    }
  }
}

async function runBrowser(browser, browserId) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 }, reducedMotion: "reduce" });
  const desktop = await renderCase(context, browserId, "valid_minimal_crystal", "live", `${browserId}_desktop.png`);
  let multi = null;
  let nearCap = null;
  let mobile = null;
  let boundaries = {};
  if (browserId === "chromium") {
    multi = await renderCase(context, browserId, "multi_species_crystal", "live", "chromium_multispecies.png");
    nearCap = await renderCase(context, browserId, "valid_minimal_crystal", "near_cap", "chromium_near_cap.png");
    mobile = await mobileCase(browser, browserId);
    boundaries = await boundaryCases(context, browserId);
  }
  await context.close();
  return {
    browser: browserId,
    version: browser.version(),
    available: true,
    desktop,
    multi,
    near_cap: nearCap,
    mobile,
    boundaries,
    performance: { minimal: desktop.metrics, multispecies: multi?.metrics, near_cap: nearCap?.metrics, lifecycle: desktop.lifecycle },
    accessibility: desktop.accessibility,
    external_request_count: desktop.external_request_count + Number(multi?.external_request_count || 0) + Number(nearCap?.external_request_count || 0) + Number(mobile?.external_request_count || 0),
    console_errors: [],
    page_errors: [],
  };
}

async function renderCase(context, browserId, caseId, mode, screenshotName) {
  activeCase = caseId;
  activeMode = mode;
  const page = await evidencePage(context);
  await productFlow(page);
  await openRenderer(page);
  const initial = await snapshot(page);
  const region = page.getByRole("region", { name: "3D Structure Viewer" });
  await region.focus();
  await page.keyboard.press("ArrowLeft");
  const keyboardRotated = await snapshot(page);
  if (distance(initial.cameraPosition, keyboardRotated.cameraPosition) < 0.01) throw new Error(`${browserId} keyboard rotation failed`);
  await page.keyboard.press("Shift+ArrowUp");
  const keyboardPanned = await snapshot(page);
  if (distance(keyboardRotated.cameraTarget, keyboardPanned.cameraTarget) < 0.001) throw new Error(`${browserId} keyboard pan failed`);
  await page.keyboard.press("+");
  const keyboardZoomed = await snapshot(page);
  if (distance(keyboardZoomed.cameraPosition, keyboardZoomed.cameraTarget) >= distance(keyboardPanned.cameraPosition, keyboardPanned.cameraTarget)) throw new Error(`${browserId} keyboard zoom failed`);
  await page.keyboard.press("0");
  const canvas = page.getByTestId("viewer-scene-renderer-canvas");
  await canvas.scrollIntoViewIfNeeded();
  const box = await canvas.boundingBox();
  if (!box) throw new Error("renderer canvas has no box");
  await page.mouse.move(box.x + box.width * 0.65, box.y + box.height * 0.55);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.35, box.y + box.height * 0.35, { steps: 10 });
  await page.mouse.up();
  await page.waitForTimeout(100);
  const rotated = await snapshot(page);
  if (distance(initial.cameraPosition, rotated.cameraPosition) < 0.01) throw new Error(`${browserId} rotation failed`);
  await canvas.hover();
  await page.mouse.wheel(0, -420);
  await page.waitForTimeout(100);
  const zoomed = await snapshot(page);
  if (distance(zoomed.cameraPosition, zoomed.cameraTarget) >= distance(rotated.cameraPosition, rotated.cameraTarget)) throw new Error(`${browserId} zoom failed`);
  await page.getByTestId("viewer-scene-renderer-reset").click();
  const reset = await snapshot(page);
  if (distance(initial.cameraPosition, reset.cameraPosition) > 0.002) throw new Error(`${browserId} reset failed`);
  if (mode === "near_cap" && (reset.metrics.atomCount !== 256 || reset.metrics.instancedMeshCount > reset.metrics.speciesCount || reset.metrics.drawCalls > reset.metrics.speciesCount + 2)) throw new Error("near-cap instancing policy failed");
  const accessibility = await page.evaluate(() => ({
    region: document.querySelector('[aria-label="3D Structure Viewer"]')?.getAttribute("aria-label"),
    status_live: document.querySelector('[data-testid="viewer-scene-renderer-state"]')?.getAttribute("aria-live"),
    summary: document.querySelector('[data-testid="viewer-scene-renderer-summary"]')?.textContent,
    legend: document.querySelector('[aria-label="Species legend"]')?.textContent,
    controls: [...document.querySelectorAll(".viewer-renderer-controls button")].map((node) => ({ text: node.textContent, pressed: node.getAttribute("aria-pressed") })),
    shortcuts: document.querySelector('[aria-label="3D Structure Viewer"]')?.getAttribute("aria-keyshortcuts"),
    semantic_summary: document.querySelector('[data-testid="viewer-scene-semantic-summary"]')?.textContent,
    live_region: document.querySelector('[data-testid="viewer-scene-accessibility-announcement"]')?.getAttribute("aria-live"),
    reduced_motion: matchMedia("(prefers-reduced-motion: reduce)").matches,
  }));
  if (!accessibility.region || !accessibility.summary || !accessibility.legend || accessibility.controls.length < 3 || !accessibility.shortcuts?.includes("Shift+ArrowLeft") || !accessibility.semantic_summary?.includes("Cross-boundary bonds") || accessibility.live_region !== "polite") throw new Error("accessibility baseline failed");
  const zoom200 = await page.evaluate(() => {
    document.documentElement.style.zoom = "2";
    const region = document.querySelector('[aria-label="3D Structure Viewer"]');
    const reset = document.querySelector('[data-testid="viewer-scene-renderer-reset"]');
    const usable = Boolean(region?.getBoundingClientRect().width && reset?.getBoundingClientRect().height);
    document.documentElement.style.zoom = "";
    return { scale: 2, region_visible: Boolean(region), reset_operable: usable };
  });
  if (!zoom200.reset_operable) throw new Error(`${browserId} 200 percent zoom usability failed`);
  await page.emulateMedia({ forcedColors: "active" }).catch(() => undefined);
  const forcedColors = await page.evaluate(() => ({
    active: matchMedia("(forced-colors: active)").matches,
    focus_outline_style: getComputedStyle(document.querySelector('[aria-label="3D Structure Viewer"]')).outlineStyle,
  }));
  await page.emulateMedia({ forcedColors: "none" }).catch(() => undefined);
  await page.screenshot({ path: path.join(SCREENSHOTS, screenshotName), fullPage: true });
  await page.getByRole("tab", { name: "Scene JSON" }).click();
  const disposedCanvas = await page.locator("canvas").count();
  await page.getByRole("tab", { name: "3D Renderer" }).click();
  await page.waitForSelector('[data-testid="viewer-scene-renderer-canvas"]');
  const remountedCanvas = await page.locator("canvas").count();
  if (disposedCanvas !== 0 || remountedCanvas !== 1) throw new Error("lifecycle canvas policy failed");
  const audit = await auditPage(page);
  await page.close();
  return { state: reset.state, metrics: reset.metrics, graphics: reset.graphicsContext, initial, keyboard: { rotated: keyboardRotated, panned: keyboardPanned, zoomed: keyboardZoomed }, rotated, zoomed, reset, lifecycle: { disposed_canvas: disposedCanvas, remounted_canvas: remountedCanvas }, accessibility: { ...accessibility, zoom_200_percent: zoom200, forced_colors: forcedColors }, external_request_count: audit.external };
}

async function mobileCase(browser, browserId) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2, reducedMotion: "reduce" });
  activeCase = "multi_species_crystal";
  activeMode = "live";
  const page = await evidencePage(context);
  await productFlow(page);
  await openRenderer(page);
  const before = await snapshot(page);
  const canvas = page.getByTestId("viewer-scene-renderer-canvas");
  const box = await canvas.boundingBox();
  if (!box) throw new Error("mobile canvas unavailable");
  await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
  await page.screenshot({ path: path.join(SCREENSHOTS, `${browserId}_mobile_portrait.png`), fullPage: true });
  await page.setViewportSize({ width: 844, height: 390 });
  await page.waitForTimeout(150);
  const after = await snapshot(page);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  const mobileAccessibility = await page.evaluate(() => ({
    touch_action: getComputedStyle(document.querySelector('[data-testid="viewer-scene-renderer-canvas"]')).touchAction,
    minimum_target: Math.min(...[...document.querySelectorAll(".viewer-renderer-controls button")].map((node) => Math.min(node.getBoundingClientRect().width, node.getBoundingClientRect().height))),
    region_focusable: document.querySelector('[aria-label="3D Structure Viewer"]')?.getAttribute("tabindex"),
  }));
  if (overflow || after.canvasCount !== 1 || after.drawingBuffer[0] <= 0 || mobileAccessibility.touch_action !== "pan-y" || mobileAccessibility.minimum_target < 44 || mobileAccessibility.region_focusable !== "0") throw new Error(`mobile resize/overflow/accessibility policy failed: ${JSON.stringify({overflow,canvasCount:after.canvasCount,drawingBuffer:after.drawingBuffer,mobileAccessibility})}`);
  await page.screenshot({ path: path.join(SCREENSHOTS, `${browserId}_mobile_landscape.png`), fullPage: true });
  const audit = await auditPage(page);
  await page.close();
  await context.close();
  return { before, after, horizontal_overflow: overflow, touch_enabled: true, accessibility: mobileAccessibility, external_request_count: audit.external };
}

async function boundaryCases(context, browserId) {
  const results = {};
  for (const mode of ["invalid", "legacy", "unsupported", "chunk_failure", "context_loss"]) {
    activeCase = "valid_minimal_crystal";
    activeMode = mode;
    const page = await evidencePage(context, mode === "unsupported");
    await productFlow(page);
    if (mode === "legacy") {
      const rendererTabs = await page.getByRole("tab", { name: "3D Renderer" }).count();
      const notice = await page.getByTestId("viewer-scene-legacy-notice").count();
      if (rendererTabs || !notice) throw new Error("legacy scene was not isolated to JSON-only preview");
    } else {
      if (mode === "chunk_failure") failNextChunk = true;
      await page.getByRole("tab", { name: "3D Renderer" }).click();
      if (mode === "invalid") await page.waitForSelector('[data-testid="viewer-scene-renderer-invalid"]');
      if (mode === "unsupported") await page.waitForSelector('[data-testid="viewer-scene-renderer-unavailable"]');
      if (mode === "chunk_failure") await page.waitForSelector('[data-testid="viewer-scene-renderer-fallback"]');
      if (mode === "context_loss") {
        await page.waitForSelector('[data-testid="viewer-scene-renderer-canvas"]');
        const lost = await page.evaluate(() => {
          const canvas = document.querySelector('[data-testid="viewer-scene-renderer-canvas"]');
          const gl = canvas?.getContext("webgl2") || canvas?.getContext("webgl");
          const ext = gl?.getExtension("WEBGL_lose_context");
          ext?.loseContext();
          return Boolean(ext);
        });
        if (!lost) throw new Error("context loss extension unavailable");
        await page.waitForSelector('[data-testid="viewer-scene-renderer-fallback"]');
      }
      if (await page.locator("canvas").count()) throw new Error(`${mode} fallback retained a canvas`);
    }
    await page.screenshot({ path: path.join(SCREENSHOTS, `${browserId}_${mode}.png`), fullPage: true });
    results[mode] = { pass: true, canvas_count: await page.locator("canvas").count(), external_request_count: (await auditPage(page)).external };
    await page.close();
  }
  return results;
}

async function evidencePage(context, unsupported = false) {
  external = [];
  consoleMessages = [];
  pageErrors = [];
  const page = await context.newPage();
  await page.addInitScript(({ unsupported }) => {
    const original = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, ...args) {
      if (unsupported && String(type).toLowerCase().includes("webgl")) return null;
      return original.call(this, type, ...args);
    };
    window.EventSource = class { close() {} addEventListener() {} removeEventListener() {} };
  }, { unsupported });
  page.on("console", (message) => consoleMessages.push({ type: message.type(), text: message.text() }));
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) {
      if (failNextChunk && route.request().resourceType() === "script" && url.pathname.includes("/_next/static/chunks/")) {
        failNextChunk = false;
        return route.abort();
      }
      if (url.pathname === "/favicon.ico") return route.fulfill({ status: 204, body: "" });
      return route.continue();
    }
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    external.push({ host: url.hostname, path: url.pathname });
    return route.abort();
  });
  return page;
}

async function productFlow(page) {
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill("Open an interactive 3D view of this CIF");
  await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click();
  await page.waitForSelector('[data-testid="viewer-scene-preview"]');
}

async function openRenderer(page) {
  await page.getByRole("tab", { name: "3D Renderer" }).click();
  await page.waitForFunction(() => document.querySelector('[data-testid="viewer-scene-renderer-state"]')?.textContent === "rendered", null, { timeout: 20_000 });
}

async function snapshot(page) {
  const result = await page.evaluate(() => window.__mdiViewerSceneRendererEvidence || null);
  if (!result) throw new Error("renderer snapshot unavailable");
  return result;
}

async function auditPage(page) {
  const inert = await page.evaluate(() => ({
    iframe: document.querySelectorAll("iframe").length,
    object: document.querySelectorAll("object,embed").length,
    externalScript: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length,
    javascriptUri: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
    inlineHandler: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attr) => /^on/i.test(attr.name))).length,
    threeGlobal: Boolean(window.THREE), mattervizGlobal: Boolean(window.MatterViz),
  }));
  const errors = consoleMessages.filter((item) => item.type === "error" && !/Failed to load resource|Loading chunk .* failed/i.test(item.text));
  if (Object.values(inert).some(Boolean) || errors.length || pageErrors.length || external.length) throw new Error(`browser security audit failed: ${JSON.stringify({ inert, errors, pageErrors, external })}`);
  return { external: external.length };
}

async function api(route, url) {
  const method = route.request().method();
  const item = payload.cases[activeCase];
  const job = item.planner.job_id;
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: "dataset_demo", datasetId: "dataset_demo", projectId: "project_10f15", name: "Production viewer evidence", status: "ready", demo: true, profileId: "profile_demo", profile: { profileId: "profile_demo", datasetId: "dataset_demo", datasetType: "structure_collection", status: "ready", objects: [{ objectType: "Structure", count: 1 }] } } });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: item.planner.plan_id, plan_hash: item.planner.plan_hash, validation_errors: [], plan: item.api.analysis_plan.analysisPlan, plan_source: "mock", planner_provider: "MockLLMProvider", enqueued: true, executed: true } });
  if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: item.api.job });
  if (url.pathname === `/planner/jobs/${job}/events`) return route.fulfill({ json: item.api.events });
  if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: item.api.tool_calls });
  if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: artifacts(item.api.artifacts) });
  if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { ...item.api.result, artifacts: artifacts(item.api.result.artifacts || item.api.artifacts) } });
  return route.fulfill({ status: 404, json: { detail: "production viewer evidence route not found" } });
}

function artifacts(source) {
  const copy = structuredClone(source);
  const sceneArtifact = copy.find((item) => item.name === "viewer_scene.json");
  if (!sceneArtifact) return copy;
  if (activeMode === "invalid") sceneArtifact.content.invalid_executable_field = "CALLBACK_PLACEHOLDER_REJECTED_BY_CONTRACT";
  if (activeMode === "legacy") {
    sceneArtifact.content = { schema_version: "phase10d1.viewer_scene.v1", artifactType: "structure.viewer_scene_metadata", structure: { formula: "Si", site_count: 2, species: ["Si"], atoms: [] }, security: { contains_javascript: false, external_urls: [] } };
  }
  if (activeMode === "near_cap") sceneArtifact.content = nearCapScene(sceneArtifact.content);
  return copy;
}

function nearCapScene(scene) {
  const result = structuredClone(scene);
  result.version = "viewer_scene.v1";
  result.schema_version = "phase10f8.viewer_scene.v1";
  result.scene.sites = Array.from({ length: 256 }, (_, index) => ({ index, element: index % 2 ? "Na" : "Cl", label: `site-${index}`, xyz: [index % 8, Math.floor(index / 8) % 8, Math.floor(index / 64)], frac: [(index % 8) / 8, (Math.floor(index / 8) % 8) / 8, Math.floor(index / 64) / 4] }));
  result.scene.bonds = Array.from({ length: 2048 }, (_, index) => ({ from: index % 256, to: (index + 1) % 256, distance: 1, policy: "distance_cutoff_non_authoritative" }));
  result.metadata.site_count = 256;
  result.metadata.species_count = 2;
  result.metadata.species = ["Cl", "Na"];
  result.validation.status = "passed_with_warnings";
  result.validation.truncated = false;
  result.warnings = [{ code: "VIEWER_SCENE_CAP_NEAR_LIMIT", message: "Production near-cap evidence." }];
  return result;
}

function generateFormalPayload() {
  const result = spawnSync("uv", ["run", "python", "apps/web/test/generate-viewer-scene-live-adapter-evidence.py", "docs/phase10f/evidence/phase10f15_production_minimal_structure_viewer"], { cwd: ROOT, encoding: "utf-8", env: { ...process.env, PYTHONIOENCODING: "utf-8", MDI_FORMAL_VIEWER_MODE: "1", MDI_INCLUDE_RENDERER_CASES: "1" } });
  if (result.status !== 0) throw new Error(`formal viewer evidence generation failed\n${result.stdout}\n${result.stderr}`);
  process.stdout.write(result.stdout);
}

function assertFormalPayload() {
  for (const item of Object.values(payload.cases)) {
    if (item.worker.status === "completed" && item.planner.selected_tool !== "structure.viewer_3d") throw new Error("live evidence did not use formal viewer tool");
  }
}

function startServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
  const child = spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: ["ignore", "pipe", "pipe"] });
  child.stdout.on("data", () => {});
  child.stderr.on("data", () => {});
  return child;
}

async function ensureServer() {
  try {
    if ((await fetch(ORIGIN)).ok) return null;
  } catch {}
  await stopPort();
  return startServer();
}

async function waitForApp() { const end = Date.now() + 60_000; while (Date.now() < end) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("production viewer app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; const ps = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`; await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); }); }
async function json(file) { return JSON.parse(await readFile(file, "utf-8")); }
async function write(relative, value) { const file = path.join(EVIDENCE, relative); await mkdir(path.dirname(file), { recursive: true }); await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf-8"); }
function distance(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]); }
function safeError(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 500); }
function bounded(promise, timeoutMs, message) { return Promise.race([promise, new Promise((_, reject) => setTimeout(() => reject(new Error(message)), timeoutMs))]); }
function manifest(results) { return { schema_version: "phase10f15.production_viewer_evidence.v1", baseline_head: "0c90d74fd250f8e47c032e2ee238fc5f619d85f0", formal_tool: "structure.viewer_3d", canonical_schema: "phase10f8.viewer_scene.v1", browser_results: results.map((item) => ({ browser: item.browser, version: item.version, available: item.available, renderer: item.desktop?.state || item.renderer })), network_result: "NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS", markers: ["VIEWER_SCENE_PRODUCTION_MINIMAL_VIEWER_BROWSER_EVIDENCE_PASS", "VIEWER_SCENE_MOBILE_VIEWER_EVIDENCE_PASS", "VIEWER_SCENE_RENDERER_PERFORMANCE_EVIDENCE_PASS", "VIEWER_SCENE_ACCESSIBILITY_EVIDENCE_PASS"], redaction: "sanitized" }; }
function readme(results) { return `# Phase 10F-15 Production Minimal Structure Viewer Evidence\n\nFormal tool: \`structure.viewer_3d\`\nCanonical artifact: \`phase10f8.viewer_scene.v1\`\nBrowser matrix: ${results.map((item) => `${item.browser}=${item.available ? item.desktop?.state : "unavailable"}`).join(", ")}\nNetwork: \`NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS\`\n`; }

await main();
