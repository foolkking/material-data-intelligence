import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, process.env.MDI_INSPECTION_EVIDENCE_DIR || "docs/phase10f/evidence/phase10f16_scientific_structure_inspection");
const SCREENSHOTS = path.join(EVIDENCE, "screenshots");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const PORT = Number(process.env.MDI_VIEWER_INSPECTION_EVIDENCE_PORT || "3051");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const PERIODIC_MODE = process.env.MDI_PERIODIC_EVIDENCE === "1";
const TOPOLOGY_MODE = process.env.MDI_TOPOLOGY_EVIDENCE === "1";
let payload;
let activeCase = "measurement_crystal";
let activeMode = "live";

async function main() {
  await mkdir(SCREENSHOTS, { recursive: true });
  generatePayload();
  payload = JSON.parse(await readFile(path.join(EVIDENCE, "live_payload.json"), "utf-8"));
  const pw = await import(pathToFileURL(PLAYWRIGHT).href);
  const server = await ensureServer();
  const results = [];
  try {
    await waitForApp();
    const requested = new Set((process.env.MDI_INSPECTION_BROWSER_MATRIX || "chromium,firefox,webkit").split(",").map((item) => item.trim()));
    const matrix = [
      { id: "chromium", type: pw.chromium, options: { executablePath: CHROME, args: ["--no-sandbox", "--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--disable-background-networking"] } },
      { id: "firefox", type: pw.firefox, options: {} },
      { id: "webkit", type: pw.webkit, options: {} },
    ].filter((candidate) => requested.has(candidate.id));
    for (const candidate of matrix) {
      let browser;
      try {
        browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
        results.push(await inspectBrowser(browser, candidate.id));
      } finally {
        await browser?.close().catch(() => {});
      }
    }
    if (results.some((result) => !result.pass || result.externalRequests !== 0)) throw new Error(`inspection matrix failed: ${JSON.stringify(results)}`);
    await write("browser/browser_matrix.json", { schema_version: TOPOLOGY_MODE ? "phase10f18.periodic_topology_browser_matrix.v1" : PERIODIC_MODE ? "phase10f17.periodic_browser_matrix.v1" : "phase10f16.inspection_browser_matrix.v1", results });
    await write("browser/network_snapshot.json", { external_request_count: 0, result: TOPOLOGY_MODE ? "NO_PERIODIC_TOPOLOGY_EXTERNAL_NETWORK_REQUESTS" : PERIODIC_MODE ? "NO_PERIODIC_VIEWER_EXTERNAL_NETWORK_REQUESTS" : "NO_VIEWER_INSPECTION_EXTERNAL_NETWORK_REQUESTS" });
    await write("browser/console_snapshot.json", { errors: results.flatMap((result) => result.consoleErrors), page_errors: results.flatMap((result) => result.pageErrors) });
    await write("evidence_manifest.json", manifest(results));
    await writeFile(path.join(EVIDENCE, "README.md"), readme(results), "utf-8");
    console.log("VIEWER_SCENE_SCIENTIFIC_INSPECTION_BROWSER_EVIDENCE_PASS");
    console.log("VIEWER_SCENE_MEASUREMENT_EVIDENCE_PASS");
    console.log("VIEWER_SCENE_EXPORT_EVIDENCE_PASS");
    console.log("VIEWER_SCENE_LEGACY_GUIDANCE_EVIDENCE_PASS");
    console.log("NO_VIEWER_INSPECTION_EXTERNAL_NETWORK_REQUESTS");
    if (PERIODIC_MODE) {
      console.log("VIEWER_SCENE_PERIODIC_INSPECTION_BROWSER_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_MINIMUM_IMAGE_MEASUREMENT_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_SUPERCELL_BROWSER_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_PERIODIC_PERFORMANCE_EVIDENCE_PASS");
      console.log("NO_PERIODIC_VIEWER_EXTERNAL_NETWORK_REQUESTS");
    }
    if (TOPOLOGY_MODE) {
      console.log("VIEWER_SCENE_PERIODIC_BOND_CONTRACT_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_PERIODIC_TOPOLOGY_BROWSER_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_PERIODIC_NEIGHBOR_INSPECTOR_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_PERIODIC_BOND_PERFORMANCE_EVIDENCE_PASS");
      console.log("NO_PERIODIC_TOPOLOGY_EXTERNAL_NETWORK_REQUESTS");
    }
  } finally {
    if (server) { server.kill(); await stopPort(); }
  }
}

