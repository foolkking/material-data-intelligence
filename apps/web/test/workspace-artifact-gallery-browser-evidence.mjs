import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || path.join(ROOT, "apps", "web", "node_modules", "playwright", "index.mjs");
const OUTPUT = argumentValue("--output-dir") ? path.resolve(argumentValue("--output-dir")) : path.join(ROOT, "docs", "phase10m", "evidence", "phase10m4_artifact_gallery_viewers");
const PORT = Number(process.env.MDI_PHASE10M4_EVIDENCE_PORT || "3226");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const HASH = "a".repeat(64);
const CHECK_ONLY = process.argv.includes("--validate-fixtures");

async function main() {
  const artifacts = await artifactFixtures();
  validateFixtures(artifacts);
  if (CHECK_ONLY) return console.log("PHASE10M4_ARTIFACT_FIXTURE_VALIDATION_PASS");
  const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
  const requested = (process.env.MDI_PHASE10M4_BROWSERS || "chromium,firefox,webkit").split(",").map((item) => item.trim()).filter(Boolean);
  if (requested.length !== 3 || !["chromium", "firefox", "webkit"].every((name) => requested.includes(name))) throw new Error("M4 requires Chromium, Firefox, and WebKit.");
  await mkdir(path.join(OUTPUT, "screenshots"), { recursive: true });
  const server = await ensureServer();
  try {
    await waitForApp();
    const matrix = {};
    for (const name of requested) {
      const browser = await ({ chromium, firefox, webkit })[name].launch(browserLaunchOptions(name));
      try { matrix[name] = await runDesktop(browser, name, artifacts); } finally { await browser.close(); }
      await writeJson(`browser_${name}/summary.json`, matrix[name]);
    }
    const mobileBrowser = await chromium.launch(browserLaunchOptions("chromium"));
    let mobile;
    try { mobile = await runMobile(mobileBrowser, artifacts); } finally { await mobileBrowser.close(); }
    await writeJson("browser_mobile/summary.json", mobile);
    await writeJson("browser_matrix.json", matrix);
    await writeJson("mobile_smoke.json", mobile);
    await writeJson("network_summary.json", { externalRequestCount: 0, allowedOrigins: [ORIGIN, API_ORIGIN], marker: "NO_PHASE10M4_UNAPPROVED_EXTERNAL_REQUESTS" });
    await writeJson("console_summary.json", { consoleErrors: [], pageErrors: [], marker: "NO_PHASE10M4_BROWSER_CONSOLE_ERRORS" });
    console.log("PHASE10M4_CHROMIUM_FIREFOX_WEBKIT_PASS");
    console.log("PHASE10M4_CHROMIUM_390X844_PASS");
  } finally { await stopServer(server); }
}

