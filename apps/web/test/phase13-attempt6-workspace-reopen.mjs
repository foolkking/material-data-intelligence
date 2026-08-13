import { chromium } from "playwright";
import fs from "node:fs";

const workspaceId = process.env.WORKSPACE_ID;
const screenshotPath = process.env.SCREENSHOT_PATH;
const outputPath = process.env.OUTPUT_PATH;
const baseUrl = process.env.WEB_BASE_URL || "http://127.0.0.1:3014";

if (!workspaceId || !screenshotPath || !outputPath) {
  throw new Error("WORKSPACE_ID, SCREENSHOT_PATH, and OUTPUT_PATH are required");
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
const pageErrors = [];
const consoleErrors = [];
const failedResponses = [];
page.on("pageerror", (error) => pageErrors.push(String(error)));
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("response", (response) => {
  if (response.status() >= 400) failedResponses.push(`${response.status()} ${response.url()}`);
});

await page.goto(`${baseUrl}/workspaces/${workspaceId}`, { waitUntil: "networkidle" });
await page.getByRole("button", { name: "Report" }).click();
await page.getByTestId("workspace-report-composer").waitFor();
await page.getByRole("tab", { name: "History" }).click();
await page.getByRole("heading", { name: "Immutable history" }).waitFor();
const historyCount = await page.getByRole("button", { name: "Open" }).count();
if (historyCount < 1) throw new Error("expected at least one immutable Report history entry");
await page.screenshot({ path: screenshotPath, fullPage: true });

const result = {
  status: pageErrors.length || consoleErrors.length || failedResponses.length ? "FAIL" : "PASS",
  workspaceId,
  historyCount,
  screenshot: screenshotPath,
  pageErrors,
  consoleErrors,
  failedResponses,
};
fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, "utf8");
await browser.close();
if (result.status !== "PASS") process.exitCode = 1;