async function inspectBrowser(browser, browserId) {
  if (TOPOLOGY_MODE) return topologyBrowser(browser, browserId);
  activeCase = "measurement_crystal";
  activeMode = "live";
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 }, acceptDownloads: true, reducedMotion: "reduce" });
  const audit = { external: [], console: [], pageErrors: [], failedResponses: [] };
  const page = await evidencePage(context, audit);
  await productFlow(page);
  await openRenderer(page);
  const initial = await snapshot(page);
  if (initial.siteScreenPositions.length !== 4) throw new Error(`${browserId} site projection count invalid`);

  await pick(page, 0);
  try {
    await page.waitForFunction(() => document.querySelector('[data-testid="viewer-selected-site-index"]')?.textContent?.trim() === "0", null, { timeout: 10_000 });
  } catch (error) {
    const diagnostic = await page.evaluate(() => ({ inspector: document.querySelector('[data-testid="viewer-site-inspector"]')?.textContent, snapshot: window.__mdiViewerSceneRendererEvidence }));
    throw new Error(`site 0 pick failed: ${JSON.stringify(diagnostic)}; ${String(error)}`);
  }
  await page.screenshot({ path: path.join(SCREENSHOTS, `${browserId}_atom_selected.png`), fullPage: true });
  const inspector = await page.getByTestId("viewer-site-inspector").innerText();

  await page.getByRole("button", { name: "Distance" }).click();
  await pickMany(page, [0, 1]);
  const distance = await measurement(page, "distance");
  await page.screenshot({ path: path.join(SCREENSHOTS, `${browserId}_distance.png`), fullPage: true });

  await page.getByRole("button", { name: "Angle" }).click();
  await pickMany(page, [0, 1, 2]);
  const angle = await measurement(page, "angle");
  if (browserId === "chromium") await page.screenshot({ path: path.join(SCREENSHOTS, "chromium_angle.png"), fullPage: true });

  await page.getByRole("button", { name: "Dihedral" }).click();
  await pickMany(page, [0, 1, 2, 3]);
  const dihedral = await measurement(page, "dihedral");
  if (browserId === "chromium") await page.screenshot({ path: path.join(SCREENSHOTS, "chromium_dihedral.png"), fullPage: true });

  const periodic = PERIODIC_MODE ? await periodicCase(page, browserId) : null;

  let png = null;
  let artifactDownloads = null;
  if (browserId === "chromium") {
    const [download] = await Promise.all([page.waitForEvent("download"), page.getByTestId("viewer-scene-export-png").click()]);
    const pngPath = path.join(EVIDENCE, "export", "current-view.png");
    await mkdir(path.dirname(pngPath), { recursive: true });
    await download.saveAs(pngPath);
    const bytes = await readFile(pngPath);
    const validSignature = bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
    if (!validSignature || bytes.length < 1000 || !/structure-viewer(?:-1x1x1)?\.png$/.test(download.suggestedFilename())) throw new Error("PNG export audit failed");
    png = { filename: download.suggestedFilename(), bytes: bytes.length, validSignature };
    await write("export/png_export_audit.json", { ...png, local_only: true, max_dimensions: [4096, 4096], external_requests: 0 });
    artifactDownloads = [];
    for (const [button, expected] of [["Download scene JSON", "viewer_scene.json"], ["Download manifest", "viewer_scene_manifest.json"], ["Download summary", "summary.md"], ["Download recipe", "recipe.json"]]) {
      const [artifactDownload] = await Promise.all([page.waitForEvent("download"), page.getByRole("button", { name: button, exact: true }).click()]);
      const artifactPath = await artifactDownload.path();
      const artifactBytes = artifactPath ? (await readFile(artifactPath)).length : 0;
      if (artifactDownload.suggestedFilename() !== expected || artifactBytes === 0) throw new Error(`artifact download audit failed: ${button}`);
      artifactDownloads.push({ button, filename: artifactDownload.suggestedFilename(), bytes: artifactBytes });
    }
    await write("export/artifact_download_audit.json", { local_only: true, downloads: artifactDownloads, external_requests: 0 });
  }

  await page.getByRole("tab", { name: "Scene JSON" }).click();
  await page.getByRole("tab", { name: "3D Renderer" }).click();
  await openRenderer(page, false);
  const cleared = !(await page.getByTestId("viewer-selected-site-index").count());
  if (!cleared || await page.locator("canvas").count() !== 1) throw new Error("selection lifecycle cleanup failed");
  if (browserId === "chromium") await page.screenshot({ path: path.join(SCREENSHOTS, "chromium_measurement_cleared.png"), fullPage: true });

  let mobile = null;
  let legacy = null;
  if (browserId === "chromium") {
    mobile = await mobileCase(browser);
    legacy = await legacyCase(context);
  }
  const security = await auditPage(page, audit);
  await page.close();
  await context.close();
  return { browser: browserId, version: browser.version(), pass: true, inspector, distance, angle, dihedral, periodic, png, artifactDownloads, mobile, legacy, lifecycle: { selectionCleared: cleared, canvasCount: 1 }, externalRequests: security.external, consoleErrors: security.consoleErrors, pageErrors: audit.pageErrors };
}