async function runDesktop(browser, browserName, artifacts) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1050 }, reducedMotion: "reduce", acceptDownloads: true });
  const page = await context.newPage();
  await installLifecycleAudit(page);
  const audit = attachAudit(page), calls = [];
  await installApiFixture(page, calls, artifacts);
  await page.goto(`${ORIGIN}/workspaces/workspace_gallery?panel=panel_scientific_result`, { waitUntil: "networkidle" });
  await page.getByTestId("workspace-artifact-gallery").waitFor();
  await page.locator(".workspace-artifact-card").nth(artifacts.length - 1).waitFor({ timeout: 30000 });
  if (calls.some((call) => call.includes("/content"))) throw new Error(`${browserName}: initial Workspace load fetched an Artifact payload`);
  if ((await page.locator(".workspace-artifact-card").count()) !== artifacts.length) throw new Error(`${browserName}: Gallery inventory mismatch`);
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", `${browserName}_gallery.png`), fullPage: true });

  const exactReferenceNavigation = await exerciseExactReferenceNavigation(page, artifacts[0], browserName);
  const partialWarning = page.locator(".workspace-panel-warning").filter({ hasText: "successful source branches" });
  if (!(await partialWarning.isVisible())) throw new Error(`${browserName}: partial-result isolation warning is absent`);
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", `${browserName}_partial.png`), fullPage: true });
  const cases = {};
  let contextLoss = { tested: false, lostState: null, recovered: false, remainingCanvases: null };
  for (const name of ["Dataset Explorer", "Regression Evaluation", "Composition Space", "Structure Scene", "Trajectory", "Phonon Band", "Brillouin Zone", "Volumetric Dataset", "Generic Metrics"]) {
    const before = calls.filter((call) => call.includes("/content")).length;
    const button = page.getByRole("button", { name: `Open ${name}` });
    await button.click();
    await page.getByText(/bounded payload record/u).waitFor({ timeout: 30000 });
    const renderer = await waitForFormalRenderer(page, name);
    const after = calls.filter((call) => call.includes("/content")).length;
    cases[name] = { payloadRequests: after - before, ...renderer };
    if (after <= before) throw new Error(`${browserName}: ${name} did not lazy-load a payload`);
    if (name === "Structure Scene" && browserName === "chromium") contextLoss = await exerciseContextLoss(page);
    await page.getByRole("button", { name: "Close viewer" }).click();
    if (await page.locator(".workspace-active-artifact canvas").count()) throw new Error(`${browserName}: ${name} retained a canvas after close`);
    await page.waitForTimeout(50);
    const afterClose = await lifecycleSnapshot(page);
    cases[name].lifecycleAfterClose = afterClose;
    if (afterClose.activeWebglContexts !== 0) throw new Error(`${browserName}: ${name} retained active WebGL contexts ${JSON.stringify(afterClose)}`);
  }

  const legacyOpen = page.getByRole("button", { name: "Open Legacy Result" });
  if (!(await legacyOpen.isDisabled())) throw new Error(`${browserName}: legacy contract received a guessed renderer`);
  const htmlOpen = page.getByRole("button", { name: "Open HTML Report" });
  if (!(await htmlOpen.isDisabled())) throw new Error(`${browserName}: HTML received execution authority`);

  const lifecycleBaseline = await lifecycleSnapshot(page);
  const lifecyclePeak = { ...lifecycleBaseline };
  let maxCanvases = 0;
  const lifecycleCycles = browserName === "chromium" ? 50 : 3;
  for (let cycle = 0; cycle < lifecycleCycles; cycle += 1) {
    await page.getByRole("button", { name: "Open Structure Scene" }).click();
    await page.getByText(/bounded payload record/u).waitFor({ timeout: 30000 });
    await waitForFormalRenderer(page, "Structure Scene");
    updateLifecyclePeak(lifecyclePeak, await lifecycleSnapshot(page));
    maxCanvases = Math.max(maxCanvases, await page.locator(".workspace-active-artifact canvas").count());
    await page.getByRole("button", { name: "Close viewer" }).click();
  }
  const remainingCanvases = await page.locator(".scientific-workspace canvas").count();
  if (maxCanvases > 1 || remainingCanvases !== 0) throw new Error(`${browserName}: heavy-viewer lifecycle cap failed`);
  await page.waitForTimeout(100);
  const lifecycleFinal = await lifecycleSnapshot(page);
  const lifecycleGrowth = lifecycleDelta(lifecycleBaseline, lifecycleFinal);
  if (lifecycleGrowth.listeners !== 0 || lifecycleGrowth.resizeObservers !== 0 || lifecycleGrowth.intersectionObservers !== 0 || lifecycleGrowth.pendingAnimationFrames !== 0 || lifecycleFinal.activeWebglContexts !== 0 || lifecyclePeak.activeWebglContexts > 1) {
    throw new Error(`${browserName}: lifecycle resource growth ${JSON.stringify({ lifecycleGrowth, peak: { resizeObservers: lifecyclePeak.resizeObservers, pendingAnimationFrames: lifecyclePeak.pendingAnimationFrames, activeWebglContexts: lifecyclePeak.activeWebglContexts } })}`);
  }
  const overflow = await page.evaluate(() => ({ body: document.body.scrollWidth - document.body.clientWidth, root: document.documentElement.scrollWidth - document.documentElement.clientWidth }));
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.failedResponses.length || audit.externalRequests.length) throw new Error(`${browserName}: browser audit failed ${JSON.stringify(audit)}`);
  await context.close();
  return { browserName, metadataFirst: true, artifactCount: artifacts.length, exactReferenceNavigation, partialIsolation: { dependencyOutcome: "PARTIAL_RESULTS", panelState: "PARTIAL", warningVisible: true, successfulArtifactsRemainOpenable: Object.values(cases).every((item) => item.rendererReady) }, cases, contextLoss, lifecycleAudit: { baseline: lifecycleBaseline, peak: lifecyclePeak, final: lifecycleFinal, growth: lifecycleGrowth }, legacyInert: true, htmlInert: true, heavySwitchCycles: lifecycleCycles, fullLifecycleGateBrowser: "chromium", maxActiveCanvases: maxCanvases, remainingCanvases, overflow, contentRequests: calls.filter((call) => call.includes("/content")).length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors, externalRequests: audit.externalRequests };
}

