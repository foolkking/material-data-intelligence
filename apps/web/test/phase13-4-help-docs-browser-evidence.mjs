import { mkdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const MODE = process.env.MDI_PHASE13_4_EXPECT || "after";
const ORIGIN = process.env.MDI_PHASE13_4_ORIGIN || "http://127.0.0.1:3464";
const API_ORIGIN = process.env.MDI_PHASE13_4_API_ORIGIN || "http://localhost:8000";
const PLAYWRIGHT =
  process.env.MDI_PLAYWRIGHT_MODULE ||
  path.join(ROOT, "apps/web/node_modules/playwright/index.mjs");
const LOCAL_CHROMIUM = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const CHROMIUM_EXECUTABLE =
  process.env.MDI_CHROMIUM_EXECUTABLE ||
  (existsSync(LOCAL_CHROMIUM) ? LOCAL_CHROMIUM : undefined);
const DOCS_URL =
  "https://github.com/foolkking/material-data-intelligence/blob/master/docs/phase13/release/README.md";
const OUT = process.env.MDI_PHASE13_4_OUTPUT_DIR
  ? path.resolve(process.env.MDI_PHASE13_4_OUTPUT_DIR)
  : path.join(
      ROOT,
      "docs/phase13/evidence/phase13_4_targeted_final_product_polish",
    );
const playwright = await import(pathToFileURL(PLAYWRIGHT).href);
const requestedBrowsers = (process.env.MDI_PHASE13_4_BROWSERS || "chromium")
  .split(",")
  .map((value) => value.trim())
  .filter(Boolean);

async function installReplay(page, audit) {
  await page.route("**/*", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.origin === ORIGIN) return route.continue();
    if (url.origin !== API_ORIGIN) {
      audit.unapprovedExternalRequests.push(request.url());
      return route.abort();
    }
    if (url.pathname === "/health/runtime") {
      return route.fulfill({
        json: {
          api: { status: "ok" },
          database: { status: "mock" },
          redis: { status: "mock" },
          artifactStorage: { status: "mock" },
          worker: { status: "mock" },
          llmProvider: { status: "mock" },
        },
      });
    }
    if (url.pathname === "/datasets" && request.method() === "GET") {
      return route.fulfill({ json: [] });
    }
    if (url.pathname === "/planner/providers") {
      return route.fulfill({
        json: {
          providers: [
            {
              id: "mock",
              label: "Mock planner",
              provider: "mock",
              defaultModel: "mock",
              requiresSecret: false,
            },
          ],
        },
      });
    }
    if (url.pathname.startsWith("/planner/providers/")) {
      return route.fulfill({
        json: {
          ok: true,
          provider: "mock",
          mode: "mock",
          secretConfigured: false,
        },
      });
    }
    if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
    audit.unexpectedFailedRequests.push(
      `${request.method()} ${url.pathname}`,
    );
    return route.fulfill({ status: 404, json: { detail: "Replay route missing" } });
  });
}

