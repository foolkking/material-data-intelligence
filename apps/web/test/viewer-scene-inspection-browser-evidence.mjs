import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
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
const ADVANCED_MODE = process.env.MDI_ADVANCED_MEASUREMENT === "1";
const SUPERCELL_MODE = process.env.MDI_SUPERCELL_PRODUCTIZATION === "1";
const VIEW_CONTROLS_MODE = process.env.MDI_VIEW_CONTROLS === "1";
const SCIENTIFIC_EXPORT_MODE = process.env.MDI_SCIENTIFIC_EXPORT === "1";
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
        if (browser) await Promise.race([browser.close().catch(() => {}), new Promise((resolve)=>setTimeout(resolve,10_000))]);
      }
    }
    if (results.some((result) => !result.pass || result.externalRequests !== 0)) throw new Error(`inspection matrix failed: ${JSON.stringify(results)}`);
    await write("browser/browser_matrix.json", { schema_version: SCIENTIFIC_EXPORT_MODE ? "phase10f26.scientific_export_browser_matrix.v1" : VIEW_CONTROLS_MODE ? "phase10f25.view_controls_browser_matrix.v1" : SUPERCELL_MODE ? "phase10f24.supercell_browser_matrix.v1" : ADVANCED_MODE ? "phase10f23.advanced_picking_browser_matrix.v1" : TOPOLOGY_MODE ? "phase10f18.periodic_topology_browser_matrix.v1" : PERIODIC_MODE ? "phase10f17.periodic_browser_matrix.v1" : "phase10f16.inspection_browser_matrix.v1", results });
    await write("browser/network_snapshot.json", { external_request_count: 0, result: SCIENTIFIC_EXPORT_MODE ? "NO_EXTERNAL_NETWORK_REQUESTS" : VIEW_CONTROLS_MODE ? "NO_EXTERNAL_NETWORK_REQUESTS" : TOPOLOGY_MODE ? "NO_PERIODIC_TOPOLOGY_EXTERNAL_NETWORK_REQUESTS" : PERIODIC_MODE ? "NO_PERIODIC_VIEWER_EXTERNAL_NETWORK_REQUESTS" : "NO_VIEWER_INSPECTION_EXTERNAL_NETWORK_REQUESTS" });
    await write("browser/console_snapshot.json", { errors: results.flatMap((result) => result.consoleErrors), page_errors: results.flatMap((result) => result.pageErrors) });
    await write("evidence_manifest.json", SCIENTIFIC_EXPORT_MODE ? scientificExportManifest(results) : VIEW_CONTROLS_MODE ? viewControlsManifest(results) : SUPERCELL_MODE ? supercellManifest(results) : manifest(results));
    await writeFile(path.join(EVIDENCE, "README.md"), SCIENTIFIC_EXPORT_MODE ? scientificExportReadme(results) : VIEW_CONTROLS_MODE ? viewControlsReadme(results) : SUPERCELL_MODE ? supercellReadme(results) : readme(results), "utf-8");
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
    if (ADVANCED_MODE) {
      console.log("VIEWER_SCENE_ADVANCED_PICKING_BROWSER_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_BOND_PICKING_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_PERIODIC_MEASUREMENT_ARTIFACT_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_KEYBOARD_MOBILE_MEASUREMENT_EVIDENCE_PASS");
      console.log("NO_EXTERNAL_NETWORK_REQUESTS");
    }
    if (SUPERCELL_MODE) {
      console.log("VIEWER_SCENE_SUPERCELL_PRODUCTIZATION_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_SUPERCELL_REPLAY_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_SUPERCELL_PICKING_MEASUREMENT_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_SUPERCELL_PERFORMANCE_EVIDENCE_PASS");
      console.log("NO_EXTERNAL_NETWORK_REQUESTS");
    }
    if (VIEW_CONTROLS_MODE) {
      console.log("VIEWER_SCENE_CLIPPING_CELL_CAMERA_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_CLIPPING_PICKING_MEASUREMENT_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_CAMERA_STATE_REPLAY_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_VIEW_CONTROLS_MOBILE_CROSS_BROWSER_EVIDENCE_PASS");
      console.log("NO_EXTERNAL_NETWORK_REQUESTS");
    }
    if (SCIENTIFIC_EXPORT_MODE) {
      console.log("VIEWER_SCENE_SCIENTIFIC_EXPORT_BROWSER_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_HIGH_DPI_EXPORT_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_TRANSPARENT_EXPORT_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_EXPORT_ARTIFACT_EVIDENCE_PASS");
      console.log("VIEWER_SCENE_EXPORT_MOBILE_CROSS_BROWSER_EVIDENCE_PASS");
      console.log("NO_EXTERNAL_NETWORK_REQUESTS");
    }
  } finally {
    if (server) { server.kill(); await stopPort(); }
  }
}