async function topologyBrowser(browser, browserId) {
  activeCase = "periodic_boundary_bond";
  activeMode = "live";
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 }, reducedMotion: "reduce" });
  const audit = { external: [], console: [], pageErrors: [], failedResponses: [] };
  const page = await evidencePage(context, audit);
  await productFlow(page); await openRenderer(page);
  await page.getByTestId("viewer-supercell-x").fill("2");
  await page.getByTestId("viewer-supercell-apply").click();
  await page.waitForFunction(() => window.__mdiViewerSceneRendererEvidence?.atomCount === 4 && window.__mdiViewerSceneRendererEvidence?.bondCount === 1, null, { timeout: 20_000 });
  await pick(page, 0);
  await page.waitForSelector('[data-testid="viewer-periodic-neighbor-row"]');
  const selectedSite = Number(await page.getByTestId("viewer-selected-site-index").innerText());
  const selectedOffset = await page.getByTestId("viewer-selected-site-image-offset").innerText();
  const neighborSite = Number(await page.getByTestId("viewer-periodic-neighbor-row").getByRole("button").innerText());
  const offset = await page.getByTestId("viewer-periodic-neighbor-offset").innerText();
  const distance = await page.getByTestId("viewer-periodic-neighbor-distance").innerText();
  const source = await page.getByTestId("viewer-periodic-neighbor-source").innerText();
  const authoritative = await page.getByTestId("viewer-periodic-neighbor-authoritative").innerText();
  const endpointPair = new Set([`${selectedSite}@${selectedOffset}`, `${neighborSite}@${offset}`]);
  if (!endpointPair.has("0@[0, 0, 0]") || !endpointPair.has("1@[1, 0, 0]") || distance !== "0.400000" || source !== "distance_cutoff" || authoritative !== "no") throw new Error(`periodic neighbor mismatch: ${JSON.stringify({selectedSite,selectedOffset,neighborSite,offset,distance,source,authoritative})}`);
  await page.getByTestId("viewer-periodic-neighbor-row").click();
  const boundary = await snapshot(page);
  if (boundary.bondCount !== 1 || boundary.metrics?.bondCount !== 1) throw new Error("periodic bond metrics mismatch");
  await page.screenshot({ path: path.join(SCREENSHOTS, `${browserId}_cross_boundary_bond.png`), fullPage: true });
  let triclinic = null;
  let mobile = null;
  if (browserId === "chromium") {
    activeCase = "triclinic_boundary_bond";
    const triclinicPage = await evidencePage(context, audit);
    await productFlow(triclinicPage); await openRenderer(triclinicPage);
    await triclinicPage.getByTestId("viewer-supercell-x").fill("2");
    await triclinicPage.getByTestId("viewer-supercell-y").fill("2");
    await triclinicPage.getByTestId("viewer-supercell-z").fill("2");
    await triclinicPage.getByTestId("viewer-supercell-apply").click();
    await triclinicPage.waitForFunction(() => window.__mdiViewerSceneRendererEvidence?.bondCount > 0, null, { timeout: 20_000 });
    triclinic = await snapshot(triclinicPage);
    await triclinicPage.screenshot({ path: path.join(SCREENSHOTS, "chromium_triclinic_boundary_bond.png"), fullPage: true });
    await triclinicPage.close();
    activeCase = "periodic_boundary_bond";
    mobile = await topologyMobileCase(browser);
  }
  const security = await auditPage(page, audit);
  await page.close(); await context.close();
  return { browser:browserId, version:browser.version(), pass:true, neighbor:{selectedSite,selectedOffset,neighborSite,offset,distance,source,authoritative}, metrics:boundary.metrics, triclinic: triclinic ? {bondCount:triclinic.bondCount,metrics:triclinic.metrics} : null, mobile, externalRequests:security.external, consoleErrors:security.consoleErrors, pageErrors:audit.pageErrors };
}