async function exerciseExactReferenceNavigation(page, artifact, browserName) {
  const card = page.locator(".workspace-artifact-card").filter({ hasText: "Dataset Explorer" });
  await card.getByRole("button", { name: "Evidence" }).click();
  await page.getByRole("heading", { name: "Scientific evidence", level: 2 }).waitFor({ timeout: 30000 });
  const evidence = page.getByTestId("workspace-grounded-evidence");
  await evidence.waitFor({ timeout: 30000 });
  await evidence.getByRole("button", { name: "Select exact evidence" }).click();
  const selectionStatus = page.getByTestId("workspace-selection-status");
  if (!/EVIDENCE_ITEM/u.test(await selectionStatus.innerText())) throw new Error(`${browserName}: exact evidence selection was not propagated`);
  await page.getByRole("button", { name: /Results/u }).click();
  await page.getByTestId("workspace-artifact-gallery").waitFor();
  await page.locator(".workspace-artifact-card").filter({ hasText: "Dataset Explorer" }).getByRole("button", { name: "Lineage" }).click();
  await page.getByRole("heading", { name: "Provenance", level: 2 }).waitFor({ timeout: 30000 });
  const lineage = page.getByTestId("workspace-artifact-lineage");
  await lineage.waitFor({ timeout: 30000 });
  if (!new RegExp(artifact.artifactId, "u").test(await lineage.innerText())) throw new Error(`${browserName}: exact Artifact lineage identity is absent`);
  await page.getByRole("button", { name: /Results/u }).click();
  await page.getByTestId("workspace-artifact-gallery").waitFor();
  return { artifactId: artifact.artifactId, evidenceItemId: "evidence_dataset_count", canonicalSelection: "EVIDENCE_ITEM", lineagePanel: "PROVENANCE", exact: true };
}

async function waitForFormalRenderer(page, name) {
  const active = page.locator(".workspace-active-artifact");
  try {
  if (name === "Dataset Explorer") await active.getByTestId("dataset-materials-explorer").waitFor({ timeout: 30000 });
  else if (name === "Regression Evaluation") await active.getByTestId("materials-ml-evaluation").waitFor({ timeout: 30000 });
  else if (name === "Composition Space") await active.getByTestId("composition-space-explorer").waitFor({ timeout: 30000 });
  else if (name === "Structure Scene") {
    await active.getByTestId("viewer-scene-renderer-state").filter({ hasText: "rendered" }).waitFor({ timeout: 30000 });
    await active.locator("[data-testid=viewer-scene-renderer-valid] canvas").waitFor({ timeout: 30000 });
  } else if (name === "Trajectory") {
    await active.getByTestId("trajectory-viewer-state").filter({ hasText: /paused|degraded/u }).waitFor({ timeout: 30000 });
    await active.locator("[data-testid=trajectory-canvas-host] canvas").waitFor({ timeout: 30000 });
  } else if (name === "Phonon Band") {
    await active.getByTestId("phonon-band-preview").waitFor({ timeout: 30000 });
    await page.waitForFunction(() => JSON.parse(document.querySelector('[data-testid="phonon-band-plot-metrics"]')?.textContent || "{}").state === "rendered", null, { timeout: 30000 });
  } else if (name === "Brillouin Zone") {
    await active.getByTestId("brillouin-zone-renderer-state").filter({ hasText: "rendered" }).waitFor({ timeout: 30000 });
    await active.locator("[data-testid=brillouin-zone-canvas-host] canvas").waitFor({ timeout: 30000 });
  } else if (name === "Volumetric Dataset") {
    await active.getByTestId("volumetric-metadata-preview").waitFor({ timeout: 30000 });
    await active.locator("[data-testid=volumetric-renderer-canvas-host] canvas").waitFor({ timeout: 30000 });
  } else if (name === "Generic Metrics") await active.getByText("Validated numeric table").waitFor({ timeout: 30000 });
  } catch (error) {
    const diagnostics = await active.evaluate((node) => ({
      text: (node.textContent || "").slice(0, 1000),
      testIds: [...node.querySelectorAll("[data-testid]")].map((item) => item.getAttribute("data-testid")).filter(Boolean).slice(0, 32),
    }));
    throw new Error(`${name} formal renderer gate failed: ${JSON.stringify(diagnostics)}`, { cause: error });
  }
  const canvasCount = await active.locator("canvas").count();
  return { rendererReady: true, canvasCount, typedFallback: false };
}

async function exerciseContextLoss(page) {
  const active = page.locator(".workspace-active-artifact");
  const canvas = active.locator("[data-testid=viewer-scene-renderer-valid] canvas");
  await canvas.evaluate((node) => node.dispatchEvent(new Event("webglcontextlost", { cancelable: true })));
  await active.getByTestId("viewer-scene-renderer-state").filter({ hasText: "context_lost" }).waitFor({ timeout: 30000 });
  const remainingCanvases = await active.locator("canvas").count();
  await active.getByRole("button", { name: "Retry renderer" }).click();
  await active.getByTestId("viewer-scene-renderer-state").filter({ hasText: "rendered" }).waitFor({ timeout: 30000 });
  await active.locator("[data-testid=viewer-scene-renderer-valid] canvas").waitFor({ timeout: 30000 });
  return { tested: true, lostState: "context_lost", recovered: true, remainingCanvases };
}