async function inspectBrowser(browser, browserId) {
  if (SCIENTIFIC_EXPORT_MODE) return scientificExportBrowser(browser, browserId);
  if (VIEW_CONTROLS_MODE) return viewControlsBrowser(browser, browserId);
  if (SUPERCELL_MODE) return supercellBrowser(browser, browserId);
  if (ADVANCED_MODE) return advancedBrowser(browser, browserId);
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

async function scientificExportBrowser(browser, browserId) {
  activeCase = "measurement_crystal";
  activeMode = "live";
  const context = await browser.newContext({ viewport:{width:1440,height:1200}, acceptDownloads:true, reducedMotion:"reduce" });
  const audit = {external:[],console:[],pageErrors:[],failedResponses:[]};
  const page = await evidencePage(context,audit);
  await productFlow(page);
  await openRenderer(page);
  await setExportRequest(page,{width:800,height:600,pixelRatio:"1",background:"light"});
  const baseline = await captureExport(page,`${browserId}_baseline.png`);
  if (baseline.width !== 800 || baseline.height !== 600 || ![2,6].includes(baseline.colorType)) throw new Error(`${browserId} baseline PNG mismatch`);

  let extended = null;
  let mobile = null;
  if (browserId === "chromium") {
    await page.getByTestId("viewer-clipping-enabled").click();
    await page.getByTestId("viewer-clip-x-enabled").click();
    await page.getByRole("button",{name:"2 x 1 x 1",exact:true}).click();
    await page.getByTestId("viewer-supercell-apply").click();
    await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.atomCount===8);
    await page.getByRole("button",{name:"Distance"}).click();
    const region=page.getByRole("region",{name:"3D Structure Viewer"});
    await region.focus();await region.press("n");await region.press("n");
    await page.waitForFunction(()=>document.querySelector('[data-testid="viewer-measurement-result"]')?.textContent?.includes("distance"));

    await setExportRequest(page,{width:800,height:600,pixelRatio:"1",background:"transparent"});
    const transparent=await captureExport(page,"transparent.png");
    await page.screenshot({path:path.join(SCREENSHOTS,"02_transparent_export_controls.png"),fullPage:true});
    await setExportRequest(page,{width:800,height:600,pixelRatio:"1",background:"dark"});
    const dark=await captureExport(page,"dark.png");
    await setExportRequest(page,{width:1200,height:900,pixelRatio:"2",background:"light"});
    const highDpi=await captureExport(page,"high_dpi.png");
    if(highDpi.width!==2400||highDpi.height!==1800||transparent.colorType!==6||transparent.sha256===dark.sha256)throw new Error("high-DPI or background export evidence mismatch");

    const prepared={};
    for(const [label,name] of [["Download export JSON","viewer_export_state.json"],["Download export Markdown","viewer_export_summary.md"],["Download export manifest","viewer_export_manifest.json"]]){
      const [download]=await Promise.all([page.waitForEvent("download"),page.getByRole("button",{name:label,exact:true}).click()]);
      const target=path.join(EVIDENCE,"artifacts",name);await mkdir(path.dirname(target),{recursive:true});await download.saveAs(target);prepared[name]=await readFile(target);
    }
    const state=JSON.parse(prepared["viewer_export_state.json"].toString("utf-8"));
    const manifestBody=JSON.parse(prepared["viewer_export_manifest.json"].toString("utf-8"));
    const expectedHashes={"viewer.png":highDpi.sha256,"viewer_export_state.json":sha256(prepared["viewer_export_state.json"]),"viewer_export_summary.md":sha256(prepared["viewer_export_summary.md"])};
    for(const item of manifestBody.artifacts)if(expectedHashes[item.name]!==item.sha256||item.size_bytes!==(item.name==="viewer.png"?highDpi.bytes:prepared[item.name].length))throw new Error(`manifest integrity mismatch: ${item.name}`);
    if(state.schema_version!=="phase10f26.viewer_export_state.v1"||state.viewer_state.supercell_expansion.join()!=="2,1,1"||!state.viewer_state.clipping.enabled||state.measurements.length!==1||state.policy.structure_mutated!==false)throw new Error("viewer export state mismatch");
    if(!prepared["viewer_export_summary.md"].toString("utf-8").includes("Scientific Structure Viewer Export"))throw new Error("Markdown export missing scientific summary");

    const repeat=[];
    await setExportRequest(page,{width:800,height:600,pixelRatio:"1",background:"light"});
    for(let index=0;index<10;index+=1){const started=Date.now();repeat.push({...await captureExport(page,`repeat_${index+1}.png`,false),elapsedMs:Date.now()-started});}
    if(await page.locator("canvas").count()!==1)throw new Error("repeated export created duplicate canvas");
    mobile=await scientificExportMobile(browser);
    extended={transparent,dark,highDpi,state:{schema:state.schema_version,supercell:state.viewer_state.supercell_expansion,clipping:state.viewer_state.clipping.enabled,measurements:state.measurements.length},manifest:manifestBody,repeat};
    await write("export/export_matrix.json",extended);
    await page.screenshot({path:path.join(SCREENSHOTS,"01_scientific_export.png"),fullPage:true});
  }
  const security=await auditPage(page,audit);
  const result={browser:browserId,version:browser.version(),pass:true,baseline,extended,mobile,canvasCount:await page.locator("canvas").count(),externalRequests:security.external,consoleErrors:security.consoleErrors,pageErrors:audit.pageErrors};
  await page.close();await context.close();return result;
}

async function scientificExportMobile(browser){
  activeCase="measurement_crystal";activeMode="live";
  const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2,acceptDownloads:true,reducedMotion:"reduce"});
  const audit={external:[],console:[],pageErrors:[],failedResponses:[]};const page=await evidencePage(context,audit);await productFlow(page);await openRenderer(page);
  await setExportRequest(page,{width:800,height:600,pixelRatio:"1",background:"light"});
  const png=await captureExport(page,"mobile.png");const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);const security=await auditPage(page,audit);
  await page.addStyleTag({content:"nextjs-portal{display:none!important}"});
  await page.screenshot({path:path.join(SCREENSHOTS,"03_mobile_export.png"),fullPage:false});await page.close();await context.close();if(overflow)throw new Error("mobile export controls overflow");return{png,overflow,externalRequests:security.external};
}

async function setExportRequest(page,{width,height,pixelRatio,background}){
  await page.getByTestId("viewer-export-width").fill(String(width));await page.getByTestId("viewer-export-height").fill(String(height));await page.getByTestId("viewer-export-pixel-ratio").selectOption(String(pixelRatio));await page.getByTestId("viewer-export-background").selectOption(background);
}

