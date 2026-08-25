import path from "node:path";
import { pathToFileURL } from "node:url";

const root = process.cwd();
const origin = process.env.MDI_ACCEPTANCE_ORIGIN || "http://127.0.0.1:3002";
const email = process.env.MDI_ACCEPTANCE_EMAIL;
const password = process.env.MDI_ACCEPTANCE_PASSWORD;
const executable = process.env.MDI_BROWSER_EXECUTABLE;
const playwrightModule = process.env.MDI_PLAYWRIGHT_MODULE || path.join(root, "apps/web/node_modules/playwright/index.mjs");
const project = process.env.MDI_PHASE10_PROJECT_ID || "agent2-phase4-project-ca096d85f356";
const tableObject = process.env.MDI_PHASE10_TABLE_OBJECT_ID || "b8a1a55b-d32f-45f3-b421-df075dc3c05d";
const tableVersion = process.env.MDI_PHASE10_TABLE_VERSION_ID || "622ef3d7-301c-420a-aa75-7dda551cf7ef";
const structureObject = process.env.MDI_PHASE10_STRUCTURE_OBJECT_ID || "773089f9-3ce8-4645-92dd-2f62c64cba89";
const structureVersion = process.env.MDI_PHASE10_STRUCTURE_VERSION_ID || "65f56d10-008d-445d-ab2f-228aebf1835b";
const bandObject = process.env.MDI_PHASE10_BAND_OBJECT_ID || "54017eba-e71e-4af0-8d79-763124bbd72d";
const bandVersion = process.env.MDI_PHASE10_BAND_VERSION_ID || "0a389623-928d-4500-8dd3-b1759921a940";

if (!email || !password) throw new Error("MDI_ACCEPTANCE_EMAIL and MDI_ACCEPTANCE_PASSWORD are required");
const pw = await import(pathToFileURL(playwrightModule).href);
const browser = await pw.chromium.launch({ headless: true, executablePath: executable, args: ["--no-sandbox"] });
const results = [];

async function login(page) {
  await page.goto(origin, { waitUntil: "networkidle" });
  const login = page.getByRole("button", { name: "登录", exact: true });
  if (await login.count()) {
    await login.click();
    await page.getByLabel("邮箱", { exact: true }).fill(email);
    await page.getByLabel("密码", { exact: true }).fill(password);
    const responsePromise = page.waitForResponse((response) => ["/auth/login", "/api/auth/login"].includes(new URL(response.url()).pathname));
    await page.getByRole("dialog").getByRole("button", { name: "登录", exact: true }).click();
    const response = await responsePromise;
    if (!response.ok()) throw new Error(`login failed: ${response.status()}`);
    await page.waitForTimeout(400);
  }
}

async function runCase(name, url, viewport, checks) {
  const context = await browser.newContext({ viewport, isMobile: viewport.width < 600, hasTouch: viewport.width < 600, reducedMotion: "reduce" });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];
  page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text().slice(0, 500)); });
  page.on("pageerror", (error) => pageErrors.push(String(error).slice(0, 500)));
  page.on("response", (response) => {
    const parsed = new URL(response.url());
    if (response.status() >= 400 && !parsed.pathname.endsWith("/favicon.ico")) failedRequests.push({ status: response.status(), path: parsed.pathname });
  });
  try {
    await login(page);
    // The app probes /api/auth/me once before the real login. Exclude that
    // expected pre-auth response from the authenticated acceptance window.
    consoleErrors.length = 0;
    pageErrors.length = 0;
    failedRequests.length = 0;
    await page.goto(url, { waitUntil: "networkidle" });
    await page.waitForTimeout(1200);
    const bodyText = await page.locator("body").innerText();
    await checks(page, bodyText);
    const dimensions = await page.evaluate(() => ({
      innerWidth: window.innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      documentClientWidth: document.documentElement.clientWidth,
      bodyWidth: document.body.scrollWidth,
      bodyClientWidth: document.body.clientWidth,
    }));
    const result = { name, url: page.url(), viewport, bodyExcerpt: bodyText.slice(0, 1200), dimensions, consoleErrors, pageErrors, failedRequests, pass: consoleErrors.length === 0 && pageErrors.length === 0 && failedRequests.length === 0 && dimensions.documentWidth <= dimensions.documentClientWidth && dimensions.bodyWidth <= dimensions.bodyClientWidth };
    results.push(result);
    if (!result.pass) throw new Error(`${name} failed: ${JSON.stringify(result)}`);
  } finally {
    await context.close();
  }
}

await runCase("table-mobile", `${origin}/projects/${project}/data?object=${tableObject}&version=${tableVersion}`, { width: 390, height: 844 }, async (page, body) => {
  if (!/3\s*\/\s*3/u.test(body)) throw new Error("table row bound not visible");
  for (const column of ["formula", "band_gap", "density", "sample_id"]) if (!body.includes(column)) throw new Error(`missing table column ${column}`);
  const row = page.getByRole("button", { name: /选择第 1 行/u });
  if (await row.count() !== 1) throw new Error("table row selection is missing");
  await row.click();
});

await runCase("structure-desktop", `${origin}/projects/${project}/data?object=${structureObject}&version=${structureVersion}`, { width: 1280, height: 720 }, async (_page, body) => {
  if (!/Structure|结构|晶体/u.test(body)) throw new Error("structure viewer title not visible");
  if (!/65f56d10|版本\s*1|历史/u.test(body)) throw new Error("structure version context not visible");
  if (!/Fe|O/u.test(body)) throw new Error("structure scientific metadata not visible");
});

await runCase("electronic-band-desktop", `${origin}/projects/${project}/data?object=${bandObject}&version=${bandVersion}`, { width: 1280, height: 720 }, async (_page, body) => {
  if (!/Band|能带|electronic|电子/u.test(body)) throw new Error("electronic band viewer title not visible");
  if (!/eV|Fermi|费米|energy|能量/u.test(body)) throw new Error("electronic scientific axis metadata not visible");
});

console.log(JSON.stringify({ schema: "phase10.canonical_browser_acceptance.v1", sameStack: true, results }, null, 2));
await browser.close();