async function runMobile(browser, artifacts) {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await context.newPage();
  const audit = attachAudit(page), calls = [];
  await installApiFixture(page, calls, artifacts);
  await page.goto(`${ORIGIN}/workspaces/workspace_gallery?panel=panel_scientific_result`, { waitUntil: "networkidle" });
  await page.getByTestId("workspace-artifact-gallery").waitFor();
  await page.locator(".workspace-artifact-card").nth(artifacts.length - 1).waitFor({ timeout: 30000 });
  await page.getByRole("button", { name: "Open Structure Scene" }).click();
  await page.getByText(/bounded payload record/u).waitFor({ timeout: 30000 });
  await waitForFormalRenderer(page, "Structure Scene");
  const activeCanvases = await page.locator(".workspace-active-artifact canvas").count();
  await page.getByRole("button", { name: "Inspector" }).click();
  const inspector = page.getByRole("dialog", { name: "Context inspector" });
  await inspector.waitFor();
  const focusedClose = await inspector.getByRole("button", { name: "Close inspector" }).evaluate((element) => element === document.activeElement);
  await page.screenshot({ path: path.join(OUTPUT, "screenshots", "chromium_mobile_gallery.png"), fullPage: true });
  await page.keyboard.press("Escape");
  const focusRestored = await page.getByRole("button", { name: "Inspector" }).evaluate((element) => element === document.activeElement);
  const overflow = await page.evaluate(() => ({ body: document.body.scrollWidth - document.body.clientWidth, root: document.documentElement.scrollWidth - document.documentElement.clientWidth }));
  const minTouchTarget = await page.locator(".scientific-workspace button:visible").evaluateAll((items) => Math.min(...items.map((item) => Math.min(item.getBoundingClientRect().width, item.getBoundingClientRect().height))));
  if (activeCanvases > 1 || overflow.body > 0 || overflow.root > 0 || minTouchTarget < 44) throw new Error(`mobile lifecycle/responsive gate failed ${JSON.stringify({ activeCanvases, overflow, minTouchTarget })}`);
  if (audit.consoleErrors.length || audit.pageErrors.length || audit.failedResponses.length || audit.externalRequests.length) throw new Error(`mobile browser audit failed ${JSON.stringify(audit)}`);
  await context.close();
  return { viewport: [390, 844], oneActiveViewer: activeCanvases <= 1, activeCanvases, focusedClose, focusRestored, overflow, minTouchTarget, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors, externalRequests: audit.externalRequests, contentRequests: calls.filter((call) => call.includes("/content")).length };
}

async function installApiFixture(page, calls, artifacts) {
  await page.route(`${API_ORIGIN}/**`, async (route) => {
    const request = route.request(), url = new URL(request.url());
    calls.push(url.pathname);
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: corsHeaders() });
    if (url.pathname === "/workspaces/workspace_gallery") return route.fulfill(jsonResponse(snapshot(artifacts)));
    if (url.pathname === "/planner/jobs/job_gallery/artifacts") return route.fulfill(jsonResponse(artifacts.map(({ bytes, ...artifact }) => artifact)));
    if (url.pathname === "/planner/jobs/job_gallery/interpretations") return route.fulfill(jsonResponse(interpretationListFixture()));
    if (url.pathname === "/planner/interpretations/interpretation_gallery/evidence") return route.fulfill(jsonResponse(interpretationEvidenceFixture(artifacts[0])));
    const match = /^\/planner\/jobs\/job_gallery\/artifacts\/([^/]+)\/content$/u.exec(url.pathname);
    if (match) {
      const artifact = artifacts.find((item) => item.id === match[1]);
      if (!artifact) return route.fulfill(jsonResponse({ detail: { code: "NOT_FOUND" } }, 404));
      return route.fulfill({ status: 200, headers: { ...corsHeaders(), "content-type": artifact.contentType, "content-length": String(artifact.bytes.length), "x-content-length-validated": String(artifact.bytes.length), "x-content-type-options": "nosniff" }, body: artifact.bytes });
    }
    return route.fulfill(jsonResponse({ detail: { code: "FIXTURE_NOT_FOUND" } }, 404));
  });
}

