import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const EVIDENCE = process.env.MDI_PHASE10L3_EVIDENCE_DIR
  ? path.resolve(process.env.MDI_PHASE10L3_EVIDENCE_DIR)
  : path.join(ROOT, "docs", "phase10l", "evidence", "phase10l3_bounded_multi_tool");
const SCREENSHOTS = path.join(EVIDENCE, "screenshots");
const PORT = 3221;
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const CAPTURE_FIXTURES = JSON.parse(await readFile(path.join(EVIDENCE, "browser", "fixtures.json"), "utf8"));
const READY_CAPTURE = CAPTURE_FIXTURES.ready;
const SUCCESS_CAPTURE = CAPTURE_FIXTURES.success;
const PARTIAL_CAPTURE = CAPTURE_FIXTURES.partial;
const GRAPH_HASH = SUCCESS_CAPTURE.graphHash;
const PLAN_HASH = SUCCESS_CAPTURE.planHash;
const DATASET_ID = SUCCESS_CAPTURE.plan.datasetId;
const PROFILE_ID = SUCCESS_CAPTURE.plan.profileId;
const PROJECT_ID = SUCCESS_CAPTURE.lineage[0].projectId;
const CASE_GOAL = READY_CAPTURE.intent.rawGoal;
const CHECK_ONLY = process.argv.includes("--validate-fixtures");

const BAND_BINDING = Object.freeze(SUCCESS_CAPTURE.plan.dependencyBindings.find((item) => item.consumerInputPort === "band"));
const INDEPENDENT_PRODUCER_STEP_ID = SUCCESS_CAPTURE.plan.dependencyBindings.find(
  (item) => item.consumerStepId === BAND_BINDING.consumerStepId && item.bindingId !== BAND_BINDING.bindingId,
).producerStepId;
const PROFILE = Object.freeze(CAPTURE_FIXTURES.profile);

const CASES = Object.freeze({
  success: captureCase(SUCCESS_CAPTURE),
  partial: captureCase(PARTIAL_CAPTURE),
});

function captureCase(capture) {
  return {
    jobId: capture.api.jobId,
    planId: capture.api.planId,
    plan: capture.plan,
    audit: capture.api,
    jobStatus: capture.result.status === "completed" ? "completed" : "failed",
    toolCalls: capture.toolCalls,
    artifacts: capture.artifacts,
  };
}

async function main() {
  validateFixtures();
  if (CHECK_ONLY) {
    console.log("PHASE10L3_BROWSER_FIXTURE_VALIDATION_PASS");
    return;
  }
  const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
  const browserTypes = { chromium, firefox, webkit };
  const requestedBrowsers = (process.env.MDI_PHASE10L3_BROWSERS || "chromium,firefox,webkit")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
  if (!requestedBrowsers.length || requestedBrowsers.some((name) => !(name in browserTypes))) {
    throw new Error("MDI_PHASE10L3_BROWSERS must contain chromium, firefox, and/or webkit.");
  }
  await mkdir(path.join(EVIDENCE, "browser"), { recursive: true });
  await mkdir(SCREENSHOTS, { recursive: true });
  const server = startServer();
  try {
    await waitForApp();
    const matrix = {};
    for (const name of requestedBrowsers) {
      const browserType = browserTypes[name];
      const browser = await browserType.launch({ headless: true });
      try {
        matrix[name] = await runBrowser(browser, name);
      } finally {
        await browser.close();
      }
    }
    await writeJson("browser/browser_matrix.json", matrix);
    await writeJson("browser/dom_snapshot.json", collectCaseMetric(matrix, "domText", true));
    await writeJson("browser/accessibility_audit.json", collectCaseMetric(matrix, "accessibility", true));
    await writeJson("browser/overflow_audit.json", collectCaseMetric(matrix, "horizontalOverflow", true));
    await writeJson("browser/network_audit.json", {
      externalRequests: Object.values(matrix).reduce((sum, item) => sum + item.externalRequests, 0),
      marker: "NO_PHASE10L3_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS",
    });
    await writeJson("browser/console_audit.json", {
      consoleErrors: Object.values(matrix).flatMap((item) => item.consoleErrors),
      pageErrors: Object.values(matrix).flatMap((item) => item.pageErrors),
    });
    await hashEvidence();
    console.log("PHASE10L3_DEPENDENCY_BROWSER_EVIDENCE_PASS");
    console.log("PHASE10L3_PARTIAL_EXECUTION_BROWSER_EVIDENCE_PASS");
    console.log("PHASE10L3_ARTIFACT_LINEAGE_BROWSER_EVIDENCE_PASS");
    console.log("PHASE10L3_DEPENDENCY_MOBILE_ACCESSIBILITY_EVIDENCE_PASS");
    console.log("NO_PHASE10L3_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_ARTIFACT_HTML_EXECUTION");
    console.log("NO_ARTIFACT_JAVASCRIPT");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    stopServer(server);
  }
}