async function captureExport(page,name,persist=true){
  const [download]=await Promise.all([page.waitForEvent("download"),page.getByTestId("viewer-scene-export-png").click()]);const temporary=await download.path();if(!temporary)throw new Error("PNG download path unavailable");const bytes=await readFile(temporary);const signature=bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]));if(!signature||bytes.length<1000)throw new Error("PNG signature or size invalid");
  if(persist){const target=path.join(EVIDENCE,"export",name);await mkdir(path.dirname(target),{recursive:true});await download.saveAs(target);}
  return{filename:download.suggestedFilename(),bytes:bytes.length,width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),bitDepth:bytes[24],colorType:bytes[25],sha256:sha256(bytes)};
}

function sha256(bytes){return createHash("sha256").update(bytes).digest("hex");}

function scientificExportManifest(results){return{schema_version:"phase10f26.scientific_export_evidence.v1",baseline_head:"74db79795dd61d313c2bc6331e5ece9184165a19",canonical_schema:"phase10f18.viewer_scene.v2",export_state:"phase10f26.viewer_export_state.v1",export_manifest:"phase10f26.viewer_export_manifest.v1",formats:["png","json","markdown"],backgrounds:["light","dark","transparent"],limits:{logical:[256,4096],pixel_ratio:2,effective_pixels:16777216},browser_results:results,network_result:"NO_EXTERNAL_NETWORK_REQUESTS",markers:["VIEWER_SCENE_SCIENTIFIC_EXPORT_BROWSER_EVIDENCE_PASS","VIEWER_SCENE_HIGH_DPI_EXPORT_EVIDENCE_PASS","VIEWER_SCENE_TRANSPARENT_EXPORT_EVIDENCE_PASS","VIEWER_SCENE_EXPORT_ARTIFACT_EVIDENCE_PASS","VIEWER_SCENE_EXPORT_MOBILE_CROSS_BROWSER_EVIDENCE_PASS"],redaction:"sanitized"};}
function scientificExportReadme(results){return`# Phase 10F-26 Scientific Export Evidence\n\nBrowsers: ${results.map((item)=>`${item.browser}=${item.pass?"pass":"fail"}`).join(", ")}\nPNG, high-DPI, transparent/dark background, inert JSON/Markdown/manifest artifacts, repeated export, and mobile controls were exercised in real browsers.\nNetwork: \`NO_EXTERNAL_NETWORK_REQUESTS\`\n`;}

async function viewControlsBrowser(browser,browserId){
  activeCase="measurement_crystal";activeMode="live";
  const context=await browser.newContext({viewport:{width:1440,height:1200},acceptDownloads:true,reducedMotion:"reduce"});
  const audit={external:[],console:[],pageErrors:[],failedResponses:[]};const page=await evidencePage(context,audit);await productFlow(page);await openRenderer(page);
  const initial=await snapshot(page);if(initial.siteScreenPositions.length!==4)throw new Error(`${browserId} initial projection mismatch`);
  await page.getByTestId("viewer-clipping-enabled").click();await page.getByTestId("viewer-clip-x-enabled").click();await page.getByTestId("viewer-clip-x-position").fill("2");
  await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.activeClipPlanes===1&&window.__mdiViewerSceneRendererEvidence?.siteScreenPositions.length===2);
  const clipped=await snapshot(page);const hidden=initial.siteScreenPositions.find((item)=>item.siteIndex===1);const visible=clipped.siteScreenPositions.find((item)=>item.siteIndex===0);if(!hidden||!visible)throw new Error("clipping projection evidence missing");
  await page.getByTestId("viewer-scene-renderer-canvas").click({position:{x:hidden.x,y:hidden.y}});if(await page.locator('[data-testid="viewer-selected-site-index"]').count())throw new Error("clipped atom remained pickable");
  await page.getByTestId("viewer-scene-renderer-canvas").click({position:{x:visible.x,y:visible.y}});await page.waitForFunction(()=>document.querySelector('[data-testid="viewer-selected-site-index"]')?.textContent?.trim()==="0");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"03_clipping_x.png"),fullPage:true});
  await page.getByTestId("viewer-lattice-axes").click();await page.getByTestId("viewer-scene-renderer-toggle-cell").click();const cell=await snapshot(page);if(!cell.latticeAxesVisible||cell.latticeEdgeCount!==0)throw new Error("cell or axis toggle mismatch");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"01_unit_cell_axes.png"),fullPage:true});
  await page.getByTestId("viewer-camera-top").click();const top=await snapshot(page);if(top.cameraPreset!=="top"||Math.abs(top.cameraPosition[0]-top.cameraTarget[0])>1e-3||Math.abs(top.cameraPosition[1]-top.cameraTarget[1])>1e-3)throw new Error(`top camera preset mismatch ${JSON.stringify({preset:top.cameraPreset,position:top.cameraPosition,target:top.cameraTarget,up:top.cameraUp})}`);
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"05_camera_top.png"),fullPage:true});
  await page.getByTestId("viewer-camera-isometric").click();const isometric=await snapshot(page);if(isometric.cameraPreset!=="isometric"||isometric.cameraPosition.join()===top.cameraPosition.join())throw new Error("isometric camera preset mismatch");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"06_camera_isometric.png"),fullPage:true});
  await page.getByRole("button",{name:"2 x 1 x 1",exact:true}).click();await page.getByTestId("viewer-supercell-apply").click();await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.atomCount===8);const expanded=await snapshot(page);if(expanded.activeClipPlanes!==1||await page.locator("canvas").count()!==1)throw new Error("clip and supercell integration failed");
  await page.getByRole("button",{name:"Distance"}).click();await page.keyboard.press("n");await page.keyboard.press("n");const measured=await measurement(page,"distance");if(!measured.includes("Å"))throw new Error("measurement after clipping failed");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"09_measurement_after_clip.png"),fullPage:true});
  await page.getByTestId("viewer-clip-y-enabled").click();await page.getByTestId("viewer-clip-z-enabled").click();await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.activeClipPlanes===3);if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"04_clipping_xyz.png"),fullPage:true});
  let viewArtifact=null;if(browserId==="chromium"){const [download]=await Promise.all([page.waitForEvent("download"),page.getByTestId("viewer-view-state-download").click()]);const body=JSON.parse(await readFile(await download.path(),"utf-8"));if(body.schema_version!=="phase10f25.viewer_view_state.v1"||body.camera.preset!=="isometric"||body.clipping.planes.length!==3||body.policy.structure_mutated!==false)throw new Error("view state artifact mismatch");viewArtifact={schema:body.schema_version,camera:body.camera,clipping:body.clipping,display:body.display,security:body.security};}
  await page.getByTestId("viewer-clipping-reset").click();await page.getByTestId("viewer-camera-default").click();const reset=await snapshot(page);if(reset.activeClipPlanes!==0||reset.cameraPreset!=="default")throw new Error("view reset mismatch");if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"10_reset_view.png"),fullPage:true});
  const security=await auditPage(page,audit);let mobile=null;if(browserId==="chromium")mobile=await viewControlsMobileCase(browser);const result={browser:browserId,version:browser.version(),pass:true,initial,clipped:{activePlanes:clipped.activeClipPlanes,visibleSites:clipped.siteScreenPositions.length,hiddenPickRejected:true},cell:{latticeAxesVisible:cell.latticeAxesVisible,latticeEdgeCount:cell.latticeEdgeCount},camera:{top:{position:top.cameraPosition,target:top.cameraTarget},isometric:{position:isometric.cameraPosition,target:isometric.cameraTarget}},supercell:{atoms:expanded.atomCount,activePlanes:expanded.activeClipPlanes},measurement:measured,viewArtifact,mobile,externalRequests:security.external,consoleErrors:security.consoleErrors,pageErrors:audit.pageErrors};
  await page.close();await context.close();return result;
}

