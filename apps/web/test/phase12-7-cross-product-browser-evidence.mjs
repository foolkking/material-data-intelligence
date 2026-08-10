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
    if (url.origin === ORIGIN) return route.continue();
    if (url.hostname !== "localhost" || url.port !== "8000") {
      audit.externalRequests.push(request.url());
      return route.abort();
    }
    if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
    if (url.pathname === "/datasets" && request.method() === "GET") return route.fulfill({ json: [] });
    if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
    if (url.pathname.startsWith("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
    if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
    audit.failedResponses.push(`${request.method()} ${url.pathname}`);
    return route.fulfill({ status: 404, json: { detail: "Phase 12-7 local replay route not found" } });
  });
}

function attachAudit(page) {
  const audit = { consoleErrors: [], pageErrors: [], failedResponses: [], externalRequests: [] };
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(String(error)));
  return audit;
}

async function inspect(page, name, viewport, touch = false) {
  const audit = attachAudit(page);
  await installReplay(page, audit);
  await page.goto(ORIGIN, { waitUntil: "networkidle" });
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
  const skip = page.locator('.skip-link[href="#planner-primary-content"]');
  await skip.focus();
  if (!(await skip.isVisible())) throw new Error(`${name}: skip link not visible on focus`);
  await page.keyboard.press("Enter");
  if ((await page.locator(":focus").getAttribute("id")) !== "planner-primary-content") throw new Error(`${name}: skip target failed`);
  await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: true });
  if (Object.values(audit).some((items) => items.length)) throw new Error(`${name}: ${JSON.stringify(audit)}`);
  return { viewport, ...metrics, ...audit, keyboard: "PASS", status: "PASS" };
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