function validateFixtures() {
  for (const [caseName, fixture] of Object.entries(CASES)) {
    if (fixture.plan.schemaVersion !== "0.2" || fixture.plan.graphHash !== fixture.audit.graphHash) throw new Error(`${caseName}: plan graph identity mismatch`);
    if (!fixture.plan.dependencyBindings.length || fixture.plan.dependencyBindings.length !== fixture.audit.dependencyBindings.length) throw new Error(`${caseName}: binding mismatch`);
    if (fixture.plan.dependencyBindings.some((binding) => !fixture.audit.dependencyBindings.some((item) => item.bindingId === binding.bindingId))) throw new Error(`${caseName}: binding identity mismatch`);
    if (new Set(fixture.audit.topologicalOrder).size !== fixture.plan.steps.length) throw new Error(`${caseName}: topological order does not cover each step exactly once`);
    if (!fixture.audit.artifactLineage.length) throw new Error(`${caseName}: artifact lineage is required`);
  }
  const success = CASES.success.audit.execution;
  if (success.outcome !== "ALL_SUCCEEDED" || success.steps.some((item) => item.state !== "SUCCEEDED")) throw new Error("success fixture is not all-succeeded");
  const partial = CASES.partial.audit.execution;
  const byStep = Object.fromEntries(partial.steps.map((item) => [item.stepId, item]));
  if (
    partial.outcome !== "PARTIAL_RESULTS"
    || byStep[BAND_BINDING.producerStepId]?.state !== "FAILED"
    || byStep[BAND_BINDING.consumerStepId]?.state !== "BLOCKED_DEPENDENCY"
    || byStep[INDEPENDENT_PRODUCER_STEP_ID]?.state !== "SUCCEEDED"
  ) {
    throw new Error("partial fixture does not preserve the independent branch and blocked dependent semantics");
  }
}

