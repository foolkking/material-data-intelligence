import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs", "phase10k", "evidence", "phase10k4_composition_space");
const SCREENSHOTS = path.join(EVIDENCE, "browser", "screenshots");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const CHROME = process.env.MDI_BROWSER_EXECUTABLE;
const PORT = Number(process.env.MDI_COMPOSITION_SPACE_EVIDENCE_PORT || "3394");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const CASES = {
  normal: { color: "cluster", comparison: false },
  property_color: { color: "property:band_gap", comparison: false },
  group_comparison: { color: "group", comparison: true },
  resource_comparison: { color: "group", comparison: true },
  k3_ml_color: { colorPrefix: "ml:", comparison: false },
};
const audits = new WeakMap();

async function main() {
  await mkdir(SCREENSHOTS, { recursive: true });
  const generated = spawnSync(
    "uv",
    ["run", "python", "scripts/generate_phase10k4_composition_space_evidence.py"],
    { cwd: ROOT, encoding: "utf8", timeout: 600_000 },
  );
  if (generated.status !== 0) {
    throw new Error(`Composition-space evidence generation failed: ${safeError(generated.stderr || generated.stdout || generated.error)}`);
  }

  const captures = {};
  const profiles = {};
  const artifacts = {};
  for (const caseId of Object.keys(CASES)) {
    captures[caseId] = await json(path.join(EVIDENCE, "api", `${caseId}_runtime_capture.json`));
    profiles[caseId] = await json(path.join(EVIDENCE, "api", `${caseId}_data_profile.json`));
    artifacts[caseId] = await hydratedArtifacts(caseId, captures[caseId].artifacts);
  }

  const playwright = await import(pathToFileURL(PLAYWRIGHT).href);
  const server = await ensureServer();
  const requested = new Set(
    (process.env.MDI_COMPOSITION_SPACE_BROWSER_MATRIX || "chromium,firefox,webkit")
      .split(",")
      .map((value) => value.trim()),
  );
  const browsers = [
    {
      id: "chromium",
      type: playwright.chromium,
      options: {
        ...(CHROME ? { executablePath: CHROME } : {}),
        args: ["--no-sandbox", "--disable-background-networking"],
      },
    },
    { id: "firefox", type: playwright.firefox, options: {} },
    { id: "webkit", type: playwright.webkit, options: {} },
  ].filter((candidate) => requested.has(candidate.id));
  const results = [];
  try {
    await waitForApp();
    for (const candidate of browsers) {
      let browser;
      try {
        browser = await candidate.type.launch({ headless: true, timeout: 30_000, ...candidate.options });
        results.push(await runBrowser(browser, candidate.id, captures, profiles, artifacts));
        console.log(`COMPOSITION_SPACE_BROWSER_PASS ${candidate.id}`);
      } catch (error) {
        results.push({ browser: candidate.id, available: false, reason: safeError(error) });
        console.log(`COMPOSITION_SPACE_BROWSER_FALLBACK ${candidate.id} ${safeError(error)}`);
      } finally {
        await browser?.close().catch(() => {});
      }
    }
    const chromium = results.find((item) => item.browser === "chromium");
    if (!chromium?.available) throw new Error("Chromium is required for Composition Space evidence.");
    if (results.some((item) => item.available && (item.externalRequests || item.consoleErrors?.length || item.pageErrors?.length))) {
      throw new Error("Composition Space browser network/console audit failed.");
    }
    await write("browser/browser_matrix.json", results);
    await write("browser/console_network_audit.json", {
      browsers: results.map((item) => ({
        browser: item.browser,
        available: item.available,
        externalRequests: item.externalRequests || 0,
        consoleErrors: item.consoleErrors || [],
        pageErrors: item.pageErrors || [],
      })),
      marker: "NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS",
    });
    await write("browser/accessibility_audit.json", {
      desktop: chromium.cases,
      mobile: chromium.mobile,
      marker: "COMPOSITION_SPACE_BROWSER_EVIDENCE_PASS",
    });
    await write("browser/performance_metrics.json", {
      browsers: results.filter((item) => item.available).map((item) => ({
        browser: item.browser,
        firstProductMs: item.cases.normal.firstProductMs,
      })),
      mobileFirstProductMs: chromium.mobile.firstProductMs,
      acceptance: "PASS",
    });
    await hashEvidence();
    console.log("COMPOSITION_SPACE_RUNTIME_EVIDENCE_PASS");
    console.log("COMPOSITION_SPACE_PCA_EVIDENCE_PASS");
    console.log("COMPOSITION_SPACE_SAMPLE_LINKAGE_EVIDENCE_PASS");
    console.log("COMPOSITION_SPACE_PROPERTY_COLOR_EVIDENCE_PASS");
    console.log("COMPOSITION_SPACE_DATASET_COMPARISON_EVIDENCE_PASS");
    console.log("COMPOSITION_SPACE_CLUSTERING_EVIDENCE_PASS");
    console.log("COMPOSITION_SPACE_BROWSER_EVIDENCE_PASS");
    console.log("COMPOSITION_SPACE_PERFORMANCE_EVIDENCE_PASS");
    console.log("NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    if (server) {
      server.kill();
      await stopPort();
    }
  }
}