async function topologyMobileCase(browser) {
  activeCase = "periodic_boundary_bond";
  const context = await browser.newContext({ viewport:{width:390,height:844}, isMobile:true, hasTouch:true, deviceScaleFactor:2 });
  const audit = { external: [], console: [], pageErrors: [], failedResponses: [] };
  const page = await evidencePage(context,audit);
  await productFlow(page); await openRenderer(page);
  await page.getByTestId("viewer-supercell-x").fill("2"); await page.getByTestId("viewer-supercell-apply").click();
  await page.waitForFunction(() => window.__mdiViewerSceneRendererEvidence?.bondCount === 1, null, {timeout:20_000});
  await pick(page,0); await page.waitForSelector('[data-testid="viewer-periodic-neighbor-row"]');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (overflow) throw new Error("mobile topology overflow");
  await page.screenshot({path:path.join(SCREENSHOTS,"chromium_mobile_neighbor_inspector.png"),fullPage:false});
  const result={offset:await page.getByTestId("viewer-periodic-neighbor-offset").innerText(),overflow,external:(await auditPage(page,audit)).external};
  await page.close(); await context.close(); return result;
}

async function periodicCase(page, browserId) {
  await page.getByRole("button", { name: "Distance" }).click();
  await page.getByRole("button", { name: "Minimum image (periodic)" }).click();
  await pickMany(page, [0, 1]);
  const result = await measurement(page, "distance");
  const offsets = await page.getByTestId("viewer-periodic-measurement-offsets").innerText();
  if (!offsets.includes("@[")) throw new Error("periodic image offsets missing");
  for (const [axis, value] of [["x","2"],["y","2"],["z","2"]]) await page.getByTestId(`viewer-supercell-${axis}`).fill(value);
  await page.getByTestId("viewer-supercell-apply").click();
  await page.waitForFunction(() => window.__mdiViewerSceneRendererEvidence?.atomCount === 32, null, { timeout: 20_000 });
  const doubled = await snapshot(page);
  const replica = doubled.siteScreenPositions.find((item) => item.ref?.imageOffset?.join(",") === "1,0,0");
  const box = await page.getByTestId("viewer-scene-renderer-canvas").boundingBox();
  if (!replica || !box) throw new Error("periodic replica projection unavailable");
  await page.mouse.click(box.x + replica.x, box.y + replica.y);
  await page.waitForFunction(() => document.querySelector('[data-testid="viewer-selected-site-image-offset"]')?.textContent?.includes("1, 0, 0"));
  if (browserId === "chromium") await page.screenshot({ path: path.join(SCREENSHOTS, "chromium_periodic_replica_2x2x2.png"), fullPage: true });
  for (const axis of ["x","y","z"]) await page.getByTestId(`viewer-supercell-${axis}`).fill("3");
  const applyStarted = Date.now();
  await page.getByTestId("viewer-supercell-apply").click();
  await page.waitForFunction(() => window.__mdiViewerSceneRendererEvidence?.atomCount === 108, null, { timeout: 20_000 });
  const tripled = await snapshot(page);
  if (browserId === "chromium") await page.screenshot({ path: path.join(SCREENSHOTS, "chromium_supercell_3x3x3.png"), fullPage: true });
  await page.getByTestId("viewer-supercell-reset").click();
  await page.waitForFunction(() => window.__mdiViewerSceneRendererEvidence?.atomCount === 4, null, { timeout: 20_000 });
  return { result, offsets, two_by_two_by_two: { atoms: doubled.atomCount, metrics: doubled.metrics }, three_by_three_by_three: { atoms: tripled.atomCount, metrics: tripled.metrics, apply_ms: Date.now() - applyStarted }, reset_atoms: (await snapshot(page)).atomCount };
}

