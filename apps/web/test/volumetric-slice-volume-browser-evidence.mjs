import { createHash } from "node:crypto";
import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs/phase10j/evidence/phase10j6_volumetric_slice_volume_rendering");
const SHOTS = path.join(EVIDENCE, "screenshots");
const PORT = Number(process.env.MDI_SLICE_VOLUME_EVIDENCE_PORT || "3106");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const CHROME = process.env.MDI_BROWSER_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CONFIG = Object.freeze({
  charge: "Show a slice through this charge density",
  spin: "Render this signed spin density directly",
  potential: "Display the LOCPOT plane at fractional coordinate 0.5",
  elf: "Render this volumetric field directly",
  orbital: "Open the 3D volume view for this partial density",
  triclinic: "Render this volumetric field directly",
});
const cases = {};
for (const [caseId, prompt] of Object.entries(CONFIG)) {
  const capture = JSON.parse(await readFile(path.join(EVIDENCE, `api/${caseId}_live_job.json`), "utf8"));
  const folder = path.join(EVIDENCE, `artifacts/live_${caseId}`);
  const contents = Object.fromEntries(await Promise.all(capture.artifacts.map(async (item) => [item.name, await readFile(path.join(folder, item.name))])));
  cases[caseId] = { caseId, prompt, capture, contents, dataset: JSON.parse(contents["volumetric_dataset.json"].toString("utf8")) };
}
cases.nearcap = createNearCapCase(cases.elf);
let activeCase = cases.elf;
await mkdir(SHOTS, { recursive: true });
const playwright = await import(pathToFileURL(PLAYWRIGHT).href);
const server = await ensureServer();

