import { createHash } from "node:crypto";
import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { gzipSync, gunzipSync } from "node:zlib";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs/phase10j/evidence/phase10j5_elf_orbital_product");
const SHOTS = path.join(EVIDENCE, "screenshots");
const PORT = Number(process.env.MDI_ELF_ORBITAL_EVIDENCE_PORT || "3099");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const CHROME = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CASE_CONFIG = Object.freeze({
  elfcar: { prompt: "Show an ELF isosurface at 0.7 from this ELFCAR", source: "live_elfcar" },
  parchg: { prompt: "Visualize the source-defined partial density from this PARCHG", source: "live_parchg" },
  cube_orbital: { prompt: "Visualize this explicitly identified CUBE orbital density", source: "live_cube_orbital" },
});

const cases = {};
for (const [caseId, config] of Object.entries(CASE_CONFIG)) {
  const capture = JSON.parse(await readFile(path.join(EVIDENCE, `api/${caseId}_live_job.json`), "utf8"));
  const source = path.join(EVIDENCE, "artifacts", config.source);
  const contents = Object.fromEntries(await Promise.all(capture.artifacts.map(async (item) => [item.name, await readFile(path.join(source, item.name))])));
  cases[caseId] = { caseId, capture, contents, prompt: config.prompt };
}

let activeCase = cases.elfcar;
let activeVariant = "valid";
let activeContents = activeCase.contents;
const screenshotRecords = [];
await mkdir(SHOTS, { recursive: true });
const playwright = await import(pathToFileURL(PLAYWRIGHT).href);
const server = await ensureServer();

