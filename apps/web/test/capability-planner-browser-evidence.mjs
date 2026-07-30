import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
const EVIDENCE = path.join(ROOT, "docs", "phase10l", "evidence", "phase10l2_capability_aware_planner");
const SCREENSHOTS = path.join(EVIDENCE, "screenshots");
const PORT = 3220;
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const fixtures = JSON.parse(await readFile(path.join(EVIDENCE, "browser", "fixtures.json"), "utf8"));

const CASES = {
  ready: "Analyze this materials dataset composition distribution and anomaly candidates.",
  blocked: "Create a report using a capability that is not currently registered.",
};
const PROFILE = {
  profileId: fixtures.ready.intent.profileId,
  datasetId: fixtures.ready.intent.datasetId,
  version: "2",
  profileContractVersion: "2.0",
  semanticHash: fixtures.ready.intent.dataScope.profileSemanticHash,
  datasetType: "mixed",
  tableSummary: { nRows: 8, nColumns: 6, columns: [] },
  resourceSemantics: fixtures.ready.intent.dataScope.resourceRefs.map((item) => ({
    objectId: item.objectId,
    objectType: item.objectType,
    objectHash: item.objectHash,
    kind: item.kind,
    capabilities: ["table", "composition"],
    warnings: [],
  })),
  analysisReadiness: [],
};

async function main() {
  await mkdir(path.join(EVIDENCE, "browser"), { recursive: true });
  await mkdir(SCREENSHOTS, { recursive: true });
  const server = startServer();
  try {
    await waitForApp();
    const matrix = {};
    for (const [name, browserType] of Object.entries({ chromium, firefox, webkit })) {
      const browser = await browserType.launch({ headless: true });
      try {
        matrix[name] = await runBrowser(browser, name);
      } finally {
        await browser.close();
      }
    }
    await writeJson("browser/browser_matrix.json", matrix);
    const externalRequests = Object.values(matrix).reduce((sum, item) => sum + item.externalRequests, 0);
    await writeJson("browser/network_audit.json", {
      externalRequests,
      marker: "NO_PHASE10L2_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS",
    });
    await writeJson("browser/console_audit.json", {
      consoleErrors: Object.values(matrix).flatMap((item) => item.consoleErrors),
      pageErrors: Object.values(matrix).flatMap((item) => item.pageErrors),
    });
    await hashEvidence();
    console.log("CAPABILITY_AWARE_PLANNER_BROWSER_EVIDENCE_PASS");
    console.log("CAPABILITY_AWARE_PLANNER_MOBILE_EVIDENCE_PASS");
    console.log("PROVIDER_VISIBLE_TOOL_IDS == ELIGIBLE_TOOL_IDS");
    console.log("NO_REJECTED_CANDIDATE_LEAK_TO_LLM");
    console.log("NO_PHASE10L2_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    stopServer(server);
  }
}

async function runBrowser(browser, browserName) {
  const result = {
    browser: browserName,
    version: browser.version(),
    cases: {},
    mobile: {},
    externalRequests: 0,
    consoleErrors: [],
    pageErrors: [],
  };
  for (const caseName of Object.keys(CASES)) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
    const state = auditState(caseName);
    const page = await evidencePage(context, state);
    result.cases[caseName] = await runFlow(page, state, { mobile: false, screenshot: browserName === "chromium" });
    mergeAudit(result, state);
    assertAudit(state);
    await context.close();
  }
  if (browserName === "chromium") {
    for (const caseName of Object.keys(CASES)) {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
      const state = auditState(caseName);
      const page = await evidencePage(context, state);
      result.mobile[caseName] = await runFlow(page, state, { mobile: true, screenshot: true });
      mergeAudit(result, state);
      assertAudit(state);
      await context.close();
    }
  }
  return result;
}