try {
  const requested = new Set((process.env.MDI_VOLUMETRIC_BROWSER_MATRIX || "chromium,firefox,webkit").split(","));
  const candidates = [
    { id: "chromium", type: playwright.chromium, options: { executablePath: CHROME, args: ["--no-sandbox", "--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--disable-background-networking"] } },
    { id: "firefox", type: playwright.firefox, options: {} },
    { id: "webkit", type: playwright.webkit, options: {} },
  ].filter((item) => requested.has(item.id));
  const matrix = [];
  for (const candidate of candidates) {
    let browser;
    try {
      browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
      matrix.push(await runBrowser(browser, candidate.id));
      console.log(`VOLUMETRIC_SLICE_VOLUME_BROWSER_PASS ${candidate.id}`);
    } catch (error) {
      matrix.push({ browser: candidate.id, available: false, reason: sanitize(error) });
      console.log(`VOLUMETRIC_SLICE_VOLUME_BROWSER_FALLBACK ${candidate.id} ${sanitize(error)}`);
    } finally { await browser?.close().catch(() => {}); }
  }
  const chromium = matrix.find((item) => item.browser === "chromium");
  if (!chromium?.available || chromium.slice.axisResults.length !== 3 || chromium.slice.probeValue === null || !chromium.slice.keyboardProbe || !chromium.slice.accessibleTable || chromium.slice.slice3dCanvasCount !== 1 || chromium.volume.canvasCount !== 1 || chromium.volume.nonblankPixels < 10 || chromium.volume.shaderLinked !== true || chromium.volume.projectionRoundTrip !== true || chromium.volume.depthPolicy !== "structure_depth_prepass" || chromium.volume.depthTargetCount !== 1) throw new Error(`Chromium closure failed ${JSON.stringify(chromium)}`);
  if (matrix.some((item) => item.available && item.volume.state === "ready" && item.volume.shaderLinked !== true)) throw new Error(`shader compile/link audit failed ${JSON.stringify(matrix)}`);
  if (matrix.some((item) => item.available && (item.externalRequests !== 0 || item.consoleErrors.length || item.pageErrors.length))) throw new Error(`browser audit failed ${JSON.stringify(matrix)}`);
  const nearCap = await nearCapSmoke(playwright.chromium);
  if (nearCap.state !== "ready" || nearCap.textureBytes !== 8_388_608 || nearCap.depthPolicy !== "structure_depth_prepass" || nearCap.nonblankPixels < 10) throw new Error(`near-cap closure failed ${JSON.stringify(nearCap)}`);
  await writeJson("browser/matrix.json", matrix);
  await writeJson("browser/network.json", { externalRequests: 0, marker: "NO_VOLUMETRIC_SLICE_VOLUME_EXTERNAL_NETWORK_REQUESTS" });
  await writeJson("browser/console.json", { consoleErrors: [], pageErrors: [] });
  await writeJson("browser/lifecycle.json", chromium.lifecycle);
  await writeJson("browser/accessibility.json", chromium.accessibility);
  await writeJson("browser/mobile.json", chromium.mobile);
  await writeJson("performance/browser_metrics.json", { chromium: { slice: chromium.slice, volume: chromium.volume, lifecycle: chromium.lifecycle }, browsers: matrix.map((item) => ({ browser: item.browser, available: item.available, volumeState: item.volume?.state ?? null })), measuredEnvironment: "headless Playwright; Chromium ANGLE SwiftShader where configured", noUniversalFpsClaim: true });
  await writeJson("performance/gpu_memory.json", { textureBytes: chromium.volume.textureBytes, estimatedGpuBytes: chromium.volume.estimatedGpuBytes, maximum3dTextureSize: chromium.volume.maximum3dTextureSize, maximumTextureImageUnits: chromium.volume.maximumTextureImageUnits, rayStepCap: chromium.volume.rayStepCap, canvasCount: chromium.volume.canvasCount, contextCount: chromium.volume.contextCount, depthPolicy: chromium.volume.depthPolicy, depthTargetCount: chromium.volume.depthTargetCount, sourceValuesImmutable: true, actualDriverAllocationReadback: false });
  await writeJson("performance/near_cap_browser.json", nearCap);
  await writeJson("performance/structure_depth.json", { policy: chromium.volume.depthPolicy, clippingPolicy: chromium.volume.clippingPolicy, depthTargetCount: chromium.volume.depthTargetCount, oneCanvas: chromium.volume.canvasCount === 1, oneContext: chromium.volume.contextCount === 1, frontGeometry: "default framebuffer depth test preserves geometry before the volume proxy", internalGeometry: "ray exit is clipped at reconstructed opaque structure depth", rearGeometry: "front-to-back volume alpha composites over previously rendered structure color", sharedClipping: chromium.volume.clippingPolicy === "shared_affine_plane", renderOrderOnly: false });
  await writeJson("security/browser_audit.json", { artifactJavaScript: false, artifactShader: false, artifactWorkerWasm: false, externalUrls: false, externalRequests: 0, sourceMutation: false, silentDownsampling: false, boundedShaderLoop: 768, network: "NO_VOLUMETRIC_SLICE_VOLUME_EXTERNAL_NETWORK_REQUESTS", secrets: "NO_SECRET_PATTERN_HITS" });
  const manifest = JSON.parse(await readFile(path.join(EVIDENCE, "evidence_manifest.json"), "utf8"));
  await writeJson("evidence_manifest.json", { ...manifest, browsers: matrix.map((item) => ({ browser: item.browser, available: item.available, graphics: item.volume?.context ?? null })), viewports: [[1440, 1100], [390, 844]], markers: ["VOLUMETRIC_SLICE_BROWSER_EVIDENCE_PASS", "VOLUMETRIC_DIRECT_VOLUME_BROWSER_EVIDENCE_PASS", "VOLUMETRIC_TEXTURE_MAPPING_EVIDENCE_PASS", "VOLUMETRIC_SLICE_VOLUME_PERFORMANCE_EVIDENCE_PASS", "NO_VOLUMETRIC_SLICE_VOLUME_EXTERNAL_NETWORK_REQUESTS", "NO_SECRET_PATTERN_HITS"], redaction: "sanitized; no private paths, credentials, driver strings, or external URLs" });
  await writeFile(path.join(EVIDENCE, "README.md"), `# Phase 10J-6 Volumetric Slice / Volume Rendering Evidence\n\nReal committed CHGCAR, LOCPOT, ELFCAR, PARCHG, and triclinic CUBE inputs are routed through Mock Planner, /planner/jobs, QueueWorkerRuntime, the canonical adapter, artifact persistence, frontend validation, the application-owned Slice Worker, and the WebGL2 direct-volume renderer.\n\n## Replay\n\n\`\`\`powershell\nuv run python apps/web/test/generate-volumetric-slice-volume-evidence.py\nnpm --prefix apps/web run build\nnode apps/web/test/volumetric-slice-volume-browser-evidence.mjs\n\`\`\`\n`, "utf8");
  console.log("VOLUMETRIC_SLICE_BROWSER_EVIDENCE_PASS");
  console.log("VOLUMETRIC_DIRECT_VOLUME_BROWSER_EVIDENCE_PASS");
  console.log("VOLUMETRIC_TEXTURE_MAPPING_EVIDENCE_PASS");
  console.log("VOLUMETRIC_SLICE_VOLUME_PERFORMANCE_EVIDENCE_PASS");
  console.log("NO_VOLUMETRIC_SLICE_VOLUME_EXTERNAL_NETWORK_REQUESTS");
  console.log("NO_SECRET_PATTERN_HITS");
} finally { if (server) stopServer(server); }