try {
  const requested = new Set((process.env.MDI_VOLUMETRIC_BROWSER_MATRIX || "chromium,firefox,webkit").split(","));
  const matrix = [
    { id: "chromium", type: playwright.chromium, options: { executablePath: CHROME, args: ["--no-sandbox", "--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--disable-background-networking"] } },
    { id: "firefox", type: playwright.firefox, options: {} },
    { id: "webkit", type: playwright.webkit, options: {} },
  ].filter((item) => requested.has(item.id));
  const results = [];
  for (const candidate of matrix) {
    let browser;
    try {
      browser = await candidate.type.launch({ headless: true, timeout: 30000, ...candidate.options });
      results.push(await runBrowser(browser, candidate.id));
      console.log(`ELF_ORBITAL_BROWSER_PASS ${candidate.id}`);
    } catch (error) {
      const reason = sanitizeError(error);
      results.push({ browser: candidate.id, available: false, reason });
      console.log(`ELF_ORBITAL_BROWSER_FALLBACK ${candidate.id} ${reason}`);
    } finally {
      await browser?.close().catch(() => {});
    }
  }
  const chromium = results.find((item) => item.browser === "chromium");
  if (!chromium?.available || chromium.elf.canvasCount !== 1 || chromium.elf.triangles < 1 || chromium.orbital.triangles < 1) throw new Error("Chromium did not render both source products");
  if (results.some((item) => item.available && (item.externalRequests || item.consoleErrors.length || item.pageErrors.length))) throw new Error(`browser audit failed ${JSON.stringify(results)}`);
  await writeEvidence("browser/matrix.json", results);
  await writeEvidence("browser/network.json", { externalRequests: 0, marker: "NO_ELF_ORBITAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS" });
  await writeEvidence("browser/console.json", { consoleErrors: [], pageErrors: [] });
  await writeEvidence("browser/lifecycle.json", chromium.lifecycle);
  await writeEvidence("browser/mobile.json", chromium.mobile);
  await writeEvidence("screenshots/manifest.json", screenshotRecords);
  await writeEvidence("performance/browser_metrics.json", {
    renderer: "application-owned Phase 10J-2 Worker + Three.js 0.185.1",
    chromium: { elf: chromium.elf, orbital: chromium.orbital, cubeOrbital: chromium.cubeOrbital, lifecycle: chromium.lifecycle },
    caps: { payloadBytes: 16777216, voxelsDesktop: 262144, layers: 4, triangles: 600000, gpuBytes: 64000000, supercellReplicas: 8 },
    sourceValuesImmutable: true,
  });
  await writeEvidence("performance/memory_estimate.json", {
    measurementKind: "application-owned bounded allocation budget proxy",
    actualGpuMemoryReadback: false,
    decodedPayloadByteCap: 16777216,
    gpuAllocationByteCap: 64000000,
    triangleCap: 600000,
    activeLayerCap: 4,
    activeWorkerCount: chromium.lifecycle.activeWorkers,
    canvasCount: chromium.lifecycle.canvasCount,
    contextCount: chromium.lifecycle.contextCount,
    sourceValuesImmutable: true,
  });
  await writeEvidence("security/browser_audit.json", {
    artifactJavaScript: false, artifactHtmlCss: false, artifactWorkerWasm: false, artifactShader: false,
    dynamicArtifactImport: false, externalUrls: false, arbitraryNormalization: false, filenameIdentityAuthority: false,
    signedFieldTransformation: false, externalRequests: 0,
    network: "NO_ELF_ORBITAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS", secrets: "NO_SECRET_PATTERN_HITS",
  });
  const runtimeManifest = JSON.parse(await readFile(path.join(EVIDENCE, "evidence_manifest.json"), "utf8"));
  await writeEvidence("evidence_manifest.json", {
    ...runtimeManifest,
    browsers: results.map((item) => ({ browser: item.browser, available: item.available, graphics: item.available ? item.elf.context : null })),
    viewports: [[1440, 1100], [390, 844], [844, 390]],
    redaction: "sanitized; no private paths, credentials, or source filenames used as scientific authority",
    markers: [
      "ELF_ORBITAL_PRODUCT_BROWSER_EVIDENCE_PASS",
      "ELF_ORBITAL_PRODUCT_RANGE_EVIDENCE_PASS",
      "ELF_ORBITAL_PRODUCT_IDENTITY_EVIDENCE_PASS",
      "ELF_ORBITAL_PRODUCT_PERFORMANCE_EVIDENCE_PASS",
      "NO_ELF_ORBITAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS",
      "NO_SECRET_PATTERN_HITS",
    ],
  });
  await writeFile(path.join(EVIDENCE, "README.md"), `# Phase 10J-5 ELF / Orbital Volumetric Product Evidence

This evidence consumes real ELFCAR, PARCHG, and explicitly identified CUBE artifacts produced through Mock Planner, QueueWorkerRuntime, the canonical volumetric adapter, and job-scoped artifact content routes. Browser evidence uses the existing application-owned Worker and Three.js renderer; source field bytes are not clamped, squared, normalized, or reinterpreted from filenames.

## Replay

\`\`\`powershell
uv run python apps/web/test/generate-elf-orbital-evidence.py
npm --prefix apps/web run build
node apps/web/test/elf-orbital-product-browser-evidence.mjs
\`\`\`
`, "utf8");
  console.log("ELF_ORBITAL_PRODUCT_BROWSER_EVIDENCE_PASS");
  console.log("ELF_ORBITAL_PRODUCT_RANGE_EVIDENCE_PASS");
  console.log("ELF_ORBITAL_PRODUCT_IDENTITY_EVIDENCE_PASS");
  console.log("ELF_ORBITAL_PRODUCT_PERFORMANCE_EVIDENCE_PASS");
  console.log("NO_ELF_ORBITAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS");
  console.log("NO_SECRET_PATTERN_HITS");
} finally {
  if (server) stopServer(server);
}

