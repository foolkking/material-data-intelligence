import { spawn, spawnSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const OUT = path.join(ROOT, "docs/phase12/evidence/phase12_2_navigation_planner/browser");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
const PORT = 3456;
const ORIGIN = `http://127.0.0.1:${PORT}`;

async function waitForServer() {
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const response = await fetch(ORIGIN);
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error("Phase 12-2 browser evidence server did not become ready");
}

async function installLocalApiReplay(page, audit) {
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
    audit.httpErrors.push({ path: url.pathname, method: request.method() });
    return route.fulfill({ status: 404, json: { detail: "Phase 12-2 local browser replay route not found" } });
  });
}

async function auditBrowser(name, browserType) {
  const browser = await browserType.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const audit = { navigation: "FAIL", dataDialog: "FAIL", resultsTab: "FAIL", consoleErrors: [], pageErrors: [], externalRequests: [], httpErrors: [] };
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(String(error)));
  page.on("response", (response) => {
    if (response.url().startsWith(ORIGIN) && response.status() >= 400) audit.httpErrors.push({ path: new URL(response.url()).pathname, status: response.status() });
  });
  await installLocalApiReplay(page, audit);
  await page.goto(ORIGIN, { waitUntil: "networkidle" });
  const navigation = page.getByTestId("global-primary-navigation");
  await navigation.waitFor();
  audit.navigation = "PASS";
  const navigationButtons = navigation.locator("button");
  await navigationButtons.nth(0).click();
  await page.locator(".dialog-panel").waitFor();
  audit.dataDialog = "PASS";
  await page.goto(ORIGIN, { waitUntil: "networkidle" });
  await navigation.waitFor();
  await navigation.locator("button").nth(3).click();
  await page.getByTestId("results-export-tab").waitFor();
  audit.resultsTab = "PASS";
  await page.screenshot({ path: path.join(OUT, "screenshots", `${name}_planner.png`), fullPage: true });
  await browser.close();
  if (audit.navigation !== "PASS" || audit.dataDialog !== "PASS" || audit.resultsTab !== "PASS" || audit.consoleErrors.length || audit.pageErrors.length || audit.externalRequests.length || audit.httpErrors.length) {
    throw new Error(`${name} browser audit failed: ${JSON.stringify(audit)}`);
  }
  return audit;
}

await mkdir(path.join(OUT, "screenshots"), { recursive: true });
const server = spawn(process.platform === "win32" ? "cmd.exe" : "npm", process.platform === "win32"
  ? ["/c", "npm", "--prefix", "apps/web", "run", "start", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]
  : ["--prefix", "apps/web", "run", "start", "--", "--hostname", "127.0.0.1", "--port", String(PORT)], { cwd: ROOT, stdio: "ignore" });
try {
  await waitForServer();
  const results = {};
  for (const [name, browserType] of [["chromium", chromium], ["firefox", firefox], ["webkit", webkit]]) results[name] = await auditBrowser(name, browserType);
  const mobile = await chromium.launch({ headless: true });
  const context = await mobile.newContext({ viewport: { width: 390, height: 844 }, isMobile: true });
  const mobilePage = await context.newPage();
  const mobileAudit = { externalRequests: [], httpErrors: [] };
  await installLocalApiReplay(mobilePage, mobileAudit);
  await mobilePage.goto(ORIGIN, { waitUntil: "networkidle" });
  const overflow = await mobilePage.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  const touchTargets = await mobilePage.locator(".global-primary-nav button, .global-primary-nav a").evaluateAll((items) => items.every((item) => item.getBoundingClientRect().height >= 30));
  await mobilePage.screenshot({ path: path.join(OUT, "screenshots", "chromium_mobile_planner.png"), fullPage: true });
  results.mobile = { viewport: "390x844", horizontalOverflow: overflow, navigationTouchFoundation: touchTargets ? "PASS" : "FAIL", ...mobileAudit };
  await mobile.close();
  if (overflow || !touchTargets || mobileAudit.externalRequests.length || mobileAudit.httpErrors.length) throw new Error(`Mobile browser audit failed: ${JSON.stringify(results.mobile)}`);
  await writeFile(path.join(OUT, "browser_matrix.json"), JSON.stringify({ browsers: results, noScientificRecomputation: 0, screenshotNumericAuthority: "NONE" }, null, 2) + "\n");
  console.log("PHASE12_2_CHROMIUM_FIREFOX_WEBKIT_NAVIGATION_PASS");
  console.log("PHASE12_2_CHROMIUM_390X844_NAVIGATION_PASS");
} finally {
  if (process.platform === "win32") spawnSync("taskkill", ["/pid", String(server.pid), "/T", "/F"], { stdio: "ignore", windowsHide: true });
  else server.kill();
}
