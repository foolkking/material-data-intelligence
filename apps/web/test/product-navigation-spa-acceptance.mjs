import { chromium } from "playwright";

const baseUrl = (process.env.MDI_WEB_BASE_URL || "http://127.0.0.1:3023").replace(
  /\/$/u,
  "",
);
const projectId =
  process.env.MDI_NAVIGATION_PROJECT_ID || "project_0002_1a0af866391f412d";
const email = process.env.MDI_ACCEPTANCE_EMAIL;
const password = process.env.MDI_ACCEPTANCE_PASSWORD;
const executablePath =
  process.env.MDI_CHROMIUM_EXECUTABLE ||
  "C:/Users/86182/Desktop/wkkk/playwright-browsers/chromium-1228/chrome-win64/chrome.exe";

if (!email || !password) {
  throw new Error(
    "MDI_ACCEPTANCE_EMAIL and MDI_ACCEPTANCE_PASSWORD are required.",
  );
}

const browser = await chromium.launch({ headless: true, executablePath });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const consoleErrors = [];
const serverErrors = [];
const transitions = [];

page.on("pageerror", (error) => consoleErrors.push(String(error)));
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("response", (response) => {
  if (response.status() >= 500) {
    serverErrors.push(`${response.status()} ${response.url()}`);
  }
});

async function login() {
  await page.goto(`${baseUrl}/?login=1`, { waitUntil: "networkidle" });
  const emailInput = page.getByLabel(/邮箱|email/i);
  if (!(await emailInput.count())) return;
  await emailInput.fill(email);
  await page.getByLabel(/密码|password/i).fill(password);
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "登录", exact: true })
    .click();
  await page.waitForTimeout(500);
}

async function assertSpaTransition(label, link) {
  const href = await link.getAttribute("href");
  if (!href) throw new Error(`${label}: target link has no href.`);

  const target = new URL(href, baseUrl);
  const marker = `${label}-${Date.now()}`;
  await page.evaluate((value) => {
    window.__mdiProductNavigationProbe = value;
  }, marker);
  const before = await page.evaluate(() => ({
    href: window.location.href,
    timeOrigin: window.performance.timeOrigin,
  }));
  const documentRequests = [];
  const onRequest = (request) => {
    if (request.resourceType() === "document") {
      documentRequests.push(request.url());
    }
  };
  page.on("request", onRequest);

  const startedAt = performance.now();
  await link.click();
  await page.waitForURL((url) => {
    return url.pathname === target.pathname && url.search === target.search;
  });
  await page.locator("main").waitFor({ state: "visible" });
  const elapsedMs = Math.round(performance.now() - startedAt);
  const after = await page.evaluate(() => ({
    href: window.location.href,
    timeOrigin: window.performance.timeOrigin,
    marker: window.__mdiProductNavigationProbe || null,
  }));
  page.off("request", onRequest);

  const result = {
    label,
    from: before.href,
    to: after.href,
    elapsedMs,
    documentRequests,
    timeOriginPreserved: before.timeOrigin === after.timeOrigin,
    runtimeStatePreserved: after.marker === marker,
  };
  transitions.push(result);
  if (
    documentRequests.length ||
    !result.timeOriginPreserved ||
    !result.runtimeStatePreserved
  ) {
    throw new Error(`${label}: document reload detected: ${JSON.stringify(result)}`);
  }
}

try {
  await login();
  // The unauthenticated bootstrap intentionally probes the current session
  // before the login dialog is submitted. Qualify browser health only after
  // the authenticated product boundary has been established.
  consoleErrors.length = 0;
  serverErrors.length = 0;
  const projectRoot = `${baseUrl}/projects/${projectId}`;
  await page.goto(`${projectRoot}/reports`, { waitUntil: "networkidle" });

  await assertSpaTransition(
    "reports-to-data",
    page.getByRole("link", { name: "数据", exact: true }),
  );
  await assertSpaTransition(
    "data-to-research",
    page.getByRole("link", { name: "研究", exact: true }),
  );
  await assertSpaTransition(
    "research-to-reports",
    page.getByRole("link", { name: "报告", exact: true }),
  );

  const reportLink = page.locator('a[href*="/reports/agent2_report_"]').first();
  await reportLink.waitFor({ state: "visible", timeout: 15_000 });
  await assertSpaTransition("reports-to-report-detail", reportLink);

  const sourceResearchLink = page.getByRole("link", {
    name: "打开来源研究",
    exact: true,
  });
  await sourceResearchLink.waitFor({ state: "visible", timeout: 15_000 });
  await assertSpaTransition("report-to-source-research", sourceResearchLink);

  const viewerLink = page.getByRole("link", { name: "打开查看器" }).first();
  await viewerLink.waitFor({ state: "visible", timeout: 15_000 });
  await assertSpaTransition("research-to-viewer", viewerLink);

  if (consoleErrors.length || serverErrors.length) {
    throw new Error(
      `Browser health failed: ${JSON.stringify({ consoleErrors, serverErrors })}`,
    );
  }

  console.log(
    JSON.stringify(
      {
        marker: "PRODUCT_NAVIGATION_SPA_ACCEPTANCE_PASS",
        projectId,
        transitions,
        consoleErrors,
        serverErrors,
      },
      null,
      2,
    ),
  );
} finally {
  await browser.close();
}