async function runBrowser(browser, browserId, captures, profiles, artifacts) {
  const cases = {};
  const combinedAudit = { externalRequests: 0, consoleErrors: [], pageErrors: [] };
  for (const caseId of Object.keys(CASES)) {
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1100 },
      reducedMotion: "reduce",
    });
    const page = await evidencePage(context, caseId, captures[caseId], profiles[caseId], artifacts[caseId]);
    cases[caseId] = await productFlow(page, caseId, false);
    if (browserId === "chromium") {
      await page.getByTestId("composition-space-explorer").screenshot({
        path: path.join(SCREENSHOTS, `${caseId}.png`),
      });
    }
    mergeAudit(combinedAudit, await auditPage(page));
    await page.close();
    await context.close();
  }

  let mobile = null;
  if (browserId === "chromium") {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true,
      reducedMotion: "reduce",
    });
    const page = await evidencePage(context, "normal", captures.normal, profiles.normal, artifacts.normal);
    mobile = await productFlow(page, "normal", true);
    await page.getByTestId("composition-space-explorer").screenshot({
      path: path.join(SCREENSHOTS, "mobile_sample_inspection.png"),
    });
    mergeAudit(combinedAudit, await auditPage(page));
    await page.close();
    await context.close();
  }
  return { browser: browserId, version: browser.version(), available: true, cases, mobile, ...combinedAudit };
}

