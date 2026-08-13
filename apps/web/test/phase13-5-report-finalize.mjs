import { mkdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { pathToFileURL } from "node:url";

const playwrightModule = process.env.MDI_PLAYWRIGHT_MODULE
  || path.resolve("E:/mdi-playwright-runner/node_modules/playwright/index.mjs");
const { chromium } = await import(pathToFileURL(playwrightModule).href);
const localChrome = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const chromiumExecutable = process.env.MDI_CHROMIUM_EXECUTABLE
  || (existsSync(localChrome) ? localChrome : undefined);

const origin = process.env.MDI_PHASE13_5_WEB_ORIGIN || "http://127.0.0.1:3515";
const workspaceId = required("MDI_PHASE13_5_WORKSPACE_ID");
const output = path.resolve(required("MDI_PHASE13_5_BROWSER_OUTPUT"));
const demo = required("MDI_PHASE13_5_DEMO");

await mkdir(path.dirname(output), { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: chromiumExecutable });
const context = await browser.newContext({
  viewport: { width: 1440, height: 1050 },
  reducedMotion: "reduce",
});
const page = await context.newPage();
const audit = {
  consoleErrors: [], pageErrors: [], failedResponses: [], failedRequests: [],
  expectedClientAborts: [], externalRequests: [],
};
page.on("console", (message) => {
  if (message.type() === "error") audit.consoleErrors.push(message.text());
});
page.on("pageerror", (error) => audit.pageErrors.push(error.message));
page.on("response", (response) => {
  if (response.status() >= 400) audit.failedResponses.push(`${response.status()} ${response.url()}`);
});
page.on("requestfailed", (request) => {
  const failure = `${request.failure()?.errorText || "failed"} ${request.url()}`;
  const expectedAbort = request.failure()?.errorText === "net::ERR_ABORTED"
    && request.method() === "GET"
    && /\/report-composition(?:\/sources|s)?$/u.test(new URL(request.url()).pathname);
  (expectedAbort ? audit.expectedClientAborts : audit.failedRequests).push(failure);
});
page.on("request", (request) => {
  const host = new URL(request.url()).hostname;
  if (!["127.0.0.1", "localhost"].includes(host)) audit.externalRequests.push(request.url());
});

try {
  await page.goto(`${origin}/workspaces/${workspaceId}`, {
    waitUntil: "networkidle", timeout: 90_000,
  });
  await page.getByRole("button", { name: "Report" }).click();
  await page.getByTestId("workspace-report-composer").waitFor({ timeout: 30_000 });
  await page.getByText(/exact sources; \d+ mandatory disclosures/u).waitFor({ timeout: 30_000 });
  const addButtons = page.locator('button[aria-label^="Add "][aria-label$=" to report"]:not([disabled])');
  const sourceCount = await addButtons.count();
  if (sourceCount < 1) throw new Error(`expected persisted report source, got ${sourceCount}`);
  for (let index = sourceCount - 1; index >= 0; index -= 1) await addButtons.nth(index).click();
  const preview = page.getByRole("button", { name: "Preview report" });
  if (await preview.isDisabled()) throw new Error(`Preview disabled: ${await preview.getAttribute("title")}`);
  await preview.click();
  await page.getByRole("heading", { name: "Deterministic preview" }).waitFor({ timeout: 30_000 });
  const finalize = page.getByRole("button", { name: "Finalize report" });
  if (await finalize.isDisabled()) throw new Error(`Finalize disabled: ${await finalize.getAttribute("title")}`);
  await finalize.click();
  await page.getByRole("button", { name: "Confirm and finalize" }).click();
  await page.getByRole("heading", { name: "Report detail" }).waitFor({ timeout: 30_000 });
  await page.getByRole("heading", { name: "How this result was produced" }).waitFor({ timeout: 30_000 });
  await page.getByText("Exact non-executable Recipe declaration").waitFor({ timeout: 30_000 });
  const screenshot = path.join(path.dirname(output), `demo_${demo}_report_ui.png`);
  await page.screenshot({ path: screenshot, fullPage: true });
  const failures = [
    audit.consoleErrors, audit.pageErrors, audit.failedResponses,
    audit.failedRequests, audit.externalRequests,
  ];
  if (failures.some((items) => items.length)) {
    throw new Error(`browser audit failed: ${JSON.stringify(audit)}`);
  }
  await writeFile(output, `${JSON.stringify({
    status: "PASS", demo: Number(demo), workspaceId, selectedSources: sourceCount,
    finalizeEnabled: true, reportDetailLoaded: true, recipeLoaded: true,
    screenshot, ...audit,
  }, null, 2)}\n`, "utf8");
  console.log(`PHASE13_5_DEMO_${demo}_REAL_CHROMIUM_FINALIZE_PASS`);
} finally {
  await context.close();
  await browser.close();
}

function required(name) {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is required`);
  return value;
}