async function installLifecycleAudit(page) {
  await page.addInitScript(() => {
    const originalAdd = EventTarget.prototype.addEventListener;
    const originalRemove = EventTarget.prototype.removeEventListener;
    const listenerRecords = new Map();
    const capture = (options) => typeof options === "boolean" ? options : Boolean(options?.capture);
    EventTarget.prototype.addEventListener = function auditedAdd(type, callback, options) {
      if (callback) {
        const records = listenerRecords.get(this) || [];
        if (!records.some((item) => item.type === type && item.callback === callback && item.capture === capture(options))) {
          records.push({ type, callback, capture: capture(options) });
          listenerRecords.set(this, records);
        }
      }
      return originalAdd.call(this, type, callback, options);
    };
    EventTarget.prototype.removeEventListener = function auditedRemove(type, callback, options) {
      const records = listenerRecords.get(this) || [];
      const index = records.findIndex((item) => item.type === type && item.callback === callback && item.capture === capture(options));
      if (index >= 0) {
        records.splice(index, 1);
      }
      return originalRemove.call(this, type, callback, options);
    };

    let resizeObservers = 0;
    if (globalThis.ResizeObserver) {
      const NativeResizeObserver = globalThis.ResizeObserver;
      globalThis.ResizeObserver = class AuditedResizeObserver {
        constructor(callback) { this.native = new NativeResizeObserver(callback); this.targets = new Set(); }
        observe(target, options) { if (!this.targets.has(target)) { this.targets.add(target); resizeObservers += 1; } return this.native.observe(target, options); }
        unobserve(target) { if (this.targets.delete(target)) resizeObservers -= 1; return this.native.unobserve(target); }
        disconnect() { resizeObservers -= this.targets.size; this.targets.clear(); return this.native.disconnect(); }
      };
    }

    let intersectionObservers = 0;
    if (globalThis.IntersectionObserver) {
      const NativeIntersectionObserver = globalThis.IntersectionObserver;
      globalThis.IntersectionObserver = class AuditedIntersectionObserver {
        constructor(callback, options) { this.native = new NativeIntersectionObserver(callback, options); this.targets = new Set(); }
        observe(target) { if (!this.targets.has(target)) { this.targets.add(target); intersectionObservers += 1; } return this.native.observe(target); }
        unobserve(target) { if (this.targets.delete(target)) intersectionObservers -= 1; return this.native.unobserve(target); }
        disconnect() { intersectionObservers -= this.targets.size; this.targets.clear(); return this.native.disconnect(); }
        takeRecords() { return this.native.takeRecords(); }
        get root() { return this.native.root; }
        get rootMargin() { return this.native.rootMargin; }
        get thresholds() { return this.native.thresholds; }
      };
    }

    const nativeRequestAnimationFrame = globalThis.requestAnimationFrame.bind(globalThis);
    const nativeCancelAnimationFrame = globalThis.cancelAnimationFrame.bind(globalThis);
    const animationFrames = new Set();
    globalThis.requestAnimationFrame = (callback) => {
      let identifier = 0;
      identifier = nativeRequestAnimationFrame((time) => { animationFrames.delete(identifier); callback(time); });
      animationFrames.add(identifier);
      return identifier;
    };
    globalThis.cancelAnimationFrame = (identifier) => { animationFrames.delete(identifier); return nativeCancelAnimationFrame(identifier); };

    const nativeGetContext = HTMLCanvasElement.prototype.getContext;
    const webglContexts = [];
    HTMLCanvasElement.prototype.getContext = function auditedGetContext(type, ...options) {
      const context = nativeGetContext.call(this, type, ...options);
      if (/^(?:webgl|webgl2|experimental-webgl)$/u.test(String(type)) && context && !webglContexts.some((item) => item.canvas === this && item.context === context)) webglContexts.push({ canvas: this, context });
      return context;
    };
    const activeWebglContexts = () => webglContexts.filter((item) => {
      try { return !item.context.isContextLost(); } catch { return item.canvas.isConnected; }
    }).length;
    const isActiveTarget = (target) => target === globalThis || target === document || !(target instanceof Node) || target.isConnected;
    const activeListeners = () => [...listenerRecords.entries()].reduce((total, [target, records]) => total + (isActiveTarget(target) ? records.length : 0), 0);
    Object.defineProperty(globalThis, "__phase10m4LifecycleAudit", { value: { snapshot: () => ({ listeners: activeListeners(), resizeObservers, intersectionObservers, pendingAnimationFrames: animationFrames.size, activeWebglContexts: activeWebglContexts(), createdWebglContexts: webglContexts.length, usedJsHeapBytes: globalThis.performance?.memory?.usedJSHeapSize ?? null }) } });
  });
}

async function lifecycleSnapshot(page) { return page.evaluate(() => globalThis.__phase10m4LifecycleAudit.snapshot()); }
function lifecycleDelta(before, after) {
  return { listeners: after.listeners - before.listeners, resizeObservers: after.resizeObservers - before.resizeObservers, intersectionObservers: after.intersectionObservers - before.intersectionObservers, pendingAnimationFrames: after.pendingAnimationFrames - before.pendingAnimationFrames, activeWebglContexts: after.activeWebglContexts - before.activeWebglContexts, usedJsHeapBytes: before.usedJsHeapBytes === null || after.usedJsHeapBytes === null ? null : after.usedJsHeapBytes - before.usedJsHeapBytes };
}
function updateLifecyclePeak(peak, sample) { for (const key of ["listeners", "resizeObservers", "intersectionObservers", "pendingAnimationFrames", "activeWebglContexts", "createdWebglContexts", "usedJsHeapBytes"]) if (sample[key] !== null) peak[key] = Math.max(peak[key] ?? sample[key], sample[key]); }