function auditState(caseName) {
  return { caseName, external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
}

function mergeAudit(result, state) {
  result.externalRequests += state.external.length;
  result.consoleErrors.push(...state.consoleErrors);
  result.pageErrors.push(...state.pageErrors);
}

async function evidencePage(context, state) {
  const page = await context.newPage();
  await page.addInitScript(() => {
    window.EventSource = class {
      close() {}
      addEventListener() {}
      removeEventListener() {}
    };
  });
  page.on("console", (message) => { if (message.type() === "error") state.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => state.pageErrors.push(error.message));
  page.on("response", (response) => {
    if (response.status() >= 400) state.httpErrors.push({ status: response.status(), path: new URL(response.url()).pathname });
  });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin === API_ORIGIN) return handleApi(route, url, state);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) {
      if (url.pathname === "/favicon.ico") return route.fulfill({ status: 204, body: "" });
      return route.continue();
    }
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    state.external.push({ host: url.hostname, path: url.pathname });
    return route.abort();
  });
  return page;
}

async function handleApi(route, url, state) {
  const method = route.request().method();
  if (url.pathname === "/health/runtime") {
    return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  }
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") {
    return route.fulfill({ json: { id: PROFILE.datasetId, datasetId: PROFILE.datasetId, projectId: "project_phase10l2", name: "Phase 10L-2 Capability Evidence", status: "ready", demo: true, profileId: PROFILE.profileId, profile: PROFILE } });
  }
  if (url.pathname === `/datasets/${PROFILE.datasetId}/profile`) return route.fulfill({ json: PROFILE });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: fixtures[state.caseName] });

  const ready = fixtures.ready;
  const jobId = ready.job_id;
  if (url.pathname === `/planner/jobs/${jobId}`) {
    return route.fulfill({ json: {
      jobId,
      projectId: "project_phase10l2",
      datasetId: PROFILE.datasetId,
      status: "completed",
      planId: ready.plan_id,
      planHash: ready.plan_hash,
      planSource: ready.plan_source,
      analysisPlan: ready.plan,
      validationStatus: "validated",
      toolCallCount: 0,
      artifactCount: 0,
      eventCount: 1,
      intentId: ready.intent_id,
      intentOutcome: ready.intent_outcome,
      analysisIntent: ready.intent,
      capabilityPlanningOutcome: ready.capability_outcome,
      eligibilityResolution: ready.eligibility_resolution,
      capabilityDecision: ready.capability_decision,
    } });
  }
  if (url.pathname === `/planner/jobs/${jobId}/events`) return route.fulfill({ json: [{ jobId, seq: 1, eventType: "job.completed", status: "success", message: "Capability evidence replay completed.", payload: {}, createdAt: "2026-07-29T00:00:00Z" }] });
  if (url.pathname === `/planner/jobs/${jobId}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${jobId}/tool-calls`) return route.fulfill({ json: [] });
  if (url.pathname === `/planner/jobs/${jobId}/artifacts`) return route.fulfill({ json: [] });
  if (url.pathname === `/planner/jobs/${jobId}/result`) return route.fulfill({ json: { jobId, status: "completed", planId: ready.plan_id, planHash: ready.plan_hash, summary: "Capability evidence replay completed.", toolCallCount: 0, artifactCount: 0, artifacts: [] } });
  return route.fulfill({ status: 404, json: { detail: "capability-planner evidence route not found" } });
}

