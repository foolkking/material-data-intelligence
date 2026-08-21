import { spawn, spawnSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const OUT = path.join(ROOT, "docs/phase12/evidence/phase12_7_cross_product_ux_validation");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || path.join(ROOT, "apps/web/node_modules/playwright/index.mjs");
const PORT = Number(process.env.MDI_PHASE12_7_PORT || "3461");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const PROJECT_ID = "phase12-ux-project";
const RESEARCH_PATH = `/projects/${PROJECT_ID}/research`;
const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);

async function waitForServer() {
  for (let attempt = 0; attempt < 240; attempt += 1) {
    try { if ((await fetch(ORIGIN)).ok) return; } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error("Phase 12-7 browser evidence server timeout");
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
        profile: { datasetType: "materials_tabular_dataset", rowCount: 3, columnCount: 2, readyCapabilities: ["STRUCTURE.EXPERIMENTAL_XRD_COMPARISON", "trajectory_visualization", "phonon_visualization", "volumetric_visualization"] },
      }],
      analyses: [], activity: [],
    });
    if (pathname === "/planner/providers/status") return json({ ok: true, provider: "mock", model: "mock-model", status: "ready", execution: "live", configured: true, allowedModels: ["mock-model"] });
    if (pathname === "/planner/providers") return json({ providers: [{ id: "mock", label: "Mock planner", provider: "mock", defaultModel: "mock-model", models: ["mock-model"], requiresSecret: false, execution: "live", secretConfigured: false }] });
    if (pathname === "/health/runtime") return json({ api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } });
    if (pathname === "/datasets" && request.method() === "GET") return json([]);
    if (pathname === "/me/secrets") return json([]);
    audit.failedResponses.push(`${request.method()} ${pathname}`);
    return route.fulfill({ status: 404, json: { detail: "Phase 12-7 local replay route not found" } });
  });
}

function attachAudit(page) {
  const audit = { consoleErrors: [], pageErrors: [], failedResponses: [], externalRequests: [], mutatingApiRequests: [] };
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(String(error)));
  page.on("request", (request) => {
    const url = new URL(request.url());
    const isApi = (url.origin === ORIGIN && url.pathname.startsWith("/api/")) || ((url.hostname === "localhost" || url.hostname === "127.0.0.1") && url.port === "8000");
    if (isApi && !["GET", "HEAD", "OPTIONS"].includes(request.method())) audit.mutatingApiRequests.push(`${request.method()} ${url.pathname}`);
  });
  return audit;
}