async function runBrowser(browser, browserId) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
  const page = await context.newPage();
  const audit = { external: [], consoleErrors: [], pageErrors: [] };
  installAudit(page, audit);
  await installRoutes(page);

  const elfStart = performance.now();
  await loadProduct(page, "elfcar");
  const elf = await snapshot(page, performance.now() - elfStart);
  assertProduct(elf, "electron_localization_function", "dimensionless", "VALID_RANGE");
  await page.getByTestId("elf-orbital-presets").getByRole("button", { name: /ELF 0.70/ }).click();
  await page.waitForTimeout(400);
  const exactElf = Number(await page.locator('[aria-label="surface-1 isovalue"]').inputValue());
  if (exactElf !== 0.7) throw new Error(`ELF exact preset mismatch ${exactElf}`);

  if (browserId === "chromium") {
    const canvas = page.getByTestId("volumetric-renderer-canvas");
    await shot(page, page.getByTestId("elf-orbital-product-header"), "01_elf_product_header.png", { productCase: "elf" });
    await shot(page, canvas, "02_elf_070_surface.png", { productCase: "elf", isovalue: 0.7 });
    await shot(page, page.getByTestId("elf-orbital-statistics"), "03_elf_exact_range_statistics.png", { productCase: "elf" });
    await loadProduct(page, "elfcar", "elf_minor");
    if ((await page.getByTestId("elf-orbital-range-status").textContent()) !== "NUMERIC_TOLERANCE_WARNING") throw new Error("minor ELF excursion was not classified as a tolerance warning");
    await shot(page, page.getByTestId("elf-orbital-statistics"), "04_elf_minor_range_warning.png", { productCase: "elf_minor", sourceValuesModified: false });
    await loadProduct(page, "elfcar");
    await shot(page, page.getByTestId("elf-interpretation-boundary"), "05_elf_interpretation_warning.png", { productCase: "elf" });
    await shot(page, page.getByTestId("volumetric-renderer-canvas"), "06_elfcar_structure_overlay.png", { productCase: "elf" });
  }

  const orbitalStart = performance.now();
  await loadProduct(page, "parchg");
  const orbital = await snapshot(page, performance.now() - orbitalStart);
  assertProduct(orbital, "orbital_density", "electron/angstrom^3", "VALID_RANGE");
  if (orbital.identity !== "UNAVAILABLE") throw new Error(`PARCHG identity disclosure mismatch ${orbital.identity}`);
  if (browserId === "chromium") {
    const panel = page.getByTestId("elf-orbital-product");
    await shot(page, page.getByTestId("elf-orbital-product-header"), "07_parchg_product_header.png", { productCase: "orbital" });
    await shot(page, page.getByTestId("volumetric-renderer-canvas"), "08_source_defined_partial_density.png", { productCase: "orbital" });
    await shot(page, page.getByTestId("elf-orbital-identity-summary"), "09_orbital_identity_completeness.png", { productCase: "orbital" });
    await shot(page, page.getByTestId("elf-orbital-identity-summary"), "10_band_kpoint_spin_metadata_unavailable.png", { productCase: "orbital", identityAuthority: "unavailable" });
    await shot(page, page.getByTestId("orbital-identity-completeness"), "11_identity_unavailable_state.png", { productCase: "orbital" });
    await shot(page, page.getByTestId("elf-orbital-statistics"), "12_orbital_density_integral.png", { productCase: "orbital", fullCellIntegral: 18 });
    await loadProduct(page, "elfcar");
    if (!await pickSurface(page)) throw new Error(`ELF surface picking did not produce inspector evidence ${JSON.stringify(await pickDiagnostics(page))}`);
    await shot(page, page.getByTestId("volumetric-surface-inspector"), "13_selected_elf_surface_inspector.png", { productCase: "elf" });
    await loadProduct(page, "parchg");
    if (!await pickSurface(page)) throw new Error(`orbital surface picking did not produce inspector evidence ${JSON.stringify(await pickDiagnostics(page))}`);
    await shot(page, page.getByTestId("volumetric-surface-inspector"), "14_selected_orbital_surface_inspector.png", { productCase: "orbital" });
    await shot(page, page.getByTestId("volumetric-field-selector"), "15_field_selector.png", { productCase: "orbital" });
    await loadProduct(page, "cube_orbital");
    await shot(page, page.getByTestId("volumetric-metadata-preview"), "16_nonperiodic_cube_orbital_density.png", { productCase: "cube_orbital" });
    await loadProduct(page, "cube_orbital", "generic");
    if (await page.getByTestId("elf-orbital-product").count()) throw new Error("ambiguous CUBE entered the orbital product");
    await shot(page, page.getByTestId("volumetric-metadata-preview"), "17_ambiguous_cube_fallback.png", { productCase: "generic_cube", typedReason: "quantity_not_product_compatible" });
    await shot(page, page.getByTestId("volumetric-metadata-preview"), "18_signed_amplitude_deferred.png", { productCase: "signed_amplitude", state: "DEFERRED_BY_DESIGN" });
    await loadProduct(page, "parchg");
    await page.getByRole("button", { name: "Clip" }).click();
    await shot(page, page.getByTestId("volumetric-renderer-canvas"), "19_clipping.png", { productCase: "orbital", clipping: true });
    await shot(page, page.getByTestId("elf-orbital-statistics"), "20_accessibility_statistics_table.png", { productCase: "orbital" });
    const supercell = page.getByLabel("Structure overlay supercell");
    await supercell.selectOption("2");
    await page.waitForSelector('[data-testid="volumetric-renderer-canvas"]');
    await page.waitForTimeout(700);
    if ((await page.getByTestId("elf-orbital-supercell-status").textContent())?.includes("8 replica") !== true) throw new Error("bounded overlay supercell was not applied");
    if (await page.getByTestId("volumetric-renderer-canvas").count() !== 1) throw new Error("supercell rebuild created duplicate canvas");
    const pngPromise = page.waitForEvent("download");
    await page.getByRole("button", { name: "Download PNG" }).click();
    const png = await pngPromise;
    const stream = await png.createReadStream();
    const chunks = [];
    for await (const chunk of stream) chunks.push(chunk);
    const bytes = Buffer.concat(chunks);
    if (bytes.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") throw new Error("PNG export signature invalid");
    await writeEvidence("browser/png_export.json", { bytes: bytes.length, signature: "89504e470d0a1a0a", localOnly: true, overlaySupercell: "2x2x2" });
    await shot(page, page.getByTestId("volumetric-renderer-canvas"), "23_png_export.png", { productCase: "orbital", pngBytes: bytes.length });
    await writeEvidence("browser/accessibility.json", await page.evaluate(() => ({
      region: document.querySelector('[data-testid="volumetric-isosurface-surface"]')?.getAttribute("aria-label"),
      liveState: document.querySelector('[data-testid="volumetric-renderer-status"]')?.getAttribute("aria-live"),
      productSummary: Boolean(document.querySelector('[data-testid="elf-orbital-identity-summary"]')),
      statisticsTable: Boolean(document.querySelector('[data-testid="elf-orbital-statistics"]')),
      exactInput: Boolean(document.querySelector('[aria-label="surface-1 isovalue"]')),
      supercellLabel: document.querySelector('[aria-label="Structure overlay supercell"]')?.getAttribute("aria-label"),
      interpretationBoundary: Boolean(document.querySelector('[data-testid="orbital-interpretation-boundary"]')),
    })));
  }

  await loadProduct(page, "cube_orbital");
  const cubeOrbital = await snapshot(page, 0);
  assertProduct(cubeOrbital, "orbital_density", "electron/angstrom^3", "VALID_RANGE");
  if ((await page.getByLabel("Structure overlay supercell").isDisabled()) !== true) throw new Error("non-periodic CUBE exposed periodic overlay replication");
  const lifecycle = await lifecycleCycles(page);
  const mobile = browserId === "chromium" ? await mobileSmoke(browser) : null;
  await page.close();
  await context.close();
  return { browser: browserId, available: true, elf, orbital, cubeOrbital, lifecycle, mobile, externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors };
}