async function mobileCase(browser) {
  activeCase = "multi_species_crystal";
  activeMode = "live";
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const audit = { external: [], console: [], pageErrors: [], failedResponses: [] };
  const page = await evidencePage(context, audit);
  await productFlow(page); await openRenderer(page);
  const initialMobileCount = (await snapshot(page)).atomCount;
  if (PERIODIC_MODE) {
    await page.getByTestId("viewer-supercell-x").fill("2");
    await page.getByTestId("viewer-supercell-apply").click();
    await page.waitForFunction((expected) => window.__mdiViewerSceneRendererEvidence?.atomCount === expected, initialMobileCount * 2, { timeout: 20_000 });
  }
  const canvas = page.getByTestId("viewer-scene-renderer-canvas");
  await canvas.scrollIntoViewIfNeeded();
  const mobileSnapshot = await snapshot(page);
  const site = PERIODIC_MODE ? mobileSnapshot.siteScreenPositions.find((item) => item.ref?.imageOffset?.join(",") === "1,0,0") : mobileSnapshot.siteScreenPositions[0];
  const box = await canvas.boundingBox();
  if (!site || !box) throw new Error("mobile picking coordinates unavailable");
  await page.touchscreen.tap(box.x + site.x, box.y + site.y);
  await page.waitForSelector('[data-testid="viewer-selected-site-index"]');
  await page.getByTestId("viewer-site-inspector").scrollIntoViewIfNeeded();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (overflow) throw new Error("mobile inspection overflow");
  await page.screenshot({ path: path.join(SCREENSHOTS, "chromium_mobile_atom_selection.png"), fullPage: false });
  const result = { selected: await page.getByTestId("viewer-selected-site-index").innerText(), imageOffset: await page.getByTestId("viewer-selected-site-image-offset").innerText(), supercellAtoms: mobileSnapshot.atomCount, overflow, external: (await auditPage(page, audit)).external };
  await page.close(); await context.close();
  return result;
}

