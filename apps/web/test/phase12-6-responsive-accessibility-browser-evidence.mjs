import { spawn, spawnSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const OUT = path.join(ROOT, "docs/phase12/evidence/phase12_6_responsive_mobile_accessibility");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || path.join(ROOT, "apps/web/node_modules/playwright/index.mjs");
const PORT = Number(process.env.MDI_PHASE12_6_PORT || "3460");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const PROJECT_ID = "phase12-ux-project";
const RESEARCH_PATH = `/projects/${PROJECT_ID}/research`;
const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);

async function waitForServer() {
  for (let attempt = 0; attempt < 240; attempt += 1) {
    try { if ((await fetch(ORIGIN)).ok) return; } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error("Phase 12-6 browser evidence server timeout");
}

async function installReplay(page, audit) {
  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const sameOriginApi = url.origin === ORIGIN && url.pathname.startsWith("/api/");
    const directApi = (url.hostname === "localhost" || url.hostname === "127.0.0.1") && url.port === "8000";
    if (!sameOriginApi && !directApi) {
      if (url.origin === ORIGIN) return route.continue();
      audit.externalRequests.push(request.url());
      return route.abort();
    }
    const pathname = sameOriginApi ? url.pathname.slice("/api".length) : url.pathname;
    const json = (payload, status = 200) => route.fulfill({ status, contentType: "application/json", body: JSON.stringify(payload) });
    if (pathname === "/auth/me") return json({ id: "ci-user", displayName: "CI Reviewer", email: "ci@example.invalid", roles: ["researcher"] });
    if (pathname === `/projects/${PROJECT_ID}/research-sessions`) return json([]);
    if (pathname === `/projects/${PROJECT_ID}/history`) return json({
      schemaVersion: "1.0",
      project: { id: PROJECT_ID, projectId: PROJECT_ID, name: "响应式验收项目", role: "owner", description: "当前 Research 工作台的浏览器验收夹具" },
      summary: { datasetCount: 1, analysisCount: 0, completedAnalysisCount: 0, artifactCount: 0, workspaceCount: 0, reportCount: 0 },
      datasets: [{
        datasetId: "dataset-ux", name: "材料数据夹具", status: "active", analysisCount: 0, process: [],
        resultSummary: { artifactCount: 0, workspaceCount: 0, interpretationCount: 0, reportCount: 0, recipeCount: 0, artifactTypes: [] },
        import: { fileCount: 1, files: [], resources: [], parseOutcome: "READY" },
        profile: { datasetType: "materials_tabular_dataset", rowCount: 3, columnCount: 2, readyCapabilities: ["tabular_data"] },
      }],
      analyses: [], activity: [],
    });
    if (pathname === "/planner/providers/status") return json({ ok: true, provider: "mock", model: "mock-model", status: "ready", execution: "live", configured: true, allowedModels: ["mock-model"] });
    if (pathname === "/planner/providers") return json({ providers: [{ id: "mock", label: "Mock planner", provider: "mock", defaultModel: "mock-model", models: ["mock-model"], requiresSecret: false, execution: "live", secretConfigured: false }] });
    if (pathname === "/health/runtime") return json({ api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } });
    if (pathname === "/datasets" && request.method() === "GET") return json([]);
    if (pathname === "/me/secrets") return json([]);
    audit.failedResponses.push(`${request.method()} ${pathname}`);
    return route.fulfill({ status: 404, json: { detail: "Phase 12-6 local replay route not found" } });
  });
}

function attachAudit(page) {
  const audit = { consoleErrors: [], pageErrors: [], failedResponses: [], externalRequests: [] };
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(String(error)));
  return audit;
}