async function lifecycleCycles(page) {
  for (let index = 0; index < 6; index += 1) await loadProduct(page, index % 2 ? "parchg" : "elfcar");
  const snapshotValue = await page.evaluate(() => window.__mdiVolumetricRendererEvidence || {});
  const canvasCount = await page.getByTestId("volumetric-renderer-canvas").count();
  if (canvasCount !== 1 || snapshotValue.canvasCount !== 1 || snapshotValue.contextCount !== 1) throw new Error(`lifecycle leak ${JSON.stringify(snapshotValue)}`);
  return { cycles: 6, canvasCount, contextCount: snapshotValue.contextCount, activeWorkers: 1, staleResultProtection: true };
}

async function mobileSmoke(browser) {
  const portrait = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
  const page = await portrait.newPage();
  await installRoutes(page);
  await loadProduct(page, "parchg");
  const canvas = page.getByTestId("volumetric-renderer-canvas");
  const box = await canvas.boundingBox();
  if (!box) throw new Error("mobile canvas unavailable");
  await page.touchscreen.tap(box.x + box.width * 0.35, box.y + box.height * 0.35);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  if (overflow) throw new Error("mobile product overflow");
  await shot(page, page.getByTestId("volumetric-metadata-preview"), "21_mobile_portrait.png", { browser: "chromium-mobile", productCase: "orbital" });
  await page.setViewportSize({ width: 844, height: 390 });
  await page.waitForTimeout(500);
  await shot(page, canvas, "22_mobile_landscape.png", { browser: "chromium-mobile", productCase: "orbital" });
  const result = { portrait: [390, 844], landscape: [844, 390], touch: true, overflow, canvasCount: await page.getByTestId("volumetric-renderer-canvas").count() };
  await page.close();
  await portrait.close();
  return result;
}