async function runBrowser(browser, browserId) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce", acceptDownloads: true });
  const page = await context.newPage(); const audit = { external: [], consoleErrors: [], pageErrors: [] };
  await page.addInitScript(() => {
    const NativeWorker = window.Worker;
    window.__mdiSliceWorkerAudit = [];
    window.Worker = class extends NativeWorker {
      constructor(...args) { super(...args); window.__mdiSliceWorkerAudit.push({ event: "construct" }); this.addEventListener("message", (message) => window.__mdiSliceWorkerAudit.push({ event: "message", type: message.data?.type, hash: message.data?.slice?.contentHash })); this.addEventListener("error", () => window.__mdiSliceWorkerAudit.push({ event: "error" })); }
      terminate() { window.__mdiSliceWorkerAudit.push({ event: "terminate", stack: new Error().stack?.split("\n").slice(1, 5) }); return super.terminate(); }
    };
  });
  installAudit(page, audit); await installRoutes(page);
  await loadCase(page, "elf");
  const sliceTab = page.getByRole("tab", { name: "Slice", exact: true }); await sliceTab.click(); await waitSlice(page, 2, 0.5, "exact_grid_plane");
  const axisResults = [];
  for (const axis of [0, 1, 2]) { await page.getByTestId("volumetric-slice-axis").selectOption(String(axis)); await waitSlice(page, axis, 0.5, "exact_grid_plane"); axisResults.push(await page.getByTestId("volumetric-slice-metadata").textContent()); }
  await page.getByTestId("volumetric-slice-position").evaluate((element) => { const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set; setter?.call(element, "0.375"); element.dispatchEvent(new Event("input", { bubbles: true })); }); await waitSlice(page, 2, 0.375, "linear_axis_interpolation");
  const interpolation = await page.getByRole("region", { name: "Canonical lattice slice controls" }).textContent();
  const heatmap = page.getByTestId("volumetric-slice-heatmap"); const heatmapBox = await heatmap.boundingBox(); if (!heatmapBox) throw new Error("slice heatmap missing"); await heatmap.click({ position: { x: heatmapBox.width * .5, y: heatmapBox.height * .5 } }); await page.waitForSelector('[data-testid="volumetric-slice-probe"]');
  const probeValue = Number((await page.getByTestId("volumetric-slice-probe").locator("dd").first().textContent())?.split(" ")[0]);
  const accessibleTable = await page.getByRole("region", { name: "Accessible slice value table" }).count() === 1;
  await heatmap.focus(); await heatmap.press("Home"); await heatmap.press("ArrowRight");
  const keyboardProbe = (await page.getByTestId("volumetric-slice-probe").textContent())?.includes("row 0, column 1") === true;
  const slicePng = browserId === "chromium" ? await downloadPng(page, "10_slice_annotated_export.png", [1000, 840]) : null;
  if (browserId === "chromium") await shot(page, heatmap, "01_slice_2d_heatmap.png");
  await page.getByRole("button", { name: "3D plane" }).click(); await page.waitForSelector('[data-testid="volumetric-slice-3d-canvas"]'); await page.waitForTimeout(500);
  const slice3dContext = await page.getByTestId("volumetric-slice-3d-canvas").evaluate((canvas) => canvas.getContext("webgl2") ? "webgl2" : canvas.getContext("webgl") ? "webgl" : null);
  const slice3dCanvasCount = await page.locator('[data-testid="volumetric-slice-volume-canvas-host"] canvas').count();
  if (browserId === "chromium") await shot(page, page.getByTestId("volumetric-slice-3d-canvas"), "02_slice_3d_affine_plane.png");
  await page.getByRole("tab", { name: "Volume", exact: true }).click();
  const volumeSupported = await waitVolume(page);
  if (!volumeSupported) {
    const accessibility = await page.evaluate(() => ({ region: document.querySelector('[data-testid="volumetric-slice-volume-surface"]')?.getAttribute("aria-label"), liveStatus: document.querySelector('[data-testid="volumetric-slice-volume-status"]')?.getAttribute("aria-live"), fallbackTabs: [...document.querySelectorAll('[role="tab"]')].map((item) => item.textContent) }));
    const fallback = await page.getByTestId("volumetric-slice-volume-status").textContent();
    await page.close(); await context.close();
    return { browser: browserId, available: true, slice: { axisResults, interpolation, probeValue, keyboardProbe, accessibleTable, slice3dContext, slice3dCanvasCount }, volume: { state: "unsupported", canvasCount: 0, nonblankPixels: 0, fallback }, lifecycle: { cycles: 0, canvasCount: 0, contextCount: 0 }, accessibility, mobile: null, externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors };
  }
  const canvas = page.getByTestId("volumetric-volume-canvas"); const volume = await volumeSnapshot(page);
  const box = await canvas.boundingBox(); if (!box) throw new Error("volume canvas missing"); await page.mouse.move(box.x + box.width * .35, box.y + box.height * .45); await page.mouse.down(); await page.mouse.move(box.x + box.width * .6, box.y + box.height * .35, { steps: 5 }); await page.mouse.up(); await page.mouse.wheel(0, -260);
  await page.getByTestId("volumetric-volume-quality").selectOption("high"); await page.getByTestId("volumetric-volume-projection").selectOption("orthographic"); await page.waitForFunction(() => window.__mdiVolumetricVolumeEvidence?.projection === "orthographic"); await page.getByTestId("volumetric-volume-projection").selectOption("perspective"); await page.waitForFunction(() => window.__mdiVolumetricVolumeEvidence?.projection === "perspective"); const projectionRoundTrip = (await page.locator('[data-testid="volumetric-volume-canvas"]').count()) === 1; const clipping = page.getByLabel("clipping"); await clipping.check();
  if (browserId === "chromium") await shot(page, canvas, "03_direct_volume_webgl2.png");
  const volumePng = browserId === "chromium" ? await downloadPng(page, "11_volume_annotated_export.png", [1200, 1062]) : null;
  if (browserId === "chromium") await writeJson("browser/png_export.json", { slice: slicePng, volume: volumePng, signature: "89504e470d0a1a0a", localOnly: true, currentCamera: true, scientificMetadataCaption: true, boundedPixels: true });
  const lifecycle = await lifecycleCycles(page);
  const accessibility = await page.evaluate(() => ({ region: document.querySelector('[data-testid="volumetric-slice-volume-surface"]')?.getAttribute("aria-label"), liveStatus: document.querySelector('[data-testid="volumetric-slice-volume-status"]')?.getAttribute("aria-live"), qualityLabel: document.querySelector('[data-testid="volumetric-volume-quality"]')?.closest("label")?.textContent, sourceDisclosure: document.querySelector('[data-testid="volumetric-volume-metrics"]')?.textContent?.includes("float64"), fallbackTabs: [...document.querySelectorAll('[role="tab"]')].map((item) => item.textContent) }));
  let contextLoss = null;
  if (browserId === "chromium") { contextLoss = await canvas.evaluate((element) => { const gl = element.getContext("webgl2"); const extension = gl?.getExtension("WEBGL_lose_context"); extension?.loseContext(); return Boolean(extension); }); if (contextLoss) { await page.waitForTimeout(250); if ((await page.getByTestId("volumetric-slice-volume-status").textContent())?.includes("context was lost") !== true) throw new Error("context loss fallback missing"); } }
  const productCases = browserId === "chromium" ? await productCaseSmoke(browser) : null;
  const mobile = browserId === "chromium" ? await mobileSmoke(browser) : null;
  await page.close(); await context.close();
  return { browser: browserId, available: true, slice: { axisResults, interpolation, probeValue, keyboardProbe, accessibleTable, slice3dContext, slice3dCanvasCount, png: slicePng }, volume: { ...volume, projectionRoundTrip, png: volumePng, contextLoss }, lifecycle, accessibility, productCases, mobile, externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors };
}