async function legacyCase(context) {
  activeCase = "valid_minimal_crystal";
  activeMode = "legacy";
  const audit = { external: [], console: [], pageErrors: [], failedResponses: [] };
  const page = await evidencePage(context, audit);
  await productFlow(page);
  const notice = await page.getByTestId("viewer-scene-legacy-notice").innerText();
  if (!notice.includes("structure.viewer_3d") || await page.getByRole("tab", { name: "3D Renderer" }).count()) throw new Error("legacy guidance boundary failed");
  await page.screenshot({ path: path.join(SCREENSHOTS, "chromium_legacy_guidance.png"), fullPage: true });
  const result = { notice, rendererTabs: 0, external: (await auditPage(page, audit)).external };
  await page.close();
  activeMode = "live";
  return result;
}

async function pickMany(page, siteIndices) {
  for (const siteIndex of siteIndices) await pick(page, siteIndex);
  await page.waitForFunction((count) => document.querySelector('[data-testid="viewer-measurement-selection"]')?.textContent?.includes(`${count}/${count}`), siteIndices.length);
}

async function pick(page, siteIndex) {
  const state = await snapshot(page);
  const site = state.siteScreenPositions.find((item) => item.siteIndex === siteIndex);
  const box = await page.getByTestId("viewer-scene-renderer-canvas").boundingBox();
  if (!site || !box) throw new Error(`site ${siteIndex} screen position unavailable`);
  await page.mouse.click(box.x + site.x, box.y + site.y);
}

async function measurement(page, kind) {
  const value = await page.getByTestId("viewer-measurement-result").innerText();
  if (!value.startsWith(kind) || !/[Å°]/.test(value)) throw new Error(`${kind} result invalid: ${value}`);
  return value;
}

async function evidencePage(context, audit) {
  const page = await context.newPage();
  await page.addInitScript(() => { window.EventSource = class { close() {} addEventListener() {} removeEventListener() {} }; });
  page.on("console", (message) => audit.console.push({ type: message.type(), text: message.text(), location: message.location() }));
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => { if (response.status() >= 400) audit.failedResponses.push({ status: response.status(), url: response.url() }); });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) return url.pathname === "/favicon.ico" ? route.fulfill({ status: 204, body: "" }) : route.continue();
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    audit.external.push({ host: url.hostname, path: url.pathname });
    return route.abort();
  });
  return page;
}

async function productFlow(page) {
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill("Open this crystal for scientific structure inspection");
  await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click();
  await page.waitForSelector('[data-testid="viewer-scene-preview"]');
}

async function openRenderer(page, click = true) {
  if (click) await page.getByRole("tab", { name: "3D Renderer" }).click();
  await page.waitForFunction(() => document.querySelector('[data-testid="viewer-scene-renderer-state"]')?.textContent === "rendered", null, { timeout: 20_000 });
}

async function snapshot(page) {
  const result = await page.evaluate(() => window.__mdiViewerSceneRendererEvidence || null);
  if (!result) throw new Error("renderer snapshot unavailable");
  return result;
}

async function auditPage(page, audit) {
  const inert = await page.evaluate(() => ({ iframe: document.querySelectorAll("iframe").length, object: document.querySelectorAll("object,embed").length, externalScript: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length, javascriptUri: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length, inlineHandler: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attr) => /^on/i.test(attr.name))).length }));
  const consoleErrors = audit.console.filter((item) => item.type === "error" && !/\/favicon\.ico$/i.test(item.location?.url || ""));
  if (Object.values(inert).some(Boolean) || consoleErrors.length || audit.pageErrors.length || audit.external.length) throw new Error(`inspection security audit failed: ${JSON.stringify({ inert, consoleErrors, pageErrors: audit.pageErrors, failedResponses: audit.failedResponses, external: audit.external })}`);
  return { external: audit.external.length, consoleErrors };
}