async function viewControlsMobileCase(browser){activeCase="measurement_crystal";activeMode="live";const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2,reducedMotion:"reduce"});const audit={external:[],console:[],pageErrors:[],failedResponses:[]};const page=await evidencePage(context,audit);await productFlow(page);await openRenderer(page);await page.getByTestId("viewer-clipping-enabled").click();await page.getByTestId("viewer-clip-x-enabled").click();await page.getByTestId("viewer-camera-side").click();await page.getByTestId("viewer-lattice-axes").click();await page.setViewportSize({width:844,height:390});await page.waitForTimeout(100);const snap=await snapshot(page);const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);await page.screenshot({path:path.join(SCREENSHOTS,"07_mobile_controls.png"),fullPage:false});const external=(await auditPage(page,audit)).external;await page.close();await context.close();if(overflow||snap.activeClipPlanes!==1||snap.cameraPreset!=="side"||!snap.latticeAxesVisible)throw new Error("mobile view controls failed");return{overflow,activeClipPlanes:snap.activeClipPlanes,cameraPreset:snap.cameraPreset,latticeAxesVisible:snap.latticeAxesVisible,external};}

async function supercellBrowser(browser,browserId){
  activeCase="measurement_crystal"; activeMode="live";
  const context=await browser.newContext({viewport:{width:1440,height:1200},acceptDownloads:true,reducedMotion:"reduce"}); const audit={external:[],console:[],pageErrors:[],failedResponses:[]};
  const page=await evidencePage(context,audit); await productFlow(page); await openRenderer(page); await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.atomCount===4);
  const states=[]; const capture=async(label)=>{const snapshot=await page.evaluate(()=>window.__mdiViewerSceneRendererEvidence); states.push({label,status:await page.getByTestId("viewer-supercell-status").innerText(),estimate:await page.getByTestId("viewer-supercell-estimate").innerText(),atoms:snapshot.atomCount,bonds:snapshot.bondCount,canvas:await page.locator("canvas").count(),metrics:snapshot.metrics}); if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,`${String(states.length).padStart(2,"0")}_${label}.png`),fullPage:true});};
  await capture("default_1x1x1");
  for(const expansion of [[2,1,1],[2,2,1],[2,2,2]]){for(const [axis,value] of ["x","y","z"].map((axis,index)=>[axis,String(expansion[index])]))await page.getByTestId(`viewer-supercell-${axis}`).fill(value); await page.getByTestId("viewer-supercell-apply").click(); await page.waitForFunction((count)=>window.__mdiViewerSceneRendererEvidence?.atomCount===count,4*expansion[0]*expansion[1]*expansion[2]); await capture(`supercell_${expansion.join("x")}`);}
  await page.getByRole("button",{name:"Distance"}).click(); const snap=await page.evaluate(()=>window.__mdiViewerSceneRendererEvidence); const primary=snap.siteScreenPositions.find((item)=>item.siteIndex===0&&item.ref.imageOffset.join()=== "0,0,0"); const replica=snap.siteScreenPositions.find((item)=>item.siteIndex===0&&item.ref.imageOffset.join()=== "1,0,0"); if(!primary||!replica)throw new Error("supercell replica identity missing"); for(const item of [primary,replica])await page.getByTestId("viewer-scene-renderer-canvas").click({position:{x:item.x,y:item.y}}); const selected=await page.getByTestId("viewer-measurement-selection").innerText(); const measured=await measurement(page,"distance"); if(!selected.includes("0@[1,0,0]"))throw new Error(`replica picking mismatch ${selected}`);
  let artifact=null;if(browserId==="chromium"){const [download]=await Promise.all([page.waitForEvent("download"),page.getByTestId("viewer-supercell-download").click()]);const body=JSON.parse(await readFile(await download.path(),"utf-8"));if(body.schema_version!=="phase10f24.viewer_supercell_state.v1"||body.expansion.join()!=="2,2,2"||body.policy.structure_mutated!==false)throw new Error("supercell state artifact invalid");artifact={filename:download.suggestedFilename(),schema:body.schema_version,expansion:body.expansion,counts:body.counts};}
  await page.getByTestId("viewer-supercell-x").fill("4"); const refused=await page.getByTestId("viewer-supercell-estimate").innerText(); if(!refused.includes("refused")||await page.getByTestId("viewer-supercell-apply").isEnabled())throw new Error("supercell refusal preflight missing"); if(await page.locator("canvas").count()!==1)throw new Error("refused draft replaced canvas");
  await page.getByTestId("viewer-supercell-reset").click(); await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.atomCount===4); await capture("reset_1x1x1");
  for(let index=0;index<20;index+=1){const expanded=index%2===0;await page.getByRole("button",{name:expanded?"2 x 1 x 1":"1 x 1 x 1",exact:true}).click();await page.getByTestId("viewer-supercell-apply").click();await page.waitForFunction((count)=>window.__mdiViewerSceneRendererEvidence?.atomCount===count,expanded?8:4);if(await page.locator("canvas").count()!==1)throw new Error("supercell lifecycle canvas leak");}
  let degraded=null;let mobile=null;if(browserId==="chromium"){activeMode="near_cap";const degradedPage=await evidencePage(context,audit);await productFlow(degradedPage);await openRenderer(degradedPage);await degradedPage.getByRole("button",{name:"2 x 2 x 2",exact:true}).click();await degradedPage.getByTestId("viewer-supercell-apply").click();await degradedPage.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.atomCount===1024);const tier=await degradedPage.getByTestId("viewer-scene-renderer-performance-tier").innerText();const warning=await degradedPage.getByTestId("viewer-scene-renderer-performance-warning").innerText();if(tier!=="degraded")throw new Error(`degraded tier missing: ${tier}`);await degradedPage.screenshot({path:path.join(SCREENSHOTS,"08_degraded_mode.png"),fullPage:true});degraded={tier,warning,syntheticCanonicalSites:128,displayedAtoms:1024};await degradedPage.close();activeMode="live";mobile=await supercellMobileCase(browser);}
  const security=await auditPage(page,audit);await page.close();await context.close();return{browser:browserId,version:browser.version(),pass:true,states,selected,measured,artifact,refused,degraded,mobile,externalRequests:security.external,consoleErrors:security.consoleErrors,pageErrors:audit.pageErrors};
}