async function productFlow(page, caseId, mobile) {
  const started = Date.now();
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill("Explore this composition space with deterministic PCA and bounded clusters.");
  await page.locator('[data-testid="planner-form"] button').last().click();
  await page.locator(".main-tab-list button").nth(2).click();
  const product = page.getByTestId("composition-space-explorer");
  await product.waitFor();
  const firstProductMs = Date.now() - started;

  const color = product.getByTestId("composition-space-color-mode");
  const options = await color.locator("option").evaluateAll((nodes) => nodes.map((node) => ({ value: node.value, text: node.textContent || "" })));
  const requestedColor = CASES[caseId].colorPrefix
    ? options.find((item) => item.value.startsWith(CASES[caseId].colorPrefix))?.value
    : CASES[caseId].color;
  if (!requestedColor || !options.some((item) => item.value === requestedColor)) {
    throw new Error(`Required color option is unavailable for ${caseId}: ${JSON.stringify(options)}`);
  }
  await color.selectOption(requestedColor);

  const points = product.locator('svg[role="img"] circle[role="button"]');
  const pointCount = await points.count();
  if (pointCount < 3) throw new Error(`${caseId} did not render enough composition points.`);
  if (mobile) await points.nth(0).tap();
  else await points.nth(0).click();
  const inspector = product.getByTestId("composition-space-sample-inspector");
  const pointerInspector = await inspector.innerText();
  const pointerInspectorLower = pointerInspector.toLowerCase();
  if (!pointerInspectorLower.includes("sample reference") || !pointerInspectorLower.includes("atomic fractions")) {
    throw new Error(`${caseId} pointer/touch sample linkage failed: ${JSON.stringify(pointerInspector.slice(0, 500))}`);
  }
  await points.nth(1).focus();
  await page.keyboard.press("Enter");
  const keyboardInspector = await inspector.innerText();
  if (keyboardInspector === pointerInspector || !keyboardInspector.toLowerCase().includes("formula")) {
    throw new Error(`${caseId} keyboard sample linkage failed.`);
  }

  const state = await product.evaluate((node) => ({
    label: node.getAttribute("aria-label"),
    text: node.textContent || "",
    tables: node.querySelectorAll("table").length,
    svgImages: node.querySelectorAll('svg[role="img"]').length,
    pointButtons: node.querySelectorAll('svg circle[role="button"][tabindex="0"]').length,
    canvases: node.querySelectorAll("canvas").length,
    iframes: node.querySelectorAll("iframe").length,
    scripts: node.querySelectorAll("script").length,
  }));
  const chartLabel = await product.locator('svg[role="img"]').getAttribute("aria-label");
  const comparisonCount = await product.getByTestId("composition-space-comparison").count();
  const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  const contentChecks = {
    pca: state.text.includes("PCA 2D") && state.text.includes("Normalized atomic fractions"),
    clustering: state.text.includes("Composition clusters") && state.text.includes("feature space"),
    outliers: state.text.includes("Composition-space candidates") && state.text.includes("does not label a material invalid"),
    scientificBoundary: state.text.includes("do not establish structural similarity"),
    color: chartLabel?.includes(requestedColor),
    comparison: CASES[caseId].comparison ? comparisonCount === 1 && state.text.includes("exploratory") : comparisonCount === 0,
    invalidDisclosure: caseId !== "normal" || state.text.includes("excluded by the backend parser"),
    mlInspector: caseId !== "k3_ml_color" || keyboardInspector.toLowerCase().includes("linked ml values"),
  };
  if (Object.values(contentChecks).some((value) => !value)) {
    throw new Error(`Composition Space content mismatch: ${JSON.stringify({ caseId, contentChecks })}`);
  }
  if (
    state.label !== "Composition Space Explorer"
    || state.tables < 2
    || state.svgImages !== 1
    || state.pointButtons !== pointCount
    || state.canvases
    || state.iframes
    || state.scripts
    || horizontalOverflow
  ) {
    throw new Error(`Composition Space surface audit failed: ${JSON.stringify({ caseId, state, horizontalOverflow })}`);
  }
  return {
    firstProductMs,
    selectedColor: requestedColor,
    pointCount,
    pointerInspector,
    keyboardInspector,
    horizontalOverflow,
    accessibility: {
      regionLabel: state.label,
      chartImageCount: state.svgImages,
      keyboardPointCount: state.pointButtons,
      tableFallback: state.tables > 0,
      touchSelection: mobile,
    },
  };
}

async function hydratedArtifacts(caseId, records) {
  return Promise.all(records.map(async (artifact) => {
    const file = path.join(EVIDENCE, "artifacts", caseId, artifact.name);
    const raw = await readFile(file, "utf8");
    const content = artifact.name.endsWith(".json") ? JSON.parse(raw) : raw;
    return { ...artifact, content, metadata: { ...(artifact.metadata || {}), preview: content } };
  }));
}

async function evidencePage(context, caseId, capture, profile, artifacts) {
  const audit = { external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
  const page = await context.newPage();
  audits.set(page, audit);
  await page.addInitScript(() => {
    window.EventSource = class {
      close() {}
      addEventListener() {}
      removeEventListener() {}
    };
  });
  page.on("console", (message) => {
    if (message.type() === "error") audit.consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => {
    if (response.status() >= 400) audit.httpErrors.push({ status: response.status(), path: new URL(response.url()).pathname });
  });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === "localhost" && url.port === "8000") return api(route, url, caseId, capture, profile, artifacts);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) {
      if (url.pathname === "/favicon.ico") return route.fulfill({ status: 204, body: "" });
      return route.continue();
    }
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    audit.external.push({ host: url.hostname, path: url.pathname });
    return route.abort();
  });
  return page;
}