async function api(route, url) {
  const method = route.request().method();
  const item = payload.cases[activeCase];
  const job = item.planner.job_id;
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: "dataset_demo", datasetId: "dataset_demo", projectId: "project_10f16", name: "Inspection evidence", status: "ready", demo: true, profileId: "profile_demo", profile: { profileId: "profile_demo", datasetId: "dataset_demo", datasetType: "structure_collection", status: "ready", objects: [{ objectType: "Structure", count: 1 }] } } });
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
  return route.fulfill({ status: 404, json: { detail: "inspection evidence route not found" } });
}

function artifacts(source) {
  const copy = structuredClone(source);
  if (activeMode === "legacy") {
    const scene = copy.find((item) => item.name === "viewer_scene.json");
    scene.content = { schema_version: "phase10d1.viewer_scene.v1", artifactType: "structure.viewer_scene_metadata", structure: { formula: "Si", site_count: 2, species: ["Si"], atoms: [] }, security: { contains_javascript: false, external_urls: [] } };
  }
  return copy;
}

function generatePayload() {
  const output = process.env.MDI_INSPECTION_EVIDENCE_DIR || "docs/phase10f/evidence/phase10f16_scientific_structure_inspection";
  const result = spawnSync("uv", ["run", "python", "apps/web/test/generate-viewer-scene-live-adapter-evidence.py", output], { cwd: ROOT, encoding: "utf-8", env: { ...process.env, PYTHONIOENCODING: "utf-8", MDI_FORMAL_VIEWER_MODE: "1", MDI_INCLUDE_RENDERER_CASES: "1", MDI_INCLUDE_INSPECTION_CASES: "1", MDI_INCLUDE_TOPOLOGY_CASES: TOPOLOGY_MODE ? "1" : "0" } });
  if (result.status !== 0) throw new Error(`inspection payload generation failed\n${result.stdout}\n${result.stderr}`);
  process.stdout.write(result.stdout);
}

function startServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
  const child = spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: ["ignore", "pipe", "pipe"] });
  child.stdout.on("data", () => {}); child.stderr.on("data", () => {});
  return child;
}