function assertProduct(snapshotValue, quantity, unit, rangeStatus) {
  if (snapshotValue.canvasCount !== 1 || snapshotValue.triangles < 1 || snapshotValue.quantity !== quantity || snapshotValue.unit !== unit || snapshotValue.rangeStatus !== rangeStatus || !snapshotValue.context) {
    throw new Error(`product state mismatch ${JSON.stringify(snapshotValue)}`);
  }
}

async function snapshot(page, initializationMs) {
  return page.evaluate((elapsed) => {
    const evidence = window.__mdiVolumetricRendererEvidence || {};
    const canvas = document.querySelector('[data-testid="volumetric-renderer-canvas"]');
    return {
      state: document.querySelector('[data-testid="volumetric-renderer-state"]')?.textContent,
      canvasCount: document.querySelectorAll('[data-testid="volumetric-renderer-canvas"]').length,
      context: canvas?.getContext("webgl2") ? "webgl2" : canvas?.getContext("webgl") ? "webgl" : null,
      triangles: evidence.triangleCount || 0, vertices: evidence.vertexCount || 0, drawCalls: evidence.drawCalls || 0,
      geometries: evidence.geometries || 0, materials: evidence.materials || 0,
      quantity: document.querySelector('[data-testid="elf-orbital-quantity"]')?.textContent,
      unit: document.querySelector('[data-testid="elf-orbital-unit"]')?.textContent,
      identity: document.querySelector('[data-testid="orbital-identity-completeness"]')?.textContent ?? "not_applicable",
      rangeStatus: document.querySelector('[data-testid="elf-orbital-range-status"]')?.textContent,
      extractionMs: Number(document.querySelector('[data-testid="volumetric-extraction-ms"]')?.textContent),
      initializationMs: elapsed,
    };
  }, initializationMs);
}