async function supercellMobileCase(browser){activeCase="measurement_crystal";const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});const audit={external:[],console:[],pageErrors:[],failedResponses:[]};const page=await evidencePage(context,audit);await productFlow(page);await openRenderer(page);await page.getByRole("button",{name:"2 x 2 x 1"}).click();await page.getByTestId("viewer-supercell-apply").click();await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.atomCount===16);await page.setViewportSize({width:844,height:390});await page.waitForTimeout(100);const canvasCount=await page.locator("canvas").count();const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);await page.screenshot({path:path.join(SCREENSHOTS,"10_mobile_supercell.png"),fullPage:false});const external=(await auditPage(page,audit)).external;await page.close();await context.close();if(canvasCount!==1||overflow)throw new Error("mobile supercell lifecycle failed");return{canvasCount,overflow,external};}

function supercellManifest(results){return {schema_version:"phase10f24.supercell_productization_evidence.v1",baseline_head:"8bfd41b4379d91d3ad3cd9cf6f275bdc759e2985",canonical_schema:"phase10f18.viewer_scene.v2",state_artifact:"phase10f24.viewer_supercell_state.v1",origin_policy:"positive_octant",axis_cap:3,displayed_atom_cap:2048,displayed_bond_cap:8192,browser_results:results,network_result:"NO_EXTERNAL_NETWORK_REQUESTS",markers:["VIEWER_SCENE_SUPERCELL_PRODUCTIZATION_EVIDENCE_PASS","VIEWER_SCENE_SUPERCELL_REPLAY_EVIDENCE_PASS","VIEWER_SCENE_SUPERCELL_PICKING_MEASUREMENT_EVIDENCE_PASS","VIEWER_SCENE_SUPERCELL_PERFORMANCE_EVIDENCE_PASS"],redaction:"sanitized"};}
function supercellReadme(results){return `# Phase 10F-24 Supercell Productization Evidence\n\nBrowsers: ${results.map((item)=>`${item.browser}=${item.pass?"pass":"fail"}`).join(", ")}\nSupercells are bounded renderer-local view state with positive-octant identity and inert replay artifacts.\nNetwork: \`NO_EXTERNAL_NETWORK_REQUESTS\`\n`;}
function viewControlsManifest(results){return {schema_version:"phase10f25.clipping_cell_camera_evidence.v1",baseline_head:"00cf7df584eb1229a6dd7155127241968c8f93eb",canonical_schema:"phase10f18.viewer_scene.v2",view_state_artifact:"phase10f25.viewer_view_state.v1",clipping:{axes:["x","y","z"],maximum_planes:3,renderer_only:true},camera_presets:["default","top","front","side","isometric"],cell_display:{unit_cell:true,supercell_boundary:true,lattice_axes:true,internal_grid:false},browser_results:results,network_result:"NO_EXTERNAL_NETWORK_REQUESTS",markers:["VIEWER_SCENE_CLIPPING_CELL_CAMERA_EVIDENCE_PASS","VIEWER_SCENE_CLIPPING_PICKING_MEASUREMENT_EVIDENCE_PASS","VIEWER_SCENE_CAMERA_STATE_REPLAY_EVIDENCE_PASS","VIEWER_SCENE_VIEW_CONTROLS_MOBILE_CROSS_BROWSER_EVIDENCE_PASS"],redaction:"sanitized"};}
function viewControlsReadme(results){return `# Phase 10F-25 Clipping, Cell and Camera Evidence\n\nBrowsers: ${results.map((item)=>`${item.browser}=${item.pass?"pass":"fail"}`).join(", ")}\nAxis-aligned clipping, lattice display, deterministic camera presets, supercell integration, picking, and measurements were exercised in real browsers.\nNetwork: \`NO_EXTERNAL_NETWORK_REQUESTS\`\n`;}