async function artifactFixtures() {
  const sources = [
    ["dataset", "table_json", "Dataset Explorer", "call_dataset", "docs/phase10k/evidence/phase10k5_material_intelligence_integration/products/replay_dataset/dataset_materials_explorer.json"],
    ["ml", "table_json", "Regression Evaluation", "call_ml", "docs/phase10k/evidence/phase10k5_material_intelligence_integration/products/replay_regression/materials_ml_regression.json"],
    ["composition", "table_json", "Composition Space", "call_composition", "docs/phase10k/evidence/phase10k5_material_intelligence_integration/products/case_a_c_f_composition/composition_space.json"],
    ["structure", "structure_json", "Structure Scene", "call_structure", "docs/phase10f/fixtures/viewer_scene_v1/valid_minimal_crystal.viewer_scene.v1.json"],
    ["trajectory", "trajectory_json", "Trajectory", "call_trajectory", "docs/phase10g/fixtures/trajectory_viewer/fixed_lattice_md_12_frames.json"],
    ["phonon_band", "phonon_band_json", "Phonon Band", "call_phonon", "docs/phase10h/fixtures/phonon_contract/stable_band.json"],
    ["phonon_dos", "phonon_dos_json", "Phonon DOS", "call_phonon", "docs/phase10h/fixtures/phonon_contract/projected_dos.json"],
    ["reciprocal", "reciprocal_lattice_json", "Reciprocal Lattice", "call_bz", "docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/reciprocal_lattice.json"],
    ["bz", "brillouin_zone_json", "Brillouin Zone", "call_bz", "docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/brillouin_zone.json"],
    ["kpath", "kpath_json", "K Path", "call_bz", "docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/kpath.json"],
    ["bz_manifest", "brillouin_zone_manifest_json", "BZ Manifest", "call_bz", "docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/manifest.json"],
  ];
  const items = [];
  for (const [id, type, name, toolCallId, relative] of sources) items.push(artifact(id, type, name, toolCallId, await readFile(path.join(ROOT, relative))));
  const volumeFixture = JSON.parse(await readFile(path.join(ROOT, "docs/phase10j/fixtures/volumetric_contract/cubic_constant_scalar.json"), "utf8"));
  for (const [id, type, name, value] of [
    ["volume_dataset", "volumetric_dataset_json", "Volumetric Dataset", volumeFixture.raw_dataset],
    ["volume_grid", "volumetric_grid_json", "Volumetric Grid", volumeFixture.grid],
    ["volume_field", "volumetric_field_json", "Volumetric Field", volumeFixture.raw_field],
    ["volume_payload", "volumetric_payload_json", "Volumetric Payload", volumeFixture.raw_payload],
    ["volume_manifest", "volumetric_manifest_json", "Volumetric Manifest", volumeFixture.manifest],
  ]) items.push(artifact(id, type, name, "call_volume", Buffer.from(JSON.stringify(value))));
  const volumeBinary = Buffer.alloc(volumeFixture.values.length * Float64Array.BYTES_PER_ELEMENT);
  volumeFixture.values.forEach((value, index) => volumeBinary.writeDoubleLE(value, index * Float64Array.BYTES_PER_ELEMENT));
  items.push(artifact("volume_binary", "volumetric_binary", "cubic-constant.f64", "call_volume", volumeBinary, "application/vnd.mdi.volumetric+float64"));
  items.push(artifact("metrics", "metrics_json", "Generic Metrics", "call_metrics", Buffer.from(JSON.stringify({ rows: [{ metric: "count", value: 3, unit: "count" }] }))));
  items.push({ ...artifact("legacy", "metrics_json", "Legacy Result", "call_legacy", Buffer.from("{}")), version: "0" });
  items.push(artifact("html", "report_html", "HTML Report", "call_report", Buffer.from("<script>window.__artifactExecuted=true</script>"), "text/html"));
  return Object.freeze(items);
}

function artifact(id, type, name, toolCallId, bytes, contentType = "application/json") {
  return Object.freeze({ id: `artifact_${id}`, artifactId: `artifact_${id}`, projectId: "project_local", datasetId: "dataset_demo", jobId: "job_gallery", toolCallId, type, version: "1", name, sizeBytes: bytes.length, contentType, sha256: createHash("sha256").update(bytes).digest("hex"), contentHash: createHash("sha256").update(bytes).digest("hex"), createdAt: "2026-08-01T00:00:00Z", metadata: { projectId: "project_local", stepId: `step_${id}` }, bytes });
}