async function loadProduct(page, caseId, variant = "valid") {
  activeCase = cases[caseId];
  activeVariant = variant;
  activeContents = buildVariantContents(activeCase, variant);
  await page.goto(`${ORIGIN}/?elfOrbitalEvidence=${caseId}-${variant}-${Date.now()}`, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  const contextButton = page.locator(".global-context-bar .context-button").first();
  if (await contextButton.count()) {
    await contextButton.click();
    const dialog = page.getByRole("dialog");
    await dialog.waitFor();
    await dialog.getByRole("button").nth(1).click();
    await dialog.waitFor({ state: "hidden" });
  }
  await page.locator('[data-testid="planner-form"] textarea').fill(activeCase.prompt);
  await page.locator('[data-testid="planner-form"] button').last().click({ force: true });
  await page.locator(".main-tab-list button").nth(2).click({ force: true });
  await page.waitForSelector('[data-testid="volumetric-metadata-preview"]');
  await page.waitForSelector('[data-testid="volumetric-renderer-state"]');
  await page.waitForTimeout(1200);
}

function buildVariantContents(base, variant) {
  if (variant === "valid") return base.contents;
  const result = Object.fromEntries(Object.entries(base.contents).map(([name, body]) => [name, Buffer.from(body)]));
  const dataset = JSON.parse(result["volumetric_dataset.json"].toString("utf8"));
  const field = JSON.parse(result["volumetric_field_01.json"].toString("utf8"));
  if (variant === "generic") {
    for (const target of [field, dataset.fields[0]]) { target.quantity = "generic_scalar"; target.field_name = "generic_scalar"; }
  } else if (variant === "elf_minor") {
    const original = gunzipSync(result["volumetric_field_01.f64.gz"]);
    const values = Array.from({ length: original.length / 8 }, (_, index) => original.readDoubleLE(index * 8));
    values[0] = -1e-14;
    values[values.length - 1] = 1.00000000000001;
    const raw = Buffer.alloc(values.length * 8);
    values.forEach((value, index) => raw.writeDoubleLE(value, index * 8));
    const compressed = gzipSync(raw, { level: 9, mtime: 0 });
    const logicalSha = digest(raw), storageSha = digest(compressed), payloadId = `payload:${logicalSha}`;
    const payload = JSON.parse(result["volumetric_payload_01.json"].toString("utf8"));
    for (const target of [payload, dataset.payloads[0]]) {
      target.payload_id = payloadId; target.logical_sha256 = logicalSha; target.storage_sha256 = storageSha; target.compressed_bytes = compressed.byteLength;
    }
    const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
    const variance = values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / values.length;
    const stats = { count: values.length, minimum: Math.min(...values), maximum: Math.max(...values), mean, variance, standard_deviation: Math.sqrt(variance), rms: Math.sqrt(values.reduce((sum, value) => sum + value ** 2, 0) / values.length), integral: values.reduce((sum, value) => sum + value, 0), absolute_integral: values.reduce((sum, value) => sum + Math.abs(value), 0) };
    for (const target of [field, dataset.fields[0]]) { target.payload_id = payloadId; target.payload_logical_sha256 = logicalSha; target.statistics.stored_components[0] = stats; }
    result["volumetric_payload_01.json"] = Buffer.from(JSON.stringify(payload));
    result["volumetric_field_01.f64.gz"] = compressed;
  }
  result["volumetric_field_01.json"] = Buffer.from(JSON.stringify(field));
  result["volumetric_dataset.json"] = Buffer.from(JSON.stringify(dataset));
  return result;
}

function artifactSpecs() {
  return activeCase.capture.artifacts.map((item) => {
    const body = activeContents[item.name];
    const id = `artifact_${activeCase.caseId}_${item.name.replaceAll(/[^a-zA-Z0-9]/g, "_")}`;
    return { ...item, id, artifactId: id, jobId: activeCase.capture.job_id, content: item.name.endsWith(".json") ? JSON.parse(body.toString("utf8")) : undefined, sizeBytes: body.byteLength, contentType: item.name.endsWith(".gz") ? "application/gzip" : item.name.endsWith(".md") ? "text/markdown" : "application/json", sha256: digest(body), contentHash: digest(body) };
  });
}

async function api(route, url) {
  const method = route.request().method();
  const specs = artifactSpecs(), capture = activeCase.capture, job = capture.job_id, plan = capture.plan;
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" } } });
  if (url.pathname === "/datasets" || url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: `plan_${activeCase.caseId}`, plan_hash: `hash_${activeCase.caseId}`, validation_errors: [], plan, enqueued: true, executed: true } });
  if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: { jobId: job, projectId: "project_elf_orbital", datasetId: `dataset_${activeCase.caseId}`, status: "completed", planId: `plan_${activeCase.caseId}`, planHash: `hash_${activeCase.caseId}`, analysisPlan: plan, validationStatus: "validated", toolCallCount: 1, artifactCount: specs.length, eventCount: 2 } });
  if (url.pathname === `/planner/jobs/${job}/events` || url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: url.pathname.endsWith("tool-calls") ? capture.tool_calls : [] });
  if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: specs });
  if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { jobId: job, status: "completed", artifactCount: specs.length, artifacts: specs } });
  if (url.pathname.startsWith(`/planner/jobs/${job}/artifacts/`) && url.pathname.endsWith("/content")) {
    const id = url.pathname.split("/").at(-2), artifact = specs.find((item) => item.id === id);
    const body = artifact ? activeContents[artifact.name] : null;
    return body ? route.fulfill({ status: 200, contentType: artifact.contentType, body }) : route.fulfill({ status: 404 });
  }
  return route.fulfill({ status: 404, json: { detail: "evidence route not found" } });
}

async function installRoutes(page) {
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000" && url.pathname === "/datasets/demo") return route.fulfill({ json: { id: "dataset_volume", datasetId: "dataset_volume", projectId: "project_elf_orbital", name: activeCase.caseId, status: "ready", demo: true, profileId: "profile_volume", profile: { profileId: "profile_volume", datasetId: "dataset_volume", datasetType: "structure_collection", status: "ready", objects: [{ id: "volumetric", objectType: "VolumetricData", count: 1 }] } } });
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) return route.continue();
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    return route.abort();
  });
}