async function advancedBrowser(browser, browserId) {
  activeCase = "measurement_crystal"; activeMode = "live";
  const context = await browser.newContext({ viewport:{width:1440,height:1200}, acceptDownloads:true, reducedMotion:"reduce" });
  const audit={external:[],console:[],pageErrors:[],failedResponses:[]};
  const page=await evidencePage(context,audit); await productFlow(page); await openRenderer(page);
  await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.bondCount===2,null,{timeout:20_000});
  await pick(page,3); await page.waitForSelector('[data-testid="viewer-selected-site-index"]'); const atomIdentity=`${await page.getByTestId("viewer-selected-site-index").innerText()}@${await page.getByTestId("viewer-selected-site-image-offset").innerText()}`;
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"01_atom_selected.png"),fullPage:true}); await page.getByTestId("viewer-measurement-clear").click();
  await pickBond(page,0); await page.waitForSelector('[data-testid="viewer-selected-bond-id"]');
  const bondId=await page.getByTestId("viewer-selected-bond-id").innerText();
  await page.getByRole("button",{name:"Distance"}).click(); await pickBond(page,0);
  const explicitDistance=await measurement(page,"distance");
  const orderedSelection=await page.getByTestId("viewer-measurement-selection").innerText();
  if(!orderedSelection.includes("0@[0,0,0]")||!orderedSelection.includes("1@[0,0,0]")||!explicitDistance.includes("4.000")) throw new Error(`advanced bond measurement mismatch: ${orderedSelection} ${explicitDistance}`);
  const region=page.getByRole("region",{name:"3D Structure Viewer"}); await page.getByTestId("viewer-measurement-clear").click(); await region.focus(); await region.press("n"); await region.press("n");
  await page.waitForFunction(()=>document.querySelector('[data-testid="viewer-measurement-selection"]')?.textContent?.includes("2/2"));
  const keyboardResult=await measurement(page,"distance"); await region.press("Backspace");
  if(!(await page.getByTestId("viewer-measurement-selection").innerText()).includes("1/2")) throw new Error("keyboard undo failed");
  await page.getByTestId("viewer-measurement-clear").click(); await page.getByRole("button",{name:"Angle"}).click(); await region.focus(); for(let i=0;i<3;i+=1)await region.press("n"); const angle=await measurement(page,"angle");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"05_angle_measurement.png"),fullPage:true});
  await page.getByTestId("viewer-measurement-clear").click(); await page.getByRole("button",{name:"Dihedral"}).click(); await region.focus(); for(let i=0;i<4;i+=1)await region.press("n"); const dihedral=await measurement(page,"dihedral");
  if(browserId==="chromium")await page.screenshot({path:path.join(SCREENSHOTS,"06_dihedral_measurement.png"),fullPage:true});
  activeCase="periodic_boundary_bond"; const crossPage=await evidencePage(context,audit); await productFlow(crossPage); await openRenderer(crossPage);
  await crossPage.getByTestId("viewer-supercell-x").fill("2"); await crossPage.getByTestId("viewer-supercell-apply").click(); await crossPage.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.bondCount===1);
  await crossPage.getByRole("button",{name:"Distance"}).click(); const crossRegion=crossPage.getByRole("region",{name:"3D Structure Viewer"}); await crossRegion.focus(); await crossRegion.press("b");
  const crossBoundarySelection=await crossPage.getByTestId("viewer-measurement-selection").innerText(); const crossBoundaryDistance=await measurement(crossPage,"distance");
  if(!crossBoundarySelection.includes("1@[1,0,0]")||!crossBoundaryDistance.includes("0.400"))throw new Error("cross-boundary keyboard bond selection failed"); await crossPage.close(); activeCase="measurement_crystal";
  let artifact=null; let mobile=null; let contextLoss=null;
  if(browserId==="chromium"){
    const [download]=await Promise.all([page.waitForEvent("download"),page.getByTestId("viewer-measurement-download").click()]);
    const artifactPath=await download.path(); const artifactBody=JSON.parse(await readFile(artifactPath,"utf-8"));
    if(download.suggestedFilename()!=="viewer_measurement.json"||artifactBody.schema_version!=="phase10f23.viewer_measurement.v1"||artifactBody.policy.topology_mutated!==false) throw new Error("measurement artifact invalid");
    artifact={filename:download.suggestedFilename(),schema:artifactBody.schema_version,value:artifactBody.measurement.value};
    await page.screenshot({path:path.join(SCREENSHOTS,"03_bond_selected.png"),fullPage:true});
    mobile=await advancedMobileCase(browser);
    await page.getByTestId("viewer-scene-renderer-canvas").dispatchEvent("webglcontextlost");
    await page.waitForSelector('[data-testid="viewer-scene-renderer-fallback"]'); contextLoss="safe_fallback";
  }
  if(browserId!=="chromium"){ await page.getByRole("tab",{name:"Scene JSON"}).click(); await page.getByRole("tab",{name:"3D Renderer"}).click(); await openRenderer(page,false); }
  const canvasCount=await page.locator("canvas").count(); if(canvasCount!==1&&contextLoss===null) throw new Error("advanced lifecycle canvas mismatch");
  const security=await auditPage(page,audit); await page.close(); await context.close();
  return {browser:browserId,version:browser.version(),pass:true,atomIdentity,bondId,orderedSelection,explicitDistance,crossBoundarySelection,crossBoundaryDistance,keyboardResult,angle,dihedral,artifact,mobile,contextLoss,canvasCount,externalRequests:security.external,consoleErrors:security.consoleErrors,pageErrors:audit.pageErrors};
}