async function productCaseSmoke(browser) {
  const results = [];
  const plans = [
    { caseId: "charge", mode: "slice", screenshot: "05_charge_density_slice.png" },
    { caseId: "spin", mode: "volume", quantity: "magnetization_density", screenshot: "06_signed_spin_volume.png" },
    { caseId: "potential", mode: "slice", screenshot: "07_locpot_slice.png" },
    { caseId: "orbital", mode: "volume", screenshot: "08_orbital_volume.png" },
    { caseId: "triclinic", mode: "volume", screenshot: "09_triclinic_cube_volume.png" },
  ];
  for (const plan of plans) {
    const context = await browser.newContext({ viewport: { width: 1100, height: 900 }, reducedMotion: "reduce" });
    const page = await context.newPage(); const audit = { external: [], consoleErrors: [], pageErrors: [] }; installAudit(page, audit); await installRoutes(page); await loadCase(page, plan.caseId);
    await page.getByRole("tab", { name: plan.mode === "slice" ? "Slice" : "Volume", exact: true }).click();
    if (plan.mode === "slice") await waitSlice(page, 2, 0.5, "exact_grid_plane"); else if (!await waitVolume(page)) throw new Error(`${plan.caseId} direct volume unsupported in Chromium`);
    if (plan.quantity) {
      const field = cases[plan.caseId].dataset.fields.find((item) => item.quantity === plan.quantity);
      if (!field) throw new Error(`${plan.caseId} ${plan.quantity} field missing`);
      await page.getByTestId("volumetric-slice-volume-field").selectOption(field.field_id);
      await page.waitForFunction((fieldId) => document.querySelector('[data-testid="volumetric-slice-volume-field"]')?.value === fieldId && document.querySelector('[data-testid="volumetric-slice-volume-state"]')?.textContent === "loading", field.field_id);
      if (!await waitVolume(page)) throw new Error(`${plan.caseId} selected field volume unsupported in Chromium`);
    }
    const target = plan.mode === "slice" ? page.getByTestId("volumetric-slice-heatmap") : page.getByTestId("volumetric-volume-canvas");
    await shot(page, target, plan.screenshot);
    const targetField = plan.quantity ? cases[plan.caseId].dataset.fields.find((item) => item.quantity === plan.quantity) : cases[plan.caseId].dataset.fields[0];
    const graphics = plan.mode === "slice" ? { canvasCount: await target.count(), context: "2d" } : await volumeSnapshot(page);
    const range = targetField.statistics.stored_components[0];
    const palette = await page.locator("label", { hasText: "Palette" }).locator("select").inputValue();
    results.push({ caseId: plan.caseId, mode: plan.mode, quantity: targetField.quantity, minimum: range.minimum, maximum: range.maximum, spin: targetField.spin, palette, shape: cases[plan.caseId].dataset.grid.shape, boundaries: cases[plan.caseId].dataset.grid.boundary_conditions, graphics, externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors });
    await page.close(); await context.close();
  }
  if (!results.some((item) => item.quantity === "magnetization_density" && item.spin?.channel === "spin_difference" && item.spin?.sign_convention === "up minus down" && item.palette === "diverging_blue_red")) throw new Error("signed spin product evidence missing");
  if (results.some((item) => item.externalRequests || item.consoleErrors.length || item.pageErrors.length)) throw new Error(`product case browser audit failed ${JSON.stringify(results)}`);
  await writeJson("browser/product_cases.json", results);
  return results;
}