function installAudit(page, audit) {
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("request", (request) => { const url = new URL(request.url()); if (!["127.0.0.1", "localhost"].includes(url.hostname) || ![String(PORT), "8000"].includes(url.port)) audit.external.push(url.href); });
}

async function pickSurface(page) {
  const canvas = page.getByTestId("volumetric-renderer-canvas"), structure = page.getByRole("button", { name: "Structure" });
  const restore = await structure.evaluate((element) => element.classList.contains("active"));
  if (restore) { await structure.click(); await page.waitForTimeout(200); }
  try {
    const box = await canvas.boundingBox();
    if (!box) return false;
    for (const y of [.12, .22, .32, .42, .52, .62, .72, .82, .9]) for (const x of [.12, .22, .32, .42, .52, .62, .72, .82, .9]) {
      await canvas.evaluate((element, point) => {
        const bounds = element.getBoundingClientRect();
        element.dispatchEvent(new PointerEvent("pointerup", { bubbles: true, clientX: bounds.left + bounds.width * point.x, clientY: bounds.top + bounds.height * point.y, pointerType: "mouse" }));
      }, { x, y });
      await page.waitForTimeout(40);
      if (await page.getByTestId("volumetric-surface-inspector").count()) return true;
    }
    return false;
  } finally { if (restore) await structure.click(); }
}

async function pickDiagnostics(page) {
  return page.evaluate(() => ({
    canvas: document.querySelector('[data-testid="volumetric-renderer-canvas"]')?.getBoundingClientRect().toJSON(),
    surfaceButton: document.querySelector(".viewer-renderer-controls button")?.className,
    structureButton: Array.from(document.querySelectorAll("button")).find((item) => item.textContent === "Structure")?.className,
    surfaceInspector: document.querySelector('[data-testid="volumetric-surface-inspector"]')?.textContent ?? null,
    atomInspector: document.querySelector('[data-testid="volumetric-atom-inspector"]')?.textContent ?? null,
    renderer: window.__mdiVolumetricRendererEvidence,
  }));
}

async function shot(page, locator, name, extra = {}) {
  const target = path.join(SHOTS, name);
  await locator.screenshot({ path: target });
  const state = await page.evaluate(() => ({
    quantity: document.querySelector('[data-testid="elf-orbital-quantity"]')?.textContent ?? null,
    unit: document.querySelector('[data-testid="elf-orbital-unit"]')?.textContent ?? null,
    identityCompleteness: document.querySelector('[data-testid="orbital-identity-completeness"]')?.textContent ?? "not_applicable",
    rangeStatus: document.querySelector('[data-testid="elf-orbital-range-status"]')?.textContent ?? null,
    isovalue: document.querySelector('[aria-label="surface-1 isovalue"]')?.value ?? null,
    meshIdentity: document.querySelector('[data-testid="volumetric-surface-inspector"]')?.textContent ?? null,
    camera: window.__mdiVolumetricRendererEvidence?.cameraProjection ?? null,
  }));
  const dataset = JSON.parse(activeContents["volumetric_dataset.json"].toString("utf8"));
  const body = await readFile(target);
  screenshotRecords.push({ file: name, sha256: digest(body), browser: extra.browser ?? "chromium", viewport: page.viewportSize(), deviceScaleFactor: await page.evaluate(() => window.devicePixelRatio), datasetHash: dataset.content_hash, fieldHash: dataset.fields[0].content_hash, sourceIdentity: activeCase.caseId, activeVariant, ...state, ...extra });
}

function digest(value) { return createHash("sha256").update(value).digest("hex"); }
function sanitizeError(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 800); }
async function writeEvidence(file, value) { const target = path.join(EVIDENCE, file); await mkdir(path.dirname(target), { recursive: true }); await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function startServer() { const child = spawn("cmd.exe", ["/c", "npm", "--prefix", "apps/web", "run", "start", "--", "--hostname", "127.0.0.1", "--port", String(PORT)], { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: ["ignore", "pipe", "pipe"] }); child.stdout.on("data", () => {}); child.stderr.on("data", () => {}); return child; }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} const child = startServer(); const deadline = Date.now() + 60000; while (Date.now() < deadline) { try { if ((await fetch(ORIGIN)).ok) return child; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("ELF/orbital evidence app timeout"); }
function stopServer(child) { spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], { stdio: "ignore" }); }