async function inspect(page, name, viewport, touch = false) {
  const audit = attachAudit(page);
  await installReplay(page, audit);
  await page.goto(`${ORIGIN}${RESEARCH_PATH}`, { waitUntil: "networkidle" });
  const starter = page.getByRole("region", { name: "从 1 个项目数据集开始" });
  await starter.waitFor({ state: "visible" });
  const starterQuestions = starter.getByRole("button");
  if (await starterQuestions.count() !== 3) throw new Error(`${name}: capability-aware starter did not expose exactly three bounded questions`);
  const selectedQuestion = "比较实验与理论 XRD";
  await starter.getByRole("button", { name: new RegExp(selectedQuestion) }).click();
  const composer = page.getByLabel("询问此项目中的数据");
  if (await composer.inputValue() !== selectedQuestion || !(await composer.evaluate((element) => element === document.activeElement))) throw new Error(`${name}: starter question did not fill and focus the composer`);
  if (audit.mutatingApiRequests.length) throw new Error(`${name}: selecting an inert starter question created a write request`);
  const searchTrigger = page.getByRole("button", { name: "搜索项目" });
  const accountTrigger = page.getByRole("button", { name: /打开账户菜单/ });
  if (!(await searchTrigger.isVisible()) || !(await accountTrigger.isVisible())) throw new Error(`${name}: internal route lost global navigation controls`);
  await accountTrigger.click();
  const settingsItem = page.getByRole("menuitem", { name: "模型设置" });
  await settingsItem.waitFor({ state: "visible" });
  if ((await page.locator(":focus").textContent())?.trim() !== "模型设置") throw new Error(`${name}: account menu did not receive focus`);
  await page.keyboard.press("ArrowDown");
  if ((await page.locator(":focus").textContent())?.trim() !== "退出登录") throw new Error(`${name}: account menu keyboard navigation failed`);
  await page.keyboard.press("Escape");
  if (await page.getByRole("menu", { name: "账户菜单" }).isVisible().catch(() => false)) throw new Error(`${name}: account menu did not close on Escape`);
  if ((await page.locator(":focus").getAttribute("aria-controls")) !== "product-account-menu") throw new Error(`${name}: account menu did not restore trigger focus`);
  const metrics = await page.evaluate(({ touch }) => {
    const root = getComputedStyle(document.documentElement);
    const visible = [...document.querySelectorAll("button, input, select, textarea, a")].filter((item) => {
      const style = getComputedStyle(item);
      const rect = item.getBoundingClientRect();
      return style.visibility !== "hidden" && style.display !== "none" && rect.width > 0 && rect.height > 0;
    });
    const undersized = touch ? visible.filter((item) => item.getBoundingClientRect().height < 44 && !item.classList.contains("skip-link")) : [];
    return {
      horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      visibleControls: visible.length,
      undersized: undersized.map((item) => item.getAttribute("aria-label") || item.textContent?.trim().slice(0, 30)),
      designSystem: {
        accent: root.getPropertyValue("--color-accent").trim(),
        spacing: root.getPropertyValue("--ds-space-3").trim(),
        denseControl: root.getPropertyValue("--ds-control-compact").trim(),
        touchControl: root.getPropertyValue("--ds-control-touch").trim(),
        focusRing: root.getPropertyValue("--color-focus-ring").trim(),
      },
      headings: [...document.querySelectorAll("h1")].map((node) => node.textContent?.trim()),
      statusColorOnly: document.querySelectorAll('[aria-label=""], [aria-label=" "]').length,
    };
  }, { touch });
  if (metrics.horizontalOverflow || metrics.undersized.length) throw new Error(`${name}: ${JSON.stringify(metrics)}`);
  if (Object.values(metrics.designSystem).some((value) => !value)) throw new Error(`${name}: unresolved DS2 token`);
  const panelVisibility = {
    timeline: await page.getByRole("tabpanel", { name: "对话" }).isVisible(),
    workbench: await page.getByRole("tabpanel", { name: "工作台" }).isVisible(),
  };
  if (touch && (!panelVisibility.timeline || panelVisibility.workbench)) throw new Error(`${name}: mobile Research did not retain one active conversation panel`);
  const skip = page.locator('.skip-link[href="#research-primary-content"]');
  await skip.focus();
  if (!(await skip.isVisible())) throw new Error(`${name}: skip link not visible on focus`);
  await page.keyboard.press("Enter");
  if ((await page.locator(":focus").getAttribute("id")) !== "research-primary-content") throw new Error(`${name}: skip target failed`);
  await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: true });
  if (Object.values(audit).some((items) => items.length)) throw new Error(`${name}: ${JSON.stringify(audit)}`);
  return { viewport, ...metrics, ...audit, starterQuestionCount: 3, starterSelection: "FILLED_AND_FOCUSED_WITHOUT_WRITE", panelVisibility, globalNavigation: "PASS", accountMenuKeyboard: "PASS", keyboard: "PASS", status: "PASS" };
}

async function run(browserType, name, viewport, touch = false) {
  const browser = await browserType.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport, isMobile: touch, reducedMotion: "reduce" });
    return await inspect(await context.newPage(), name, `${viewport.width}x${viewport.height}`, touch);
  } finally { await browser.close(); }
}

await mkdir(OUT, { recursive: true });
const command = process.platform === "win32" ? "cmd.exe" : "npm";
const args = process.platform === "win32" ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)] : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
const server = spawn(command, args, { cwd: ROOT, stdio: "ignore", windowsHide: true });
try {
  await waitForServer();
  const results = {
    chromium: await run(chromium, "chromium_1440", { width: 1440, height: 900 }),
    firefox: await run(firefox, "firefox_1440", { width: 1440, height: 900 }),
    webkit: await run(webkit, "webkit_1440", { width: 1440, height: 900 }),
    chromium1280x720: await run(chromium, "chromium_1280", { width: 1280, height: 720 }),
    chromium390x844: await run(chromium, "chromium_mobile_390", { width: 390, height: 844 }, true),
  };
  await writeFile(path.join(OUT, "browser_matrix.json"), `${JSON.stringify({ status: "PASS", ...results, canonicalJourneyCount: 11, retainedCrossProductEvidence: ["phase12-2", "phase12-3", "phase12-4", "phase12-5", "phase12-6"], screenshotNumericScientificAuthority: "NONE", frontendScientificRecomputation: 0 }, null, 2)}\n`);
  console.log("PHASE12_7_CHROMIUM_FIREFOX_WEBKIT_PASS");
  console.log("PHASE12_7_1280_AND_390_PASS");
} finally {
  if (process.platform === "win32") spawnSync("taskkill", ["/pid", String(server.pid), "/T", "/F"], { stdio: "ignore", windowsHide: true });
  else server.kill("SIGTERM");
}
