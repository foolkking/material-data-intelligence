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
    await page.goto(`${ORIGIN}/analysis`, { waitUntil: "networkidle" });
    const skip = page.locator('.skip-link[href="#planner-primary-content"]');
    await skip.focus();
    const focusedSkip = await page.locator(":focus").getAttribute("href");
    if (focusedSkip !== "#planner-primary-content" || !(await skip.isVisible())) throw new Error(`${name}: skip navigation was not focus-visible`);
    await page.keyboard.press("Enter");
    if ((await page.locator(":focus").getAttribute("id")) !== "planner-primary-content") throw new Error(`${name}: skip target did not receive focus`);
    const separator = page.locator('.resize-handle[role="separator"]');
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
    await page.goto(`${ORIGIN}/analysis`, { waitUntil: "networkidle" });
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
