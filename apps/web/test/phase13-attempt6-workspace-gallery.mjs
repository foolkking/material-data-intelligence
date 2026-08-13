import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium, firefox, webkit } from "playwright";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const state = JSON.parse(await fs.readFile(path.resolve(process.env.MDI_PHASE13_ATTEMPT6_STATE || path.join(root, ".runtime_services/attempt6-demo5.json")), "utf8"));
const out = path.resolve(process.env.MDI_PHASE13_ATTEMPT6_GALLERY_OUTPUT || path.join(root, ".runtime_services/attempt6-gallery"));
const baseUrl = process.env.MDI_WEB_BASE_URL || "http://127.0.0.1:3014";
await fs.mkdir(out, { recursive: true });
const expected = state.artifacts.length;
const results = {};

async function run(engine, launcher, viewport, representativeOnly = false) {
  const browser = await launcher.launch({ headless: true });
  const page = await browser.newPage({ viewport });
  page.setDefaultTimeout(60_000);
  const pageErrors = [];
  const consoleErrors = [];
  const failedRequests = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); });
  page.on("requestfailed", (request) => {
    const errorText = request.failure()?.errorText || "";
    if (!/ABORTED|cancelled/i.test(errorText)) failedRequests.push(`${request.method()} ${request.url()} ${errorText}`);
  });
  const panel = `?panel=${encodeURIComponent(state.workspace.panelIds[4])}`;
  await page.goto(`${baseUrl}/workspaces/${state.workspaceId}${panel}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await page.getByTestId("workspace-panel-scientific_result").waitFor();
  await page.getByTestId("workspace-artifact-gallery").waitFor();
  await page.getByLabel(`${expected} Artifacts loaded`).waitFor();
  const cards = await page.locator(".workspace-artifact-card").count();
  if (cards !== expected) throw new Error(`${engine}: ${cards} Gallery cards != ${expected}`);
  const bodyWidth = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth }));
  if (bodyWidth.scroll > bodyWidth.client + 1) throw new Error(`${engine}: horizontal overflow ${bodyWidth.scroll}/${bodyWidth.client}`);
  if (!representativeOnly) {
    for (const token of ["phonon band", "phonon dos", "combined", "brillouin"]) {
      const button = page.getByRole("button", { name: new RegExp(`^Open .*${token}`, "i") }).first();
      if (await button.count()) {
        await button.click();
        await page.getByTestId("workspace-scientific-viewer").waitFor();
        await page.getByRole("button", { name: "Close viewer" }).click();
      }
    }
  }
  await page.screenshot({ path: path.join(out, `browser_${engine}.png`), fullPage: true });
  await browser.close();
  if (pageErrors.length || consoleErrors.length || failedRequests.length) {
    throw new Error(`${engine}: browser errors ${JSON.stringify({ pageErrors, consoleErrors, failedRequests })}`);
  }
  results[engine] = { status: "PASS", artifactCards: cards, expectedArtifacts: expected, viewport, horizontalOverflow: 0, pageErrors: 0, consoleErrors: 0, unexpectedFailedRequests: 0 };
}

await run("chromium", chromium, { width: 1440, height: 1000 });
await run("firefox", firefox, { width: 1280, height: 900 }, true);
await run("webkit", webkit, { width: 1280, height: 900 }, true);
await run("mobile_390x844", chromium, { width: 390, height: 844 }, true);
await fs.writeFile(path.join(out, "browser_matrix.json"), `${JSON.stringify(results, null, 2)}\n`);
console.log(JSON.stringify(results));
