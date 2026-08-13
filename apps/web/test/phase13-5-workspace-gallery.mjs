import fs from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const state = JSON.parse(await fs.readFile(path.resolve(required("MDI_PHASE13_5_STATE")), "utf8"));
const out = path.resolve(required("MDI_PHASE13_5_GALLERY_OUTPUT"));
const origin = process.env.MDI_PHASE13_5_WEB_ORIGIN || "http://127.0.0.1:3515";
const playwrightPath = process.env.MDI_PLAYWRIGHT_MODULE
  || path.resolve("E:/mdi-playwright-runner/node_modules/playwright/index.mjs");
const playwright = await import(pathToFileURL(playwrightPath).href);
const localChrome = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const chromiumExecutable = process.env.MDI_CHROMIUM_EXECUTABLE
  || (existsSync(localChrome) ? localChrome : undefined);
await fs.mkdir(out, { recursive: true });

const results = {};
async function check(name, launcher, viewport, mobile = false) {
  const browser = await launcher.launch({
    headless: true,
    executablePath: name === "chromium" || name === "mobile_390x844"
      ? chromiumExecutable
      : undefined,
  });
  const context = await browser.newContext({ viewport, isMobile: mobile, reducedMotion: "reduce" });
  const page = await context.newPage();
  const audit = { pageErrors: [], consoleErrors: [], failedRequests: [], externalRequests: [] };
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("requestfailed", (request) => {
    const expectedAbort = /ABORTED|CANCELLED|CANCELED|NS_BINDING_ABORTED/u.test((request.failure()?.errorText || "").toUpperCase())
      && request.method() === "GET"
      && /\/planner\/jobs\/[^/]+\/artifacts$/u.test(new URL(request.url()).pathname);
    if (!expectedAbort) audit.failedRequests.push(`${request.method()} ${request.url()} ${request.failure()?.errorText || "failed"}`);
  });
  page.on("request", (request) => { if (!/^https?:\/\/(127\.0\.0\.1|localhost)(:\d+)?\//u.test(request.url())) audit.externalRequests.push(request.url()); });
  try {
    await page.goto(`${origin}/workspaces/${state.workspaceId}?panel=${encodeURIComponent(state.workspace.panelIds[4])}`, { waitUntil: "networkidle", timeout: 90_000 });
    if (mobile) await page.getByRole("button", { name: "Context" }).click();
    const resultsNav = mobile
      ? page.locator(".workspace-mobile-panel-switcher").getByRole("button", { name: "Scientific results" })
      : page.getByRole("button", { name: /^Results/u });
    await resultsNav.click();
    await page.getByTestId("workspace-panel-scientific_result").waitFor();
    await page.getByTestId("workspace-artifact-gallery").waitFor();
    const expected = state.artifacts.length;
    await page.getByLabel(`${expected} Artifacts loaded`).waitFor();
    const cards = await page.locator(".workspace-artifact-card").count();
    const dimensions = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
    if (cards !== expected || dimensions.scrollWidth > dimensions.clientWidth + 1) throw new Error(`Gallery mismatch ${cards}/${expected} or overflow`);
    if (!mobile) await page.screenshot({ path: path.join(out, `${name}.png`), fullPage: true });
    results[name] = { status: "PASS", cards, expected, horizontalOverflow: 0, ...audit };
  } finally { await context.close(); await browser.close(); }
  if (Object.values(audit).some((items) => items.length)) {
    throw new Error(`${name} browser audit failed: ${JSON.stringify(audit)}`);
  }
}
await check("chromium", playwright.chromium, { width: 1440, height: 1000 });
await check("firefox", playwright.firefox, { width: 1280, height: 900 });
await check("webkit", playwright.webkit, { width: 1280, height: 900 });
await check("mobile_390x844", playwright.chromium, { width: 390, height: 844 }, true);
await fs.writeFile(path.join(out, "browser_matrix.json"), `${JSON.stringify(results, null, 2)}\n`, "utf8");
console.log(JSON.stringify(results));

function required(name) { const value = process.env[name]; if (!value) throw new Error(`${name} is required`); return value; }