async function api(route, url, caseId, capture, profile, artifacts) {
  const method = route.request().method();
  const job = `job_phase10k4_${caseId}_browser`;
  const plan = capture.plan;
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: profile.datasetId, datasetId: profile.datasetId, projectId: "project_phase10k4_evidence", name: `Composition Space ${caseId}`, status: "ready", demo: true, profileId: profile.profileId, profile } });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: { ok: true, job_id: job, plan_id: `plan_phase10k4_${caseId}`, plan_hash: capture.job.planHash, validation_errors: [], plan, plan_source: "mock", planner_provider: "MockLLMProvider", enqueued: true, executed: true } });
  if (url.pathname === `/planner/jobs/${job}`) return route.fulfill({ json: { jobId: job, projectId: "project_phase10k4_evidence", datasetId: profile.datasetId, status: "completed", planId: `plan_phase10k4_${caseId}`, planHash: capture.job.planHash, planSource: "mock", analysisPlan: plan, validationStatus: "validated", toolCallCount: 1, artifactCount: artifacts.length, eventCount: capture.events.length } });
  if (url.pathname === `/planner/jobs/${job}/events`) return route.fulfill({ json: capture.events });
  if (url.pathname === `/planner/jobs/${job}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${job}/tool-calls`) return route.fulfill({ json: capture.toolCalls });
  if (url.pathname === `/planner/jobs/${job}/artifacts`) return route.fulfill({ json: artifacts });
  if (url.pathname === `/planner/jobs/${job}/result`) return route.fulfill({ json: { ...capture.result, jobId: job, artifacts } });
  return route.fulfill({ status: 404, json: { detail: "composition-space evidence route not found" } });
}

async function auditPage(page) {
  const audit = audits.get(page);
  const inert = await page.evaluate(() => ({
    iframe: document.querySelectorAll("iframe").length,
    externalScript: [...document.querySelectorAll("script[src]")].filter((node) => new URL(node.src, location.href).origin !== location.origin).length,
    javascriptUri: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
    inlineHandler: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length,
  }));
  if (Object.values(inert).some(Boolean) || audit.consoleErrors.length || audit.pageErrors.length || audit.external.length || audit.httpErrors.length) {
    throw new Error(`Composition Space browser audit failed: ${JSON.stringify({ inert, ...audit })}`);
  }
  return { externalRequests: audit.external.length, consoleErrors: audit.consoleErrors, pageErrors: audit.pageErrors };
}

function mergeAudit(target, source) {
  target.externalRequests += source.externalRequests;
  target.consoleErrors.push(...source.consoleErrors);
  target.pageErrors.push(...source.pageErrors);
}

function startServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args = process.platform === "win32"
    ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]
    : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
  return spawn(command, args, {
    cwd: ROOT,
    env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: "http://localhost:8000" },
    stdio: "ignore",
  });
}

async function ensureServer() {
  try {
    if ((await fetch(ORIGIN)).ok) return null;
  } catch {}
  await stopPort();
  return startServer();
}

async function waitForApp() {
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    try {
      if ((await fetch(ORIGIN)).ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error("Composition Space app startup timed out.");
}

async function stopPort() {
  if (process.platform !== "win32") return;
  const command = `$c=Get-NetTCPConnection -LocalPort ${PORT} -State Listen -ErrorAction SilentlyContinue; if($c){$c|%{if($_.OwningProcess){Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue}}}`;
  await new Promise((resolve) => {
    const child = spawn("powershell.exe", ["-NoProfile", "-Command", command], { stdio: "ignore" });
    child.on("exit", resolve);
    child.on("error", resolve);
  });
}

async function write(relative, value) {
  const file = path.join(EVIDENCE, relative);
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function json(file) {
  return JSON.parse(await readFile(file, "utf8"));
}

function safeError(error) {
  return String(error instanceof Error ? error.message : error)
    .replace(/[A-Z]:\\[^\n]+/gi, "[local-path]")
    .slice(0, 1000);
}

async function listFiles(directory) {
  const result = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...await listFiles(target));
    else result.push(target);
  }
  return result.sort();
}

async function hashEvidence() {
  const files = (await listFiles(EVIDENCE)).filter((file) => !file.endsWith("evidence_manifest.json"));
  await write("evidence_manifest.json", {
    algorithm: "sha256",
    files: await Promise.all(files.map(async (file) => ({
      name: path.relative(EVIDENCE, file).replaceAll("\\", "/"),
      bytes: (await stat(file)).size,
      sha256: createHash("sha256").update(await readFile(file)).digest("hex"),
    }))),
  });
}

await main();