function snapshot(artifacts) {
  const workspaceId = "workspace_gallery", jobId = "job_gallery";
  const kinds = ["OVERVIEW", "DATA", "PLAN", "EXECUTION", "SCIENTIFIC_RESULT", "FINDINGS", "EVIDENCE", "PROVENANCE", "REPORT"];
  const panels = kinds.map((kind, ordinal) => panel(workspaceId, jobId, kind, ordinal, artifacts[0]));
  const workspace = { schemaVersion: "1.0", workspaceId, projectId: "project_local", sourceJobId: jobId, sourceReferenceHash: HASH, datasetId: "dataset_demo", datasetVersion: "v1", profileId: "profile_demo", profileSemanticHash: HASH, intentId: "intent_demo", intentSemanticHash: HASH, planId: "plan_demo", planHash: HASH, planSchemaVersion: "0.2", title: "Typed Artifact Gallery", activePanelId: "panel_scientific_result", pinnedSelection: null, durableMetadata: { tags: [], note: null }, panelIds: panels.map((item) => item.panelId), currentLayoutRevision: 1, revision: 1, projectedStatus: "COMPLETE", historicalProjection: false, readOnly: false, warnings: [], diagnostics: [], artifactCount: artifacts.length, toolCallCount: 9, interpretationCount: 1, reportCount: 0, recipeCount: 0, createdByKind: "USER", createdBy: "browser_fixture", createdAt: "2026-08-01T00:00:00Z", updatedAt: "2026-08-01T00:00:00Z", executionAuthorized: false, scientificAuthority: false };
  return { workspace, panels, currentLayoutRevision: { schemaVersion: "1.0", workspaceId, revision: 1, layout: { schemaVersion: "1.0", activePanelId: "panel_scientific_result", panelOrder: panels.map((item) => item.panelId), visiblePanelIds: panels.map((item) => item.panelId), panelLayouts: panels.map((item) => ({ panelId: item.panelId, ...item.layout })), durableMetadata: { tags: [], note: null } }, selection: null, semanticHash: HASH, createdBy: "browser_fixture", createdAt: "2026-08-01T00:00:00Z" }, sourceSummary: { jobStatus: "completed", analysisPlanSchemaVersion: "0.2", dependencyOutcome: "PARTIAL_RESULTS", artifactCount: artifacts.length, toolCallCount: 9, interpretationCount: 1, reportCount: 0, recipeCount: 0, metadataOnly: true }, projectionHash: HASH };
}

