import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const ORIGIN = process.env.MDI_ACCEPTANCE_ORIGIN || "http://127.0.0.1:3002";
const EMAIL = process.env.MDI_ACCEPTANCE_EMAIL;
const PASSWORD = process.env.MDI_ACCEPTANCE_PASSWORD;
const PROJECT_ID = process.env.MDI_PHASE9_PROJECT_ID || "agent2-phase4-project-ca096d85f356";
const OBJECT_ID = process.env.MDI_PHASE9_TABLE_OBJECT_ID || "c1b1fcfe-4ade-4864-8580-9305d71b9a0e";
const VERSION_ID = process.env.MDI_PHASE9_TABLE_VERSION_ID || "a8ff3049-c483-4f4b-83d1-90146c9db978";
const EXECUTABLE = process.env.MDI_BROWSER_EXECUTABLE;

if (!EMAIL || !PASSWORD) throw new Error("MDI_ACCEPTANCE_EMAIL and MDI_ACCEPTANCE_PASSWORD are required");

const pw = await import(pathToFileURL(PLAYWRIGHT).href);
const browser = await pw.chromium.launch({ headless: true, ...(EXECUTABLE ? { executablePath: EXECUTABLE } : {}), args: ["--no-sandbox"] });
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  hasTouch: true,
  reducedMotion: "reduce",
});
const page = await context.newPage();
const consoleErrors = [];
const pageErrors = [];
const failedCriticalRequests = [];
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text().slice(0, 500));
});
page.on("pageerror", (error) => pageErrors.push(String(error).slice(0, 500)));
page.on("response", (response) => {
  const url = new URL(response.url());
  if (response.status() >= 400 && !url.pathname.endsWith("/favicon.ico")) {
    failedCriticalRequests.push({ status: response.status(), path: url.pathname });
  }
});

try {
  await page.goto(ORIGIN, { waitUntil: "networkidle" });
  const login = page.getByRole("button", { name: "登录", exact: true });
  if (await login.count()) {
    await login.click();
    await page.getByLabel("邮箱", { exact: true }).fill(EMAIL);
    await page.getByLabel("密码", { exact: true }).fill(PASSWORD);
    const loginResponse = page.waitForResponse((response) => new URL(response.url()).pathname === "/api/auth/login", { timeout: 15_000 });
    await page.getByRole("dialog").getByRole("button", { name: "登录", exact: true }).click();
    const response = await loginResponse;
    if (!response.ok()) throw new Error(`authenticated login failed (${response.status()})`);
    await page.waitForTimeout(500);
  }

  // The initial unauthenticated /auth/me probe is expected before login and is
  // not evidence of a protected-route failure after authentication.
  consoleErrors.length = 0;
  pageErrors.length = 0;
  failedCriticalRequests.length = 0;

  const tableUrl = `${ORIGIN}/projects/${PROJECT_ID}/data?object=${OBJECT_ID}&version=${VERSION_ID}`;
  await page.goto(tableUrl, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Phase 9 canonical materials table" }).waitFor();
  const bodyText = await page.locator("body").innerText();
  if (!bodyText.includes("3 / 3 行")) throw new Error("bounded 3/3 table rows were not rendered");
  for (const column of ["formula", "y_pred", "y_true"]) {
    if (!bodyText.includes(column)) throw new Error(`missing scientific column: ${column}`);
  }
  const rowButton = page.getByRole("button", { name: "选择第 1 行", exact: true });
  if (await rowButton.count() !== 1) throw new Error("canonical row selector missing");
  await rowButton.click();
  await page.getByText("Si", { exact: true }).first().waitFor();
  const overflow = await page.evaluate(() => ({
    viewport: { width: window.innerWidth, height: window.innerHeight },
    documentWidth: document.documentElement.scrollWidth,
    documentClientWidth: document.documentElement.clientWidth,
    bodyWidth: document.body.scrollWidth,
    bodyClientWidth: document.body.clientWidth,
  }));
  const result = {
    viewport: overflow.viewport,
    table: "PASS",
    rows: "3 / 3",
    columns: ["formula", "y_pred", "y_true"],
    boundedPayload: "PASS",
    rowSelection: "PASS",
    documentOverflow: overflow.documentWidth > overflow.documentClientWidth,
    bodyOverflow: overflow.bodyWidth > overflow.bodyClientWidth,
    consoleErrors,
    unhandledRejections: pageErrors,
    criticalApiFailures: failedCriticalRequests,
    url: page.url(),
  };
  if (result.documentOverflow || result.bodyOverflow) throw new Error(`global overflow: ${JSON.stringify(result)}`);
  if (consoleErrors.length || pageErrors.length || failedCriticalRequests.length) throw new Error(`browser runtime failure: ${JSON.stringify(result)}`);
  console.log(JSON.stringify(result));
} finally {
  await context.close();
  await browser.close();
}