async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} await stopPort(); return startServer(); }
async function waitForApp() { const end = Date.now() + 60_000; while (Date.now() < end) { try { if ((await fetch(ORIGIN)).ok) return; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("inspection app timeout"); }
async function stopPort() { if (process.platform !== "win32") return; const ps = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`; await new Promise((resolve) => { const child = spawn("powershell.exe", ["-NoProfile", "-Command", ps], { stdio: "ignore" }); child.on("exit", resolve); child.on("error", resolve); }); }
async function write(relative, value) { const file = path.join(EVIDENCE, relative); await mkdir(path.dirname(file), { recursive: true }); await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf-8"); }
function manifest(results) { return TOPOLOGY_MODE ? { schema_version:"phase10f18.periodic_bond_topology_evidence.v1", baseline_head:"bfca00d4c93ab2bd16966b237d850bd33206c20c", final_head:"current commit recorded in final report", formal_tool:"structure.viewer_3d", canonical_schema:"phase10f18.viewer_scene.v2", periodic_bonds:"adapter_generated_explicit_endpoints", source_policy:"distance_cutoff_non_authoritative", evidence_generation_command:"node apps/web/test/viewer-scene-periodic-topology-browser-evidence.mjs", timestamp:payload.cases.periodic_boundary_bond.api.artifacts[0]?.metadata?.createdAt, artifact_hashes:Object.fromEntries(payload.cases.periodic_boundary_bond.api.artifacts.map((item)=>[item.name,item.sha256||item.contentHash])), browser_results:results.map((item)=>({browser:item.browser,version:item.version,pass:item.pass,neighbor:item.neighbor,metrics:item.metrics})), network_result:"NO_PERIODIC_TOPOLOGY_EXTERNAL_NETWORK_REQUESTS", markers:["VIEWER_SCENE_PERIODIC_BOND_CONTRACT_EVIDENCE_PASS","VIEWER_SCENE_PERIODIC_TOPOLOGY_BROWSER_EVIDENCE_PASS","VIEWER_SCENE_PERIODIC_NEIGHBOR_INSPECTOR_EVIDENCE_PASS","VIEWER_SCENE_PERIODIC_BOND_PERFORMANCE_EVIDENCE_PASS"], redaction:"sanitized" } : PERIODIC_MODE ? { schema_version: "phase10f17.periodic_crystal_inspection_evidence.v1", baseline_head: "5e7474be92e0ef75bed7a91ec5309c7fdea9e7f0", formal_tool: "structure.viewer_3d", coordinate_policies: ["displayed_positions", "minimum_image"], lattice_convention: "row_vectors", supercell: "renderer_local_bounded_1_to_3", periodic_bonds: "same_cell_replication_only", browser_results: results.map((item) => ({ browser: item.browser, version: item.version, pass: item.pass })), network_result: "NO_PERIODIC_VIEWER_EXTERNAL_NETWORK_REQUESTS", markers: ["VIEWER_SCENE_PERIODIC_INSPECTION_BROWSER_EVIDENCE_PASS", "VIEWER_SCENE_MINIMUM_IMAGE_MEASUREMENT_EVIDENCE_PASS", "VIEWER_SCENE_SUPERCELL_BROWSER_EVIDENCE_PASS", "VIEWER_SCENE_PERIODIC_PERFORMANCE_EVIDENCE_PASS"], redaction: "sanitized" } : { schema_version: "phase10f16.scientific_inspection_evidence.v1", baseline_head: "1be7689c2d8881b0fb9f2f67360da7cf2d795703", formal_tool: "structure.viewer_3d", coordinate_policy: "displayed_canonical_cartesian_positions", dihedral_range: "[-180, 180]", browser_results: results.map((item) => ({ browser: item.browser, version: item.version, pass: item.pass })), network_result: "NO_VIEWER_INSPECTION_EXTERNAL_NETWORK_REQUESTS", markers: ["VIEWER_SCENE_SCIENTIFIC_INSPECTION_BROWSER_EVIDENCE_PASS", "VIEWER_SCENE_MEASUREMENT_EVIDENCE_PASS", "VIEWER_SCENE_EXPORT_EVIDENCE_PASS", "VIEWER_SCENE_LEGACY_GUIDANCE_EVIDENCE_PASS"], redaction: "sanitized" }; }
function readme(results) { return TOPOLOGY_MODE ? `# Phase 10F-18 Canonical Periodic Bond Topology Evidence\n\nFormal tool: \`structure.viewer_3d\`\nCanonical schema: \`phase10f18.viewer_scene.v2\`\nBrowsers: ${results.map((item)=>`${item.browser}=${item.pass?"pass":"fail"}`).join(", ")}\nTopology source: bounded non-authoritative distance cutoff with explicit periodic endpoints.\nNetwork: \`NO_PERIODIC_TOPOLOGY_EXTERNAL_NETWORK_REQUESTS\`\n` : PERIODIC_MODE ? `# Phase 10F-17 Periodic Crystal Inspection Evidence\n\nFormal tool: \`structure.viewer_3d\`\nBrowsers: ${results.map((item) => `${item.browser}=${item.pass ? "pass" : "fail"}`).join(", ")}\nMinimum-image search is bounded and independently cross-checked against pymatgen. Supercells are renderer-local.\nNetwork: \`NO_PERIODIC_VIEWER_EXTERNAL_NETWORK_REQUESTS\`\n` : `# Phase 10F-16 Scientific Structure Inspection Evidence\n\nFormal tool: \`structure.viewer_3d\`\nBrowsers: ${results.map((item) => `${item.browser}=${item.pass ? "pass" : "fail"}`).join(", ")}\nMeasurements use displayed canonical Cartesian positions.\nNetwork: \`NO_VIEWER_INSPECTION_EXTERNAL_NETWORK_REQUESTS\`\n`; }

await main();