function panel(workspaceId, jobId, kind, ordinal, artifact) {
  const labels = { OVERVIEW: "Analysis overview", DATA: "Dataset context", PLAN: "Analysis plan", EXECUTION: "Execution timeline", SCIENTIFIC_RESULT: "Scientific results", FINDINGS: "Grounded findings", EVIDENCE: "Scientific evidence", PROVENANCE: "Provenance", REPORT: "Report" };
  const renderer = { OVERVIEW: "workspace.overview/1.0", DATA: "workspace.data/1.0", PLAN: "workspace.plan/1.0", EXECUTION: "workspace.execution/1.0", SCIENTIFIC_RESULT: "workspace.artifact-metadata/1.0", FINDINGS: "workspace.findings/1.0", EVIDENCE: "workspace.evidence/1.0", PROVENANCE: "workspace.provenance/1.0", REPORT: "workspace.report/1.0" };
  const declarations = {
    OVERVIEW: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
    DATA: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME"], []],
    PLAN: [[], []], EXECUTION: [["ARTIFACT"], []],
    SCIENTIFIC_RESULT: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT"], ["DATASET_SAMPLE", "MATERIAL_OBJECT", "ARTIFACT"]],
    FINDINGS: [["PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
    EVIDENCE: [["PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
    PROVENANCE: [["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
    REPORT: [["ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], []],
  };
  const jobRef = { kind: "JOB", sourceId: jobId, sourceHash: HASH, contract: null, contractVersion: null, mediaType: null, projectId: "project_local", jobId, toolCallId: null, stepId: null };
  const artifactRef = { kind: "ARTIFACT", sourceId: artifact.artifactId, sourceHash: artifact.sha256, contract: artifact.type, contractVersion: artifact.version, mediaType: artifact.contentType, projectId: "project_local", jobId, toolCallId: artifact.toolCallId, stepId: artifact.metadata.stepId };
  const interpretationRef = { kind: "INTERPRETATION", sourceId: "interpretation_gallery", sourceHash: HASH, contract: "grounded_interpretation", contractVersion: "1.0", mediaType: null, projectId: "project_local", jobId, toolCallId: null, stepId: null };
  const bundleRef = { kind: "EVIDENCE_BUNDLE", sourceId: "bundle_gallery", sourceHash: HASH, contract: "scientific_evidence_bundle", contractVersion: "1.0", mediaType: null, projectId: "project_local", jobId, toolCallId: null, stepId: null };
  const sourceRefs = kind === "SCIENTIFIC_RESULT" ? [artifactRef] : kind === "FINDINGS" ? [interpretationRef, artifactRef] : kind === "EVIDENCE" ? [bundleRef, artifactRef] : [jobRef];
  return { schemaVersion: "1.0", panelId: `panel_${kind.toLowerCase()}`, workspaceId, panelKind: kind, title: labels[kind], ordinal, visible: true, sourceRefs, sourceReferenceHash: HASH, rendererContract: renderer[kind], state: kind === "SCIENTIFIC_RESULT" ? "PARTIAL" : "PRODUCED", acceptedSelectionKinds: declarations[kind][0], emittedSelectionKinds: declarations[kind][1], evidenceRefs: kind === "EVIDENCE" ? ["evidence_dataset_count"] : [], provenanceRefs: kind === "FINDINGS" || kind === "EVIDENCE" ? [artifact.artifactId] : [jobId], capabilityRequirement: null, layout: { region: "PRIMARY", order: ordinal, width: 1, height: 1, collapsed: false }, mobilePresentationMode: "FULL_WIDTH", accessibleName: labels[kind], unsupportedReason: null, panelStateHash: HASH, contractProvenance: "phase10m4.renderer_registry.v1" };
}

function interpretationListFixture() {
  const claim = { schemaVersion: "1.0", claimId: "claim_dataset_count", claimType: "OBSERVATION", subjectEvidenceIds: ["evidence_dataset_count"], supportingEvidenceIds: ["evidence_dataset_count"], limitingEvidenceIds: [], contradictingEvidenceIds: [], semanticPredicate: "HAS_COUNT", qualifiers: [], renderedText: "The persisted dataset result reports a bounded sample count.", scope: "artifact_dataset", confidenceClass: "DIRECT", groundingStatus: "GROUNDED", displayOrder: 0 };
  const interpretation = { schemaVersion: "1.0", interpretationId: "interpretation_gallery", interpretationHash: HASH, sourceBundleId: "bundle_gallery", sourceBundleHash: HASH, sourceJobId: "job_gallery", sourcePlanId: "plan_demo", sourcePlanHash: HASH, sourceGraphHash: HASH, mode: "DETERMINISTIC", provider: "deterministic", providerVersion: "1.0", claims: [claim], globalWarnings: [], globalLimitations: [], recommendations: [], completeness: "COMPLETE", partialResultState: false, repairCount: 0, validationOutcome: "VALID", executionRecordId: "execution_gallery" };
  return { jobId: "job_gallery", interpretations: [interpretation], runs: [], count: 1, runCount: 0 };
}

function interpretationEvidenceFixture(artifact) {
  return { interpretationId: "interpretation_gallery", bundleId: "bundle_gallery", bundleHash: HASH, sourceArtifactIds: [artifact.artifactId], bundleWarnings: [], bundleLimitations: [], evidenceItems: [{ schemaVersion: "1.0", evidenceItemId: "evidence_dataset_count", semanticRole: "dataset.sample_count", evidenceKind: "COUNT", subjectId: artifact.artifactId, displayValue: "3", unit: "count", sourceArtifactId: artifact.artifactId, sourceArtifactChecksum: artifact.sha256, artifactContract: artifact.type, artifactContractVersion: artifact.version, sourceToolId: "dataset.materials_explorer", sourceToolVersion: "1.0", fieldLocator: { fieldId: "summary.sample_count" }, warnings: [], limitations: [] }] };
}

function validateFixtures(artifacts) { if (artifacts.length < 16 || new Set(artifacts.map((item) => item.id)).size !== artifacts.length || artifacts.some((item) => item.sizeBytes !== item.bytes.length)) throw new Error("M4 artifact fixtures are invalid"); }
function browserLaunchOptions(name) {
  return name === "chromium"
    ? { headless: true, args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] }
    : { headless: true };
}
function attachAudit(page) { const audit = { consoleErrors: [], pageErrors: [], failedResponses: [], externalRequests: [] }; page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); }); page.on("pageerror", (error) => audit.pageErrors.push(error.message)); page.on("response", (response) => { if (response.status() >= 400) audit.failedResponses.push(`${response.status()} ${response.url()}`); }); page.on("request", (request) => { const url = new URL(request.url()); if (!["127.0.0.1", "localhost"].includes(url.hostname)) audit.externalRequests.push(request.url()); }); return audit; }
function corsHeaders() { return { "access-control-allow-origin": ORIGIN, "access-control-allow-methods": "GET,OPTIONS", "access-control-allow-headers": "content-type", "access-control-expose-headers": "content-length,x-content-length-validated,x-content-type-options" }; }
function jsonResponse(value, status = 200) { return { status, contentType: "application/json", headers: corsHeaders(), body: JSON.stringify(value) }; }
async function writeJson(relative, value) { const target = path.join(OUTPUT, relative); await mkdir(path.dirname(target), { recursive: true }); await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function argumentValue(name) { const index = process.argv.indexOf(name); return index >= 0 ? process.argv[index + 1] : null; }
function startServer() { const command = process.platform === "win32" ? "cmd.exe" : "npm"; const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]; return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: API_ORIGIN }, stdio: "ignore" }); }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const deadline = Date.now() + 90000; while (Date.now() < deadline) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("M4 Workspace app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; spawnSync("powershell.exe", ["-NoProfile", "-Command", `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue;if($c){$c|%{Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}`], { stdio: "ignore" }); }
async function stopServer(server) { if (!server) return; if (process.platform === "win32") { spawnSync("taskkill", ["/pid", String(server.pid), "/T", "/F"], { stdio: "ignore" }); await stopPort(); } else server.kill("SIGTERM"); }

main().catch((error) => { console.error(error); process.exitCode = 1; });