async function capture(browserName, viewport, mobile = false) {
  const browserType = playwright[browserName];
  if (!browserType) throw new Error(`Unsupported browser: ${browserName}`);
  const browser = await browserType.launch(
    browserName === "chromium" && CHROMIUM_EXECUTABLE
      ? { executablePath: CHROMIUM_EXECUTABLE, headless: true }
      : { headless: true },
  );
  try {
    const context = await browser.newContext({
      viewport,
      isMobile: mobile,
      reducedMotion: "reduce",
    });
    const page = await context.newPage();
    const audit = {
      consoleErrors: [],
      pageErrors: [],
      unexpectedFailedRequests: [],
      unapprovedExternalRequests: [],
    };
    page.on("console", (message) => {
      if (message.type() === "error") audit.consoleErrors.push(message.text());
    });
    page.on("pageerror", (error) => audit.pageErrors.push(String(error)));
    await installReplay(page, audit);
    await page.goto(`${ORIGIN}/analysis`, { waitUntil: "networkidle" });

    const help = page.locator(
      MODE === "before"
        ? ".top-settings > button.icon-button:last-of-type"
        : `.top-settings > a.icon-button[href="${DOCS_URL}"]`,
    );
    await help.waitFor();
    const beforeUrl = page.url();
    const tagName = await help.evaluate((element) => element.tagName);
    const href = await help.getAttribute("href");
    const target = await help.getAttribute("target");
    const rel = await help.getAttribute("rel");
    const box = await help.boundingBox();
    await help.focus();
    const focusVisible = await help.evaluate((element) =>
      element.matches(":focus-visible"),
    );

    let keyboardActivation = "NO_ACTION";
    if (MODE === "after") {
      await help.evaluate((element) => {
        element.addEventListener(
          "click",
          (event) => {
            event.preventDefault();
            window.__phase13HelpActivated = true;
          },
          { once: true },
        );
      });
      await page.keyboard.press("Enter");
      keyboardActivation = (await page.evaluate(
        () => window.__phase13HelpActivated === true,
      ))
        ? "PASS"
        : "FAIL";
    } else {
      await page.keyboard.press("Enter");
      keyboardActivation = page.url() === beforeUrl ? "NO_ACTION" : "UNEXPECTED";
    }

    const horizontalOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    );
    const screenshot = path.join(
      OUT,
      "screenshots",
      MODE,
      mobile ? "chromium_390x844.png" : `${browserName}_1440x900.png`,
    );
    await mkdir(path.dirname(screenshot), { recursive: true });
    await page.screenshot({ path: screenshot, fullPage: true });

    const result = {
      mode: MODE,
      browser: browserName,
      viewport: `${viewport.width}x${viewport.height}`,
      tagName,
      href,
      target,
      rel,
      focusVisible,
      keyboardActivation,
      touchTarget:
        box && box.width >= (mobile ? 44 : 36) && box.height >= (mobile ? 44 : 36)
          ? "PASS"
          : "FAIL",
      horizontalOverflow,
      screenshot: path.relative(ROOT, screenshot).replaceAll("\\", "/"),
      ...audit,
    };

    if (
      audit.consoleErrors.length ||
      audit.pageErrors.length ||
      audit.unexpectedFailedRequests.length ||
      audit.unapprovedExternalRequests.length ||
      horizontalOverflow ||
      !focusVisible ||
      result.touchTarget !== "PASS"
    ) {
      throw new Error(JSON.stringify(result));
    }
    if (
      MODE === "before" &&
      (tagName !== "BUTTON" || href !== null || keyboardActivation !== "NO_ACTION")
    ) {
      throw new Error(`Unexpected before state: ${JSON.stringify(result)}`);
    }
    if (
      MODE === "after" &&
      (tagName !== "A" ||
        href !== DOCS_URL ||
        target !== "_blank" ||
        rel !== "noreferrer" ||
        keyboardActivation !== "PASS")
    ) {
      throw new Error(`Unexpected after state: ${JSON.stringify(result)}`);
    }
    return result;
  } finally {
    await browser.close();
  }
}

const evidence = {
  polishId: "P13-POLISH-002",
  documentationUrl: DOCS_URL,
  screenshotScientificAuthority: "NONE",
  browsers: {},
};
for (const browserName of requestedBrowsers) {
  evidence.browsers[browserName] = {
    desktop: await capture(browserName, { width: 1440, height: 900 }),
  };
}
evidence.desktop = evidence.browsers.chromium?.desktop;
if (requestedBrowsers.includes("chromium")) {
  evidence.mobile = await capture(
    "chromium",
    { width: 390, height: 844 },
    true,
  );
}
await writeFile(
  path.join(OUT, `polish_p13_polish_002_${MODE}.json`),
  `${JSON.stringify(evidence, null, 2)}\n`,
);
console.log(`PHASE13_4_HELP_DOCS_${MODE.toUpperCase()}_PASS`);