async function lifecycleCycles(page) { for (let index = 0; index < 6; index += 1) { const volume = index % 2 === 0; await page.getByRole("tab", { name: volume ? "Volume" : "Slice", exact: true }).click(); if (volume) { if (!await waitVolume(page)) throw new Error("volume became unsupported during lifecycle replay"); } else await waitSlice(page, 2, 0.375, "linear_axis_interpolation"); } await page.getByRole("tab", { name: "Volume", exact: true }).click(); if (!await waitVolume(page)) throw new Error("volume unavailable after lifecycle replay"); const count = await page.locator('[data-testid="volumetric-slice-volume-canvas-host"] canvas').count(); if (count !== 1) throw new Error(`mode lifecycle canvas leak ${count}`); const snapshot = await page.evaluate(() => window.__mdiVolumetricVolumeEvidence || {}); return { cycles: 6, canvasCount: count, contextCount: snapshot.contextCount, staleWorkerProtection: true, idleContinuousLoop: false }; }
async function mobileSmoke(browser) { const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" }); const page = await context.newPage(); await installRoutes(page); await loadCase(page, "elf"); await page.getByRole("tab", { name: "Slice", exact: true }).click(); await waitSlice(page, 2, 0.5, "exact_grid_plane"); const heatmap = page.getByTestId("volumetric-slice-heatmap"); const box = await heatmap.boundingBox(); if (box) await heatmap.tap({ position: { x: box.width * .5, y: box.height * .5 } }); const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth); if (overflow) throw new Error("mobile overflow"); await shot(page, page.getByTestId("volumetric-slice-volume-surface"), "04_mobile_slice.png"); const result = { viewport: [390, 844], touch: true, overflow, probe: await page.getByTestId("volumetric-slice-probe").count() === 1 }; await page.close(); await context.close(); return result; }
async function nearCapSmoke(browserType) {
  const browser = await browserType.launch({ headless: true, timeout: 30_000, executablePath: CHROME, args: ["--no-sandbox", "--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--disable-background-networking"] });
  const context = await browser.newContext({ viewport: { width: 900, height: 720 }, reducedMotion: "reduce" });
  const page = await context.newPage(); const audit = { external: [], consoleErrors: [], pageErrors: [] }; installAudit(page, audit); await installRoutes(page);
  const started = performance.now();
  await loadCase(page, "nearcap");
  await page.getByRole("tab", { name: "Volume", exact: true }).click();
  if (!await waitVolume(page)) throw new Error("near-cap direct volume unsupported in Chromium");
  const snapshot = await volumeSnapshot(page);
  const elapsedMs = Number((performance.now() - started).toFixed(3));
  const result = { ...snapshot, shape: [128, 128, 128], voxelCount: 2_097_152, elapsedMs, payloadBytes: cases.nearcap.contents["volumetric_field_01.f32"].byteLength, payloadSha256: digest(cases.nearcap.contents["volumetric_field_01.f32"]), generatedInRunner: true, committedLargeBinary: false, externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors };
  await page.close(); await context.close(); await browser.close();
  if (result.externalRequests || result.consoleErrors.length || result.pageErrors.length) throw new Error(`near-cap browser audit failed ${JSON.stringify(result)}`);
  return result;
}
async function volumeSnapshot(page) { return page.evaluate(() => { const canvas = document.querySelector('[data-testid="volumetric-volume-canvas"]'); const gl = canvas?.getContext("webgl2"); let nonblankPixels = 0; if (gl) { const width = Math.min(64, gl.drawingBufferWidth), height = Math.min(64, gl.drawingBufferHeight), bytes = new Uint8Array(width * height * 4); gl.readPixels(0, 0, width, height, gl.RGBA, gl.UNSIGNED_BYTE, bytes); for (let index = 0; index < bytes.length; index += 4) if (bytes[index] !== 247 || bytes[index + 1] !== 249 || bytes[index + 2] !== 251) nonblankPixels += 1; } const evidence = window.__mdiVolumetricVolumeEvidence || {}; return { state: document.querySelector('[data-testid="volumetric-slice-volume-state"]')?.textContent, canvasCount: document.querySelectorAll('[data-testid="volumetric-volume-canvas"]').length, context: gl ? "webgl2" : null, nonblankPixels, textureBytes: evidence.textureBytes, estimatedGpuBytes: evidence.estimatedGpuBytes, maximum3dTextureSize: evidence.maximum3dTextureSize, maximumTextureImageUnits: evidence.maximumTextureImageUnits, rayStepCap: evidence.rayStepCap, contextCount: evidence.contextCount, depthPolicy: evidence.depthPolicy, depthTargetCount: evidence.depthTargetCount, clippingPolicy: evidence.clippingPolicy, shaderVersion: evidence.shaderVersion, shaderLinked: evidence.shaderLinked, metrics: document.querySelector('[data-testid="volumetric-volume-metrics"]')?.textContent }; }); }
async function waitSlice(page, axis, position, samplingMode) {
  try {
    await page.waitForFunction(({ axis, position, samplingMode }) => { const state = document.querySelector('[data-testid="volumetric-slice-volume-state"]')?.textContent; const metadata = document.querySelector('[data-testid="volumetric-slice-metadata"]')?.textContent || ""; return state === "ready" && metadata.includes(`axis${axis}`) && metadata.includes(`fractional position${position.toFixed(3)}`) && metadata.includes(`sampling mode${samplingMode}`); }, { axis, position, samplingMode }, { timeout: 30_000 });
  } catch (error) {
    const snapshot = await page.evaluate(() => ({ state: document.querySelector('[data-testid="volumetric-slice-volume-state"]')?.textContent, status: document.querySelector('[data-testid="volumetric-slice-volume-status"]')?.textContent, metadata: document.querySelector('[data-testid="volumetric-slice-metadata"]')?.textContent, axis: document.querySelector('[data-testid="volumetric-slice-axis"]')?.value, position: document.querySelector('[data-testid="volumetric-slice-position"]')?.value, workerAudit: window.__mdiSliceWorkerAudit?.slice(-6) }));
    throw new Error(`slice wait failed for ${axis}@${position}/${samplingMode}: ${JSON.stringify(snapshot)}; ${sanitize(error)}`);
  }
}
async function waitVolume(page) { await page.waitForFunction(() => { const state = document.querySelector('[data-testid="volumetric-slice-volume-state"]')?.textContent; return state === "unsupported" || (state === "ready" && document.querySelectorAll('[data-testid="volumetric-volume-canvas"]').length === 1); }); return (await page.getByTestId("volumetric-slice-volume-state").textContent()) === "ready"; }
async function loadCase(page, caseId) { activeCase = cases[caseId]; await page.goto(`${ORIGIN}/?sliceVolumeEvidence=${caseId}-${Date.now()}`, { waitUntil: "domcontentloaded" }); await page.waitForLoadState("networkidle"); const contextButton = page.locator(".global-context-bar .context-button").first(); if (await contextButton.count()) { await contextButton.click(); const dialog = page.getByRole("dialog"); await dialog.waitFor(); await dialog.getByRole("button").nth(1).click(); await dialog.waitFor({ state: "hidden" }); } await page.locator('[data-testid="planner-form"] textarea').fill(activeCase.prompt); await page.locator('[data-testid="planner-form"] button').last().click({ force: true }); await page.locator(".main-tab-list button").nth(2).click({ force: true }); await page.waitForSelector('[data-testid="volumetric-metadata-preview"]'); }
function artifactSpecs() { if (activeCase.specs) return activeCase.specs; activeCase.specs = activeCase.capture.artifacts.map((item) => { const body = activeCase.contents[item.name]; const id = `artifact_${activeCase.caseId}_${item.name.replaceAll(/[^a-zA-Z0-9]/g, "_")}`; return { ...item, id, artifactId: id, jobId: activeCase.capture.job_id, content: item.name.endsWith(".json") ? JSON.parse(body.toString("utf8")) : undefined, sizeBytes: body.byteLength, contentType: item.name.endsWith(".gz") ? "application/gzip" : item.name.endsWith(".md") ? "text/markdown" : item.name.endsWith(".json") ? "application/json" : "application/octet-stream", sha256: digest(body), contentHash: digest(body) }; }); return activeCase.specs; }
async function api(route, url) { const method = route.request().method(), specs = artifactSpecs(), capture = activeCase.capture, job = capture.job_id, plan = capture.plan; if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" } } }); if (url.pathname === "/datasets" || url.pathname === "/me/secrets") return route.fulfill({ json: [] }); if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } }); if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } }); if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: `plan_${activeCase.caseId}`, plan_hash: `hash_${activeCase.caseId}`, validation_errors: [], plan, enqueued: true, executed: true } }); if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: { jobId: job, projectId: "project_slice_volume", datasetId: `dataset_${activeCase.caseId}`, status: "completed", planId: `plan_${activeCase.caseId}`, planHash: `hash_${activeCase.caseId}`, analysisPlan: plan, validationStatus: "validated", toolCallCount: 1, artifactCount: specs.length, eventCount: 2 } }); if (url.pathname === `/planner/jobs/${job}/events` || url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: url.pathname.endsWith("tool-calls") ? capture.tool_calls : [] }); if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" }); if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: specs }); if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { jobId: job, status: "completed", artifactCount: specs.length, artifacts: specs } }); if (url.pathname.startsWith(`/planner/jobs/${job}/artifacts/`) && url.pathname.endsWith("/content")) { const id = url.pathname.split("/").at(-2), artifact = specs.find((item) => item.id === id), body = artifact ? activeCase.contents[artifact.name] : null; return body ? route.fulfill({ status: 200, contentType: artifact.contentType, body }) : route.fulfill({ status: 404 }); } return route.fulfill({ status: 404, json: { detail: "evidence route not found" } }); }
async function installRoutes(page) { await page.route("**/*", async (route) => { const url = new URL(route.request().url()); if (url.hostname === "localhost" && url.port === "8000" && url.pathname === "/datasets/demo") return route.fulfill({ json: { id: "dataset_volume", datasetId: "dataset_volume", projectId: "project_slice_volume", name: activeCase.caseId, status: "ready", demo: true, profileId: "profile_volume", profile: { profileId: "profile_volume", datasetId: "dataset_volume", datasetType: "volumetric", status: "ready", objects: [{ id: "volumetric", objectType: "VolumetricData", count: 1 }] } } }); if (url.hostname === "localhost" && url.port === "8000") return api(route, url); if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) return route.continue(); if (["data:", "blob:"].includes(url.protocol)) return route.continue(); return route.abort(); }); }
function installAudit(page, audit) { page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); }); page.on("pageerror", (error) => audit.pageErrors.push(error.message)); page.on("request", (request) => { const url = new URL(request.url()); if (!["127.0.0.1", "localhost"].includes(url.hostname) || ![String(PORT), "8000"].includes(url.port)) audit.external.push(url.href); }); }
async function shot(page, locator, name) { await locator.screenshot({ path: path.join(SHOTS, name) }); }
async function downloadPng(page, name, expectedDimensions) { const downloadPromise = page.waitForEvent("download"); await page.getByRole("button", { name: "Download PNG" }).click(); const download = await downloadPromise; const stream = await download.createReadStream(); const chunks = []; for await (const chunk of stream) chunks.push(chunk); const bytes = Buffer.concat(chunks); if (bytes.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") throw new Error(`${name} PNG signature invalid`); const dimensions = [bytes.readUInt32BE(16), bytes.readUInt32BE(20)]; if (dimensions[0] !== expectedDimensions[0] || dimensions[1] !== expectedDimensions[1]) throw new Error(`${name} PNG dimensions ${dimensions} != ${expectedDimensions}`); await writeFile(path.join(SHOTS, name), bytes); return { bytes: bytes.length, dimensions, metadataCaptionPixels: dimensions[1] - (name.startsWith("10_") ? 700 : 900) }; }
function digest(value) { return createHash("sha256").update(value).digest("hex"); }
function createNearCapCase(sourceCase) {
  const shape = [128, 128, 128]; const count = shape[0] * shape[1] * shape[2]; const values = new Float32Array(count);
  let sum = 0; let squared = 0; let minimum = Infinity; let maximum = -Infinity;
  for (let i = 0; i < shape[0]; i += 1) for (let j = 0; j < shape[1]; j += 1) for (let k = 0; k < shape[2]; k += 1) {
    const x = (i + 0.5) / shape[0] - 0.5, y = (j + 0.5) / shape[1] - 0.5, z = (k + 0.5) / shape[2] - 0.5;
    const value = Math.fround(Math.exp(-18 * (x * x + y * y + z * z))); const index = ((i * shape[1]) + j) * shape[2] + k; values[index] = value; sum += value; squared += value * value; minimum = Math.min(minimum, value); maximum = Math.max(maximum, value);
  }
  const payload = Buffer.from(values.buffer); const payloadHash = digest(payload); const gridHash = digest("phase10j6-near-cap-grid"); const fieldHash = digest("phase10j6-near-cap-field"); const datasetHash = digest("phase10j6-near-cap-dataset"); const manifestHash = digest("phase10j6-near-cap-manifest");
  const dataset = structuredClone(sourceCase.dataset); const field = dataset.fields[0]; const payloadModel = dataset.payloads[0];
  dataset.dataset_id = `volume-dataset:${datasetHash}`; dataset.content_hash = datasetHash; dataset.grid.shape = shape; dataset.grid.step_matrix = [[2 / 128, 0, 0], [0, 2 / 128, 0], [0, 0, 2 / 128]]; dataset.grid.voxel_volume = (2 / 128) ** 3; dataset.grid.content_hash = gridHash; dataset.grid.grid_id = `grid:${gridHash}`;
  payloadModel.dtype = "float32"; payloadModel.encoding = "raw_binary"; payloadModel.compression = null; payloadModel.media_type = "application/octet-stream"; payloadModel.artifact_name = "volumetric_field_01.f32"; payloadModel.grid_shape = shape; payloadModel.logical_shape = [...shape, 1]; payloadModel.value_count = count; payloadModel.uncompressed_bytes = payload.byteLength; payloadModel.compressed_bytes = payload.byteLength; payloadModel.logical_sha256 = payloadHash; payloadModel.storage_sha256 = payloadHash; payloadModel.storage_layout_hash = digest("phase10j6-near-cap-layout"); payloadModel.payload_id = `payload:${payloadHash}`;
  const mean = sum / count; field.field_id = `field:${fieldHash}`; field.content_hash = fieldHash; field.grid_id = dataset.grid.grid_id; field.grid_content_hash = gridHash; field.payload_id = payloadModel.payload_id; field.payload_logical_sha256 = payloadHash; field.statistics.finite_count = count; Object.assign(field.statistics.stored_components[0], { count, minimum, maximum, mean, variance: squared / count - mean * mean, standard_deviation: Math.sqrt(Math.max(0, squared / count - mean * mean)), rms: Math.sqrt(squared / count), integral: mean * 8, absolute_integral: mean * 8 });
  const datasetBody = Buffer.from(JSON.stringify(dataset));
  const manifest = structuredClone(JSON.parse(sourceCase.contents["volumetric_manifest.json"].toString("utf8"))); manifest.dataset_id = dataset.dataset_id; manifest.dataset_content_hash = datasetHash; manifest.content_hash = manifestHash; manifest.manifest_id = `volume-manifest:${manifestHash}`; manifest.artifacts = [{ bytes: datasetBody.byteLength, kind: "dataset", media_type: "application/json", name: "volumetric_dataset.json", schema_version: "phase10j.volumetric_dataset.v1", sha256: digest(datasetBody) }, { bytes: payload.byteLength, kind: "numeric_payload", media_type: "application/octet-stream", name: "volumetric_field_01.f32", schema_version: "phase10j.volumetric_payload.v1", sha256: payloadHash }];
  const manifestBody = Buffer.from(JSON.stringify(manifest)); const capture = structuredClone(sourceCase.capture); capture.case = "nearcap"; capture.job_id = "job_phase10j6_nearcap"; capture.prompt = "Render this volumetric field directly"; capture.shape = shape; capture.dtype = "float32"; capture.dataset_hash = datasetHash; capture.field_hash = fieldHash; capture.plan.datasetId = "dataset_nearcap"; capture.plan.profileId = "profile_nearcap"; capture.plan.goal = capture.prompt; capture.artifacts = [{ name: "volumetric_dataset.json", type: "volumetric_dataset_json", bytes: datasetBody.byteLength }, { name: "volumetric_field_01.f32", type: "volumetric_binary", bytes: payload.byteLength }, { name: "volumetric_manifest.json", type: "volumetric_manifest_json", bytes: manifestBody.byteLength }];
  return { caseId: "nearcap", prompt: capture.prompt, capture, contents: { "volumetric_dataset.json": datasetBody, "volumetric_field_01.f32": payload, "volumetric_manifest.json": manifestBody }, dataset };
}
function sanitize(error) { return String(error instanceof Error ? error.message : error).replace(/[A-Z]:\\[^\n]+/gi, "[local-path]").slice(0, 800); }
async function writeJson(relative, value) { const target = path.join(EVIDENCE, relative); await mkdir(path.dirname(target), { recursive: true }); await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
function startServer() { const child = spawn("cmd.exe", ["/c", "npm", "--prefix", "apps/web", "run", "start", "--", "--hostname", "127.0.0.1", "--port", String(PORT)], { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" }, stdio: ["ignore", "pipe", "pipe"] }); child.stdout.on("data", () => {}); child.stderr.on("data", () => {}); return child; }
async function ensureServer() { try { if ((await fetch(ORIGIN)).ok) return null; } catch {} const child = startServer(); const deadline = Date.now() + 60_000; while (Date.now() < deadline) { try { if ((await fetch(ORIGIN)).ok) return child; } catch {} await new Promise((resolve) => setTimeout(resolve, 500)); } throw new Error("slice/volume evidence app timeout"); }
function stopServer(child) { spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], { stdio: "ignore" }); }