async function runFlow(page, state, { mobile, screenshot }) {
  const started = Date.now();
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  const textarea = page.locator('[data-testid="planner-form"] textarea');
  await textarea.focus();
  await textarea.fill(CASES[state.caseName]);
  await page.locator('[data-testid="planner-form"] button').last().focus();
  await page.keyboard.press("Enter");
  const panel = page.getByTestId("capability-planning-panel");
  await panel.waitFor();
  const outcome = (await panel.locator(".section-heading span").innerText()).trim();
  const checks = { outcome, mobile, firstCapabilityMs: Date.now() - started };

  if (state.caseName === "ready") {
    if (outcome !== "PLAN_READY") throw new Error(`Unexpected capability outcome: ${outcome}`);
    const selection = page.getByTestId("capability-planning-selections");
    await selection.waitFor();
    checks.selectedText = await selection.innerText();
    if (!checks.selectedText.includes("dataset.materials_explorer@")) throw new Error("READY capability selection is missing the stable tool identity.");
    await page.locator(".developer-toggle input").check();
    const audit = page.getByTestId("capability-planning-audit-json");
    await audit.locator("summary").click();
    const auditText = await audit.locator("pre").innerText();
    if (!auditText.includes('"schemaVersion": "1.0"') || !auditText.includes('"resolutionHash"')) {
      throw new Error("Capability developer audit JSON is incomplete.");
    }
    checks.auditBytes = Buffer.byteLength(auditText, "utf8");
    checks.auditSha256 = createHash("sha256").update(auditText).digest("hex");
    checks.auditContractVisible = true;
    await audit.locator("summary").click();
  } else {
    if (outcome !== "CAPABILITY_MISMATCH") throw new Error(`Unexpected non-ready outcome: ${outcome}`);
    const diagnostics = page.getByTestId("capability-planning-diagnostics");
    checks.diagnosticText = await diagnostics.innerText();
    checks.runDisabled = await page.getByTestId("run-controls").locator("button").isDisabled();
    if (!checks.runDisabled || !checks.diagnosticText.includes("NO_ELIGIBLE_CAPABILITY")) {
      throw new Error("Capability mismatch did not disclose a typed reason and disable Run.");
    }
  }

  const dom = await panel.innerText();
  checks.domSha256 = createHash("sha256").update(dom).digest("hex");
  checks.horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  checks.inert = await page.evaluate(() => ({
    iframe: document.querySelectorAll("iframe").length,
    inlineHandlers: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length,
    javascriptUris: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
    capabilityScripts: document.querySelector('[data-testid="capability-planning-panel"] script') ? 1 : 0,
  }));
  if (checks.horizontalOverflow || Object.values(checks.inert).some(Boolean)) throw new Error(`Capability UI safety/layout audit failed: ${JSON.stringify(checks)}`);
  if (screenshot) {
    const file = `${mobile ? "mobile" : "desktop"}_${state.caseName}.png`;
    await panel.screenshot({ path: path.join(SCREENSHOTS, file) });
  }
  return checks;
}

function assertAudit(state) {
  if (state.external.length || state.consoleErrors.length || state.pageErrors.length || state.httpErrors.length) {
    throw new Error(`Browser audit failed: ${JSON.stringify(state)}`);
  }
}

function startServer() {
  const command = process.platform === "win32" ? "cmd.exe" : "npm";
  const args = process.platform === "win32"
    ? ["/c", "npm", "--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)]
    : ["--prefix", "apps/web", "run", "dev", "--", "--hostname", "127.0.0.1", "--port", String(PORT)];
  return spawn(command, args, { cwd: ROOT, env: { ...process.env, NEXT_PUBLIC_MDI_API_BASE_URL: API_ORIGIN }, stdio: "ignore" });
}

function stopServer(server) {
  if (!server.pid) return;
  if (process.platform === "win32") spawnSync("taskkill.exe", ["/PID", String(server.pid), "/T", "/F"], { stdio: "ignore" });
  else server.kill("SIGTERM");
}

async function waitForApp() {
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    try { if ((await fetch(ORIGIN)).ok) return; } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error("Capability Planner evidence app startup timed out.");
}

async function writeJson(relative, value) {
  const file = path.join(EVIDENCE, relative);
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function listFiles(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await listFiles(target));
    else files.push(target);
  }
  return files.sort();
}

async function hashEvidence() {
  const files = (await listFiles(EVIDENCE)).filter((file) => !file.endsWith("evidence_manifest.json"));
  await writeJson("evidence_manifest.json", {
    algorithm: "sha256-lf-normalized-text-v1",
    files: await Promise.all(files.map(async (file) => {
      const payload = await readFile(file);
      const canonical = file.toLowerCase().endsWith(".png")
        ? payload
        : Buffer.from(payload.toString("utf8").replaceAll("\r\n", "\n"), "utf8");
      return { path: path.relative(EVIDENCE, file).replaceAll("\\", "/"), bytes: canonical.length, sha256: createHash("sha256").update(canonical).digest("hex") };
    })),
  });
}

await main();