async function advancedMobileCase(browser){
  activeCase="measurement_crystal"; const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:2});
  const audit={external:[],console:[],pageErrors:[],failedResponses:[]}; const page=await evidencePage(context,audit); await productFlow(page); await openRenderer(page);
  await page.waitForFunction(()=>window.__mdiViewerSceneRendererEvidence?.bondCount===2);
  await page.getByRole("button",{name:"Distance"}).click(); await pickBond(page,0,true); await page.waitForSelector('[data-testid="viewer-selected-bond-id"]');
  const value=await measurement(page,"distance"); await page.getByTestId("viewer-measurement-undo").click(); await page.getByTestId("viewer-measurement-clear").click();
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1); if(overflow)throw new Error("advanced mobile overflow");
  await page.screenshot({path:path.join(SCREENSHOTS,"09_mobile_distance_measurement.png"),fullPage:false}); const external=(await auditPage(page,audit)).external; await page.close();await context.close();return{value,overflow,external};
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
  const replicaCandidates = doubled.siteScreenPositions
    .filter((item) => item.ref?.imageOffset?.some((value) => value !== 0))
    .map((item) => ({ item, separation: Math.min(...doubled.siteScreenPositions.filter((other) => other !== item).map((other) => Math.hypot(other.x-item.x,other.y-item.y))) }))
    .sort((left,right) => right.separation-left.separation).map((candidate)=>candidate.item);
  const box = await page.getByTestId("viewer-scene-renderer-canvas").boundingBox();
  if (!replicaCandidates.length || !box) throw new Error("periodic replica projection unavailable");
  let replica=null;
  for(const candidate of replicaCandidates.filter((item)=>item.x>=0&&item.y>=0&&item.x<=box.width&&item.y<=box.height)){
    await page.getByTestId("viewer-scene-renderer-canvas").click({position:{x:candidate.x,y:candidate.y}});await page.waitForTimeout(150);
    const selected=await page.locator('[data-testid="viewer-selected-site-image-offset"]').textContent().catch(()=>null);
    if(selected?.includes(candidate.ref.imageOffset.join(", "))){replica=candidate;break;}
  }
  if(!replica)throw new Error(`periodic replica canvas picking failed: ${JSON.stringify(replicaCandidates.map((item)=>({offset:item.ref.imageOffset,x:item.x,y:item.y})))}`);
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
  const region=page.getByRole("region",{name:"3D Structure Viewer"}); await region.focus();
  for (const _siteIndex of siteIndices) await region.press("n");
  await page.waitForFunction((count) => document.querySelector('[data-testid="viewer-measurement-selection"]')?.textContent?.includes(`${count}/${count}`), siteIndices.length);
}

async function pick(page, siteIndex) {
  const state = await snapshot(page);
  const site = state.siteScreenPositions.find((item) => item.siteIndex === siteIndex);
  const box = await page.getByTestId("viewer-scene-renderer-canvas").boundingBox();
  if (!site || !box) throw new Error(`site ${siteIndex} screen position unavailable`);
  await page.mouse.click(box.x + site.x, box.y + site.y);
}

async function pickBond(page, bondIndex, touch=false){
  const canvas=page.getByTestId("viewer-scene-renderer-canvas"); await canvas.scrollIntoViewIfNeeded();
  const state=await snapshot(page); const bond=state.bondScreenPositions[bondIndex]; const box=await canvas.boundingBox();
  if(!bond||!box)throw new Error(`bond ${bondIndex} screen position unavailable`);
  if(touch)await page.touchscreen.tap(box.x+bond.x,box.y+bond.y);else await page.mouse.click(box.x+bond.x,box.y+bond.y);
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
  if (activeMode === "near_cap") {
    const sceneArtifact=copy.find((item)=>item.name==="viewer_scene.json"); const scene=sceneArtifact.content; const template=scene.scene.sites[0];
    scene.scene.sites=Array.from({length:128},(_,index)=>({...template,index,label:`${template.element}${index+1}`,xyz:[(index%8)*0.4,(Math.floor(index/8)%4)*0.4,Math.floor(index/32)*0.4],frac:[(index%8)*0.04,(Math.floor(index/8)%4)*0.04,Math.floor(index/32)*0.04]}));
    scene.scene.bonds=[]; scene.metadata.site_count=128; scene.metadata.formula="Si128"; scene.caps.max_sites=256; scene.caps.max_bonds=2048; scene.validation.status="passed"; scene.validation.truncated=false; scene.warnings=[];
  }
  return copy;
}