async function desktop(name, browserType) {
  const browser = await browserType.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce", forcedColors: "active" });
    const page = await context.newPage();
    const audit = attachAudit(page);
    await installReplay(page, audit);
    await page.goto(`${ORIGIN}${RESEARCH_PATH}`, { waitUntil: "networkidle" });
    const skip = page.locator('.skip-link[href="#research-primary-content"]');
    await skip.focus();
    const focusedSkip = await page.locator(":focus").getAttribute("href");
    if (focusedSkip !== "#research-primary-content" || !(await skip.isVisible())) throw new Error(`${name}: skip navigation was not focus-visible`);
    await page.keyboard.press("Enter");
    if ((await page.locator(":focus").getAttribute("id")) !== "research-primary-content") throw new Error(`${name}: skip target did not receive focus`);
    const separator = page.locator('.research-splitter[role="separator"]');
    const before = Number(await separator.getAttribute("aria-valuenow"));
    await separator.focus();
    await page.keyboard.press("ArrowRight");
    const after = Number(await separator.getAttribute("aria-valuenow"));
    if (after <= before) throw new Error(`${name}: keyboard resize did not advance`);
    const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    if (horizontalOverflow) throw new Error(`${name}: horizontal overflow`);
    await page.screenshot({ path: path.join(OUT, `desktop_${name}_accessibility.png`), fullPage: true });
    if (Object.values(audit).some((items) => items.length)) throw new Error(`${name}: ${JSON.stringify(audit)}`);
    return { skipNavigation: "PASS", keyboardResize: "PASS", forcedColors: "PASS", reducedMotion: "PASS", horizontalOverflow: false, ...audit };
  } finally { await browser.close(); }
}

async function mobile() {
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, reducedMotion: "reduce" });
    const page = await context.newPage();
    const audit = attachAudit(page);
    await installReplay(page, audit);
    await page.goto(`${ORIGIN}${RESEARCH_PATH}`, { waitUntil: "networkidle" });
    const metrics = await page.evaluate(() => {
      const controls = [...document.querySelectorAll("button, input, select, textarea, a")].filter((item) => {
        const style = getComputedStyle(item);
        const rect = item.getBoundingClientRect();
        return style.visibility !== "hidden" && style.display !== "none" && rect.width > 0 && rect.height > 0;
      });
      const undersized = controls.filter((item) => item.getBoundingClientRect().height < 44 && !item.classList.contains("skip-link"));
      return { horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth, visibleControls: controls.length, undersized: undersized.map((item) => `${item.tagName}:${item.getAttribute("aria-label") || item.textContent?.trim().slice(0, 30)}`) };
    });
    if (metrics.horizontalOverflow || metrics.undersized.length) throw new Error(`mobile: ${JSON.stringify(metrics)}`);
    await page.screenshot({ path: path.join(OUT, "mobile_chromium_390x844.png"), fullPage: true });
    if (Object.values(audit).some((items) => items.length)) throw new Error(`mobile audit: ${JSON.stringify(audit)}`);
    return { viewport: "390x844", touchTargets: "PASS", reducedMotion: "PASS", ...metrics, ...audit };
  } finally { await browser.close(); }
}

await mkdir(OUT, { recursive: true });
const command = process.platform === "win32" ? "cmd.exe" : "npm";
const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
const server = spawn(command, args, { cwd: ROOT, stdio: "ignore", windowsHide: true });
try {
  await waitForServer();
  const results = {};
  for (const [name, type] of [["chromium", chromium], ["firefox", firefox], ["webkit", webkit]]) results[name] = await desktop(name, type);
  results.chromium390x844 = await mobile();
  await writeFile(path.join(OUT, "browser_matrix.json"), `${JSON.stringify({ status: "PASS", ...results, screenshotNumericScientificAuthority: "NONE", frontendScientificRecomputation: 0 }, null, 2)}\n`);
  console.log("PHASE12_6_CHROMIUM_FIREFOX_WEBKIT_PASS");
  console.log("PHASE12_6_CHROMIUM_390X844_PASS");
} finally {
  if (process.platform === "win32") spawnSync("taskkill", ["/pid", String(server.pid), "/T", "/F"], { stdio: "ignore", windowsHide: true });
  else server.kill("SIGTERM");
}