async function runBrowser(browser, browserName) {
  const result = { browser: browserName, version: browser.version(), cases: {}, mobile: {}, externalRequests: 0, consoleErrors: [], pageErrors: [] };
  for (const caseName of Object.keys(CASES)) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
    const state = auditState(caseName);
    const page = await evidencePage(context, state);
    result.cases[caseName] = await runFlow(page, state, { mobile: false, screenshot: browserName === "chromium" });
    mergeAudit(result, state);
    assertAudit(state);
    await context.close();
  }
  if (browserName === "chromium") {
    for (const caseName of Object.keys(CASES)) {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2, reducedMotion: "reduce" });
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
  const fixture = CASES[state.caseName];
  const method = route.request().method();
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "replay" }, redis: { status: "replay" }, artifactStorage: { status: "replay" }, worker: { status: "replay" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: DATASET_ID, datasetId: DATASET_ID, projectId: PROJECT_ID, name: "Phase 10L-3 Dependency Evidence", status: "ready", demo: true, profileId: PROFILE_ID, profile: PROFILE } });
  if (url.pathname === `/datasets/${DATASET_ID}/profile`) return route.fulfill({ json: PROFILE });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: createJobResponse(fixture) });
  if (url.pathname === `/planner/jobs/${fixture.jobId}`) return route.fulfill({ json: jobDetail(fixture) });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/events`) return route.fulfill({ json: jobEvents(fixture) });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/tool-calls`) return route.fulfill({ json: fixture.toolCalls });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/artifacts`) return route.fulfill({ json: fixture.artifacts });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/result`) return route.fulfill({ json: { jobId: fixture.jobId, status: fixture.jobStatus, planId: fixture.planId, planHash: fixture.audit.planHash, summary: fixture.audit.execution.outcome, toolCallCount: fixture.toolCalls.length, artifactCount: fixture.artifacts.length, artifacts: fixture.artifacts } });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/dependencies`) return route.fulfill({ json: fixture.audit });
  return route.fulfill({ status: 404, json: { detail: "phase10l3 dependency evidence route not found" } });
}

function createJobResponse(fixture) {
  return {
    ...READY_CAPTURE,
    job_id: fixture.jobId,
    plan_id: fixture.planId,
    plan_hash: fixture.audit.planHash,
    plan: fixture.plan,
    plan_schema_version: "0.2",
    graph_hash: fixture.audit.graphHash,
    dependency_bindings: fixture.audit.dependencyBindings,
    topological_order: fixture.audit.topologicalOrder,
  };
}

function jobDetail(fixture) {
  const execution = fixture.audit.execution;
  return {
    jobId: fixture.jobId,
    projectId: PROJECT_ID,
    datasetId: DATASET_ID,
    status: fixture.jobStatus,
    planId: fixture.planId,
    planHash: fixture.audit.planHash,
    planSource: "llm",
    analysisPlan: fixture.plan,
    validationStatus: "validated",
    toolCallCount: execution.succeededCount + execution.failedCount,
    artifactCount: fixture.audit.artifactLineage.length,
    eventCount: 2,
    intentId: READY_CAPTURE.intent_id,
    intentOutcome: "READY",
    analysisIntent: READY_CAPTURE.intent,
    capabilityPlanningOutcome: "PLAN_READY",
    eligibilityResolution: READY_CAPTURE.eligibility_resolution,
    capabilityDecision: READY_CAPTURE.capability_decision,
    dependencyExecutionSummary: {
      executionId: execution.executionId,
      outcome: execution.outcome,
      graphHash: GRAPH_HASH,
      succeededCount: execution.succeededCount,
      failedCount: execution.failedCount,
      blockedCount: execution.blockedCount,
      notStartedCount: execution.notStartedCount,
    },
  };
}

function jobEvents(fixture) {
  const failure = fixture.audit.execution.outcome === "PARTIAL_RESULTS";
  return [
    { jobId: fixture.jobId, seq: 1, eventType: "plan.loaded", status: "success", message: "AnalysisPlan 0.2 loaded.", payload: { graphHash: GRAPH_HASH }, createdAt: "2026-07-30T00:00:00Z" },
    { jobId: fixture.jobId, seq: 2, eventType: failure ? "job.failed" : "job.completed", status: failure ? "failed" : "success", message: fixture.audit.execution.outcome, payload: { executionId: fixture.audit.execution.executionId }, createdAt: "2026-07-30T00:00:01Z" },
  ];
}

async function runFlow(page, state, { mobile, screenshot }) {
  const fixture = CASES[state.caseName];
  const started = Date.now();
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  const textarea = page.locator('[data-testid="planner-form"] textarea');
  await textarea.focus();
  await textarea.fill(CASE_GOAL);
  await page.locator('[data-testid="planner-form"] button').last().click();
  const panel = page.getByTestId("dependency-execution-panel");
  await panel.waitFor();
  await panel.getByText(fixture.audit.execution.outcome, { exact: true }).waitFor();

  const text = await panel.innerText();
  const bindingText = `${BAND_BINDING.producerStepId}:${BAND_BINDING.producerOutputPort} -> ${BAND_BINDING.consumerStepId}:${BAND_BINDING.consumerInputPort}`;
  if (!text.includes(bindingText) || !text.includes(BAND_BINDING.artifactContractVersion)) throw new Error(`${state.caseName}: exact dependency ports are not visible`);
  if (!text.includes(fixture.audit.topologicalOrder.join(" -> "))) throw new Error(`${state.caseName}: deterministic topological order is not visible`);
  if (
    state.caseName === "partial"
    && (
      !text.includes("BLOCKED_DEPENDENCY")
      || !text.includes(`Blocked by ${BAND_BINDING.producerStepId}`)
      || !text.includes(INDEPENDENT_PRODUCER_STEP_ID)
      || !text.includes("SUCCEEDED")
    )
  ) {
    throw new Error("partial execution did not disclose the blocked dependent and successful independent branch");
  }
  const lineagePanel = panel.getByTestId("artifact-lineage-list");
  await lineagePanel.waitFor();
  const lineageText = await lineagePanel.innerText();
  for (const item of fixture.audit.artifactLineage) {
    if (!lineageText.includes(item.producerToolId) || !lineageText.includes(item.outputPort)) throw new Error(`${state.caseName}: artifact lineage is incomplete`);
  }

  const bindingCard = panel.locator(".dependency-card").first();
  await bindingCard.focus();
  const accessibility = await panel.evaluate((element) => {
    const binding = element.querySelector(".dependency-card");
    const stepList = element.querySelector(".dependency-step-list");
    return {
      ariaLive: element.getAttribute("aria-live"),
      bindingTabIndex: binding?.getAttribute("tabindex"),
      stepListLabel: stepList?.getAttribute("aria-label"),
      focusedTag: document.activeElement?.tagName,
      focusedClass: document.activeElement?.getAttribute("class"),
    };
  });
  if (accessibility.ariaLive !== "polite" || accessibility.bindingTabIndex !== "0" || accessibility.stepListLabel !== "Dependency execution states" || accessibility.focusedTag !== "ARTICLE") {
    throw new Error(`${state.caseName}: dependency accessibility contract failed: ${JSON.stringify(accessibility)}`);
  }

  await page.locator(".developer-toggle input").check();
  const audit = panel.getByTestId("dependency-audit-json");
  await audit.locator("summary").click();
  const auditText = await audit.locator("pre").innerText();
  if (!auditText.includes('"schemaVersion": "0.2"') || !auditText.includes(BAND_BINDING.bindingId) || !auditText.includes(fixture.audit.execution.executionId)) {
    throw new Error(`${state.caseName}: inert developer audit JSON is incomplete`);
  }
  const secretPatternHits = [...`${text}\n${auditText}`.matchAll(/(?:sk-[A-Za-z0-9_-]{16,}|api[_-]?key\s*[:=]\s*[A-Za-z0-9_-]{12,}|bearer\s+[A-Za-z0-9._-]{16,})/gi)].map((match) => match[0]);
  if (secretPatternHits.length) throw new Error(`${state.caseName}: secret-shaped text reached the DOM`);

  const inert = await page.evaluate(() => ({
    iframe: document.querySelectorAll("iframe").length,
    inlineHandlers: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length,
    javascriptUris: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
    auditScripts: document.querySelector('[data-testid="dependency-audit-json"] script') ? 1 : 0,
    auditHtmlNodes: document.querySelector('[data-testid="dependency-audit-json"] iframe, [data-testid="dependency-audit-json"] object, [data-testid="dependency-audit-json"] embed') ? 1 : 0,
  }));
  const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (horizontalOverflow || Object.values(inert).some(Boolean)) throw new Error(`${state.caseName}: dependency UI safety/layout audit failed: ${JSON.stringify({ horizontalOverflow, inert })}`);

  await audit.locator("summary").click();
  if (screenshot) {
    await panel.screenshot({ path: path.join(SCREENSHOTS, `${mobile ? "mobile" : "desktop"}_${state.caseName}.png`) });
  }
  return {
    case: state.caseName,
    outcome: fixture.audit.execution.outcome,
    mobile,
    firstDependencyPanelMs: Date.now() - started,
    graphHash: GRAPH_HASH,
    topologicalOrder: fixture.audit.topologicalOrder,
    binding: bindingText,
    lineageIds: fixture.audit.artifactLineage.map((item) => item.lineageId),
    blockedDependent: state.caseName === "partial" ? BAND_BINDING.consumerStepId : null,
    independentSucceeded: state.caseName === "partial" ? INDEPENDENT_PRODUCER_STEP_ID : null,
    accessibility,
    horizontalOverflow,
    inert,
    secretPatternHits: secretPatternHits.length,
    domText: text,
    domSha256: createHash("sha256").update(text).digest("hex"),
    auditBytes: Buffer.byteLength(auditText, "utf8"),
    auditSha256: createHash("sha256").update(auditText).digest("hex"),
  };
}

function assertAudit(state) {
  if (state.external.length || state.consoleErrors.length || state.pageErrors.length || state.httpErrors.length) {
    throw new Error(`Browser audit failed: ${JSON.stringify(state)}`);
  }
}

function collectCaseMetric(matrix, key, includeMobile) {
  const output = {};
  for (const [browserName, browserResult] of Object.entries(matrix)) {
    output[browserName] = {
      desktop: Object.fromEntries(Object.entries(browserResult.cases).map(([name, item]) => [name, item[key]])),
      ...(includeMobile && Object.keys(browserResult.mobile).length ? { mobile: Object.fromEntries(Object.entries(browserResult.mobile).map(([name, item]) => [name, item[key]])) } : {}),
    };
  }
  return output;
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
  throw new Error("Phase 10L-3 dependency evidence app startup timed out.");
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
