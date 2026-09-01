import path from "node:path";
import { chromium } from "playwright";

const baseUrl = process.env.MDI_WEB_BASE_URL || "http://127.0.0.1:3000";
const projectId = "project_0002_1a0af866391f412d";
const datasetName =
  process.env.MDI_ACCEPTANCE_DATASET_NAME ||
  "Phase14R Composition ML Qualification";
const filePath = path.resolve(
  process.cwd(),
  process.env.MDI_ACCEPTANCE_SOURCE_FILE ||
    "../../tests/fixtures/tables/ml_results.csv",
);
const executablePath =
  process.env.MDI_CHROMIUM_EXECUTABLE ||
  "C:/Users/86182/Desktop/wkkk/playwright-browsers/chromium-1228/chrome-win64/chrome.exe";

const browser = await chromium.launch({ headless: true, executablePath });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const consoleErrors = [];
const criticalResponses = [];
page.on("pageerror", (error) => consoleErrors.push(String(error)));
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("response", (response) => {
  if (response.status() >= 500) {
    criticalResponses.push(`${response.status()} ${response.url()}`);
  }
});

try {
  await page.goto(`${baseUrl}/?login=1`, { waitUntil: "networkidle" });
  const email = page.getByLabel(/邮箱|email/i);
  if (await email.count()) {
    await email.fill("acceptance.researcher@local.invalid");
    await page.getByLabel(/密码|password/i).fill("LocalAcceptance-2026!");
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "登录", exact: true })
      .click();
    await page.waitForTimeout(600);
  }

  const dataUrl = `${baseUrl}/projects/${projectId}/data`;
  await page.goto(dataUrl, { waitUntil: "networkidle" });
  const existing = page.getByRole("link", { name: new RegExp(datasetName) }).first();
  if (!(await existing.count())) {
    await page.goto(`${baseUrl}/projects/${projectId}/datasets/new`, {
      waitUntil: "networkidle",
    });
    await page.getByLabel("数据集名称").fill(datasetName);
    await page.getByLabel("源文件").setInputFiles(filePath);
    await page.getByRole("button", { name: "上传并解析" }).click();
    await page.getByRole("status").filter({ hasText: "数据已上传并进入解析流程" }).waitFor({
      state: "visible",
      timeout: 90_000,
    });
  }

  await page.goto(dataUrl, { waitUntil: "networkidle" });
  const datasetLink = page
    .getByRole("link", { name: new RegExp(datasetName) })
    .first();
  await datasetLink.waitFor({ state: "visible", timeout: 30_000 });
  const href = await datasetLink.getAttribute("href");
  console.log(JSON.stringify({
    datasetName,
    href,
    sourceFile: path.basename(filePath),
    consoleErrors,
    criticalResponses,
  }, null, 2));
} finally {
  await browser.close();
}