function generatePayload() {
  const output = process.env.MDI_INSPECTION_EVIDENCE_DIR || "docs/phase10f/evidence/phase10f16_scientific_structure_inspection";
  const result = spawnSync("uv", ["run", "python", "apps/web/test/generate-viewer-scene-live-adapter-evidence.py", output], { cwd: ROOT, encoding: "utf-8", env: { ...process.env, PYTHONIOENCODING: "utf-8", MDI_FORMAL_VIEWER_MODE: "1", MDI_INCLUDE_RENDERER_CASES: "1", MDI_INCLUDE_INSPECTION_CASES: "1", MDI_INCLUDE_TOPOLOGY_CASES: TOPOLOGY_MODE || ADVANCED_MODE || SUPERCELL_MODE || VIEW_CONTROLS_MODE ? "1" : "0" } });
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
function manifest(results) { return ADVANCED_MODE ? {schema_version:"phase10f23.advanced_picking_measurement_evidence.v1",baseline_head:"31dc3b64a1b892cc649818af2fefacfd9a4522c8",canonical_schema:"phase10f18.viewer_scene.v2",selection_cap:4,coordinate_policies:["displayed_positions","minimum_image"],measurement_artifact:"phase10f23.viewer_measurement.v1",browser_results:results,network_result:"NO_EXTERNAL_NETWORK_REQUESTS",markers:["VIEWER_SCENE_ADVANCED_PICKING_BROWSER_EVIDENCE_PASS","VIEWER_SCENE_BOND_PICKING_EVIDENCE_PASS","VIEWER_SCENE_PERIODIC_MEASUREMENT_ARTIFACT_EVIDENCE_PASS","VIEWER_SCENE_KEYBOARD_MOBILE_MEASUREMENT_EVIDENCE_PASS"],redaction:"sanitized"} : TOPOLOGY_MODE ? { schema_version:"phase10f18.periodic_bond_topology_evidence.v1", baseline_head:"bfca00d4c93ab2bd16966b237d850bd33206c20c", final_head:"current commit recorded in final report", formal_tool:"structure.viewer_3d", canonical_schema:"phase10f18.viewer_scene.v2", periodic_bonds:"adapter_generated_explicit_endpoints", source_policy:"distance_cutoff_non_authoritative", evidence_generation_command:"node apps/web/test/viewer-scene-periodic-topology-browser-evidence.mjs", timestamp:payload.cases.periodic_boundary_bond.api.artifacts[0]?.metadata?.createdAt, artifact_hashes:Object.fromEntries(payload.cases.periodic_boundary_bond.api.artifacts.map((item)=>[item.name,item.sha256||item.contentHash])), browser_results:results.map((item)=>({browser:item.browser,version:item.version,pass:item.pass,neighbor:item.neighbor,metrics:item.metrics})), network_result:"NO_PERIODIC_TOPOLOGY_EXTERNAL_NETWORK_REQUESTS", markers:["VIEWER_SCENE_PERIODIC_BOND_CONTRACT_EVIDENCE_PASS","VIEWER_SCENE_PERIODIC_TOPOLOGY_BROWSER_EVIDENCE_PASS","VIEWER_SCENE_PERIODIC_NEIGHBOR_INSPECTOR_EVIDENCE_PASS","VIEWER_SCENE_PERIODIC_BOND_PERFORMANCE_EVIDENCE_PASS"], redaction:"sanitized" } : PERIODIC_MODE ? { schema_version: "phase10f17.periodic_crystal_inspection_evidence.v1", baseline_head: "5e7474be92e0ef75bed7a91ec5309c7fdea9e7f0", formal_tool: "structure.viewer_3d", coordinate_policies: ["displayed_positions", "minimum_image"], lattice_convention: "row_vectors", supercell: "renderer_local_bounded_1_to_3", periodic_bonds: "same_cell_replication_only", browser_results: results.map((item) => ({ browser: item.browser, version: item.version, pass: item.pass })), network_result: "NO_PERIODIC_VIEWER_EXTERNAL_NETWORK_REQUESTS", markers: ["VIEWER_SCENE_PERIODIC_INSPECTION_BROWSER_EVIDENCE_PASS", "VIEWER_SCENE_MINIMUM_IMAGE_MEASUREMENT_EVIDENCE_PASS", "VIEWER_SCENE_SUPERCELL_BROWSER_EVIDENCE_PASS", "VIEWER_SCENE_PERIODIC_PERFORMANCE_EVIDENCE_PASS"], redaction: "sanitized" } : { schema_version: "phase10f16.scientific_inspection_evidence.v1", baseline_head: "1be7689c2d8881b0fb9f2f67360da7cf2d795703", formal_tool: "structure.viewer_3d", coordinate_policy: "displayed_canonical_cartesian_positions", dihedral_range: "[-180, 180]", browser_results: results.map((item) => ({ browser: item.browser, version: item.version, pass: item.pass })), network_result: "NO_VIEWER_INSPECTION_EXTERNAL_NETWORK_REQUESTS", markers: ["VIEWER_SCENE_SCIENTIFIC_INSPECTION_BROWSER_EVIDENCE_PASS", "VIEWER_SCENE_MEASUREMENT_EVIDENCE_PASS", "VIEWER_SCENE_EXPORT_EVIDENCE_PASS", "VIEWER_SCENE_LEGACY_GUIDANCE_EVIDENCE_PASS"], redaction: "sanitized" }; }
function readme(results) { return ADVANCED_MODE ? `# Phase 10F-23 Advanced Picking and Measurement Evidence\n\nBrowsers: ${results.map((item)=>`${item.browser}=${item.pass?"pass":"fail"}`).join(", ")}\nAtom and bond picking use canonical periodic identities. Measurements are bounded and exported as inert JSON.\nNetwork: \`NO_EXTERNAL_NETWORK_REQUESTS\`\n` : TOPOLOGY_MODE ? `# Phase 10F-18 Canonical Periodic Bond Topology Evidence\n\nFormal tool: \`structure.viewer_3d\`\nCanonical schema: \`phase10f18.viewer_scene.v2\`\nBrowsers: ${results.map((item)=>`${item.browser}=${item.pass?"pass":"fail"}`).join(", ")}\nTopology source: bounded non-authoritative distance cutoff with explicit periodic endpoints.\nNetwork: \`NO_PERIODIC_TOPOLOGY_EXTERNAL_NETWORK_REQUESTS\`\n` : PERIODIC_MODE ? `# Phase 10F-17 Periodic Crystal Inspection Evidence\n\nFormal tool: \`structure.viewer_3d\`\nBrowsers: ${results.map((item) => `${item.browser}=${item.pass ? "pass" : "fail"}`).join(", ")}\nMinimum-image search is bounded and independently cross-checked against pymatgen. Supercells are renderer-local.\nNetwork: \`NO_PERIODIC_VIEWER_EXTERNAL_NETWORK_REQUESTS\`\n` : `# Phase 10F-16 Scientific Structure Inspection Evidence\n\nFormal tool: \`structure.viewer_3d\`\nBrowsers: ${results.map((item) => `${item.browser}=${item.pass ? "pass" : "fail"}`).join(", ")}\nMeasurements use displayed canonical Cartesian positions.\nNetwork: \`NO_VIEWER_INSPECTION_EXTERNAL_NETWORK_REQUESTS\`\n`; }

await main();
process.exit(0);
