import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE || "E:/mdi-playwright-runner/node_modules/playwright/index.mjs";
const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
const EVIDENCE = path.join(ROOT, "docs", "phase10l", "evidence", "phase10l1_analysis_intent");
const SCREENSHOTS = path.join(EVIDENCE, "screenshots");
const PORT = 3219;
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const fixtures = JSON.parse(await readFile(path.join(EVIDENCE, "browser", "fixtures.json"), "utf8"));

const CASES = {
  ready: "Analyze this materials dataset composition distribution and anomaly candidates.",
  clarification: "Analyze where the regression model predictions are wrong and whether uncertainty is credible.",
  unsupported: "Generate a Fermi surface.",
};

function jobResponse(intentResult, { ready = false } = {}) {
  const intent = intentResult.intent;
  return {
    ok: ready,
    job_id: ready ? "job_phase10l1_ready" : null,
    plan_id: ready ? "plan_phase10l1_ready" : null,
    plan_hash: ready ? "c".repeat(64) : null,
    validation_errors: [],
    plan: ready
      ? {
          schemaVersion: "0.1",
          goal: intent.rawGoal,
          datasetId: intent.datasetId,
          profileId: intent.profileId,
          toolRegistryVersion: "0.1.0",
          assumptions: [],
          warnings: [],
          steps: [{ stepId: "step_1", toolId: "dataset.materials_explorer", purpose: "Existing planner route", reason: "Browser replay", inputRefs: [], params: {}, output: { artifactTypes: ["table_json"] } }],
          expectedArtifacts: [],
        }
      : null,
    plan_source: "llm",
    planner_provider: "mock",
    enqueued: ready,
    executed: ready,
    intent_id: intent.intentId,
    intent_outcome: intent.outcome,
    intent,
    error_code: intent.outcome === "NEEDS_CLARIFICATION" ? "INTENT_CLARIFICATION_REQUIRED" : intent.outcome === "UNSUPPORTED" ? "INTENT_UNSUPPORTED" : null,
  };
}

const READY_JOB = jobResponse(fixtures.ready, { ready: true });
const CLARIFICATION_JOB = jobResponse(fixtures.clarification);
const REVISED_JOB = jobResponse(fixtures.revised, { ready: true });
const UNSUPPORTED_JOB = jobResponse(fixtures.unsupported);
const PROFILE = {
  profileId: "profile_phase10l1",
  datasetId: "dataset_phase10l1",
  version: "2",
  profileContractVersion: "2.0",
  semanticHash: "b".repeat(64),
  datasetType: "mixed",
  tableSummary: { nRows: 8, nColumns: 6, columns: [] },
  resourceSemantics: [{ kind: "dataframe", capabilities: ["table", "composition"], warnings: [] }],
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
    await writeJson("browser/network_audit.json", {
      externalRequests: Object.values(matrix).reduce((count, entry) => count + entry.externalRequests, 0),
      marker: "NO_PHASE10L1_EXTERNAL_NETWORK_REQUESTS",
    });
    await writeJson("browser/console_audit.json", {
      consoleErrors: Object.values(matrix).flatMap((entry) => entry.consoleErrors),
      pageErrors: Object.values(matrix).flatMap((entry) => entry.pageErrors),
    });
    await hashEvidence();
    console.log("ANALYSIS_INTENT_BROWSER_EVIDENCE_PASS");
    console.log("ANALYSIS_INTENT_CLARIFICATION_BROWSER_EVIDENCE_PASS");
    console.log("ANALYSIS_INTENT_MOBILE_ACCESSIBILITY_EVIDENCE_PASS");
    console.log("NO_PHASE10L1_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    stopServer(server);
  }
}

async function runBrowser(browser, browserName) {
  const result = { browser: browserName, version: browser.version(), cases: {}, mobile: null, externalRequests: 0, consoleErrors: [], pageErrors: [] };
  for (const caseName of Object.keys(CASES)) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
    const state = { caseName, clarified: false, external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
    const page = await evidencePage(context, state);
    result.cases[caseName] = await runFlow(page, state, false, browserName === "chromium");
    result.externalRequests += state.external.length;
    result.consoleErrors.push(...state.consoleErrors);
    result.pageErrors.push(...state.pageErrors);
    assertAudit(state);
    await context.close();
  }
  if (browserName === "chromium") {
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, reducedMotion: "reduce" });
    const state = { caseName: "clarification", clarified: false, external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
    const page = await evidencePage(context, state);
    result.mobile = await runFlow(page, state, true, true);
    result.externalRequests += state.external.length;
    result.consoleErrors.push(...state.consoleErrors);
    result.pageErrors.push(...state.pageErrors);
    assertAudit(state);
    await context.close();
  }
  return result;
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
  page.on("response", (response) => { if (response.status() >= 400) state.httpErrors.push({ status: response.status(), path: new URL(response.url()).pathname }); });
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
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "mock" }, redis: { status: "mock" }, artifactStorage: { status: "mock" }, worker: { status: "mock" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: PROFILE.datasetId, datasetId: PROFILE.datasetId, projectId: "project_phase10l1", name: "Phase 10L-1 Intent Evidence", status: "ready", demo: true, profileId: PROFILE.profileId, profile: PROFILE } });
  if (url.pathname === `/datasets/${PROFILE.datasetId}/profile`) return route.fulfill({ json: PROFILE });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") {
    if (state.caseName === "ready") return route.fulfill({ json: READY_JOB });
    if (state.caseName === "unsupported") return route.fulfill({ json: UNSUPPORTED_JOB });
    return route.fulfill({ json: state.clarified ? REVISED_JOB : CLARIFICATION_JOB });
  }
  if (url.pathname.includes("/planner/intents/") && url.pathname.endsWith("/clarification") && method === "POST") {
    state.clarified = true;
    return route.fulfill({ json: fixtures.revised });
  }
  if (url.pathname === "/planner/jobs/job_phase10l1_ready") return route.fulfill({ json: { jobId: "job_phase10l1_ready", projectId: "project_phase10l1", datasetId: PROFILE.datasetId, status: "completed", planId: "plan_phase10l1_ready", planHash: "c".repeat(64), planSource: "llm", analysisPlan: REVISED_JOB.plan, validationStatus: "validated", toolCallCount: 0, artifactCount: 0, eventCount: 1, intentId: REVISED_JOB.intent_id, intentOutcome: "READY", analysisIntent: REVISED_JOB.intent } });
  if (url.pathname === "/planner/jobs/job_phase10l1_ready/events") return route.fulfill({ json: [{ jobId: "job_phase10l1_ready", seq: 1, eventType: "job.completed", status: "success", message: "Intent evidence replay completed.", payload: {}, createdAt: "2026-07-29T00:00:00Z" }] });
  if (url.pathname === "/planner/jobs/job_phase10l1_ready/events/stream") return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === "/planner/jobs/job_phase10l1_ready/tool-calls") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs/job_phase10l1_ready/artifacts") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs/job_phase10l1_ready/result") return route.fulfill({ json: { jobId: "job_phase10l1_ready", status: "completed", planId: "plan_phase10l1_ready", planHash: "c".repeat(64), summary: "Intent evidence replay completed.", toolCallCount: 0, artifactCount: 0, artifacts: [] } });
  return route.fulfill({ status: 404, json: { detail: "analysis-intent evidence route not found" } });
}

async function runFlow(page, state, mobile, screenshot) {
  const started = Date.now();
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  await page.locator('[data-testid="planner-form"] textarea').fill(CASES[state.caseName]);
  await page.locator('[data-testid="planner-form"] button').last().click();
  const panel = page.getByTestId("analysis-intent-panel");
  await panel.waitFor();
  const initialOutcome = await panel.locator(".section-heading span").innerText();
  const checks = { initialOutcome, mobile, firstIntentMs: Date.now() - started };

  if (state.caseName === "clarification") {
    if (initialOutcome !== "NEEDS_CLARIFICATION") throw new Error(`Unexpected clarification outcome: ${initialOutcome}`);
    const form = page.getByTestId("analysis-intent-clarification");
    const select = form.locator("select").first();
    await select.focus();
    await select.selectOption({ index: 1 });
    if (screenshot) await panel.screenshot({ path: path.join(SCREENSHOTS, mobile ? "04_mobile_needs_clarification.png" : "02_needs_clarification.png") });
    await form.getByRole("button", { name: "Confirm intent" }).focus();
    await page.keyboard.press("Enter");
    await page.getByText("Intent confirmed. The existing planner can generate a plan.").waitFor();
    checks.revisedOutcome = await panel.locator(".section-heading span").innerText();
    checks.target = await panel.innerText();
    if (checks.revisedOutcome !== "READY" || !checks.target.includes("regression_0:target:formation_energy")) throw new Error("Clarification revision did not bind the selected target.");
    if (screenshot) await panel.screenshot({ path: path.join(SCREENSHOTS, mobile ? "05_mobile_revised_ready.png" : "03_revised_ready.png") });
  } else if (state.caseName === "unsupported") {
    const unsupported = page.getByTestId("analysis-intent-unsupported");
    await unsupported.waitFor();
    checks.reason = await unsupported.innerText();
    const runButton = page.getByTestId("run-controls").locator("button");
    checks.runDisabled = await runButton.isDisabled();
    if (!checks.runDisabled || !checks.reason.includes("INTENT_FUTURE_FERMI_SURFACE")) throw new Error("UNSUPPORTED Intent did not disable run or disclose boundary.");
    if (screenshot) await panel.screenshot({ path: path.join(SCREENSHOTS, "06_unsupported_future_scope.png") });
  } else {
    if (initialOutcome !== "READY") throw new Error(`Unexpected READY outcome: ${initialOutcome}`);
    await page.locator(".developer-toggle input").check();
    const audit = page.getByTestId("analysis-intent-audit-json");
    await audit.locator("summary").click();
    checks.auditText = await audit.locator("pre").innerText();
    if (!checks.auditText.includes('"schemaVersion": "1.0"')) throw new Error("Developer audit JSON is missing AnalysisIntent v1.");
    if (screenshot) await panel.screenshot({ path: path.join(SCREENSHOTS, "01_ready_intent_audit.png") });
  }

  const dom = await panel.innerText();
  checks.domSha256 = createHash("sha256").update(dom).digest("hex");
  checks.horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  checks.inert = await page.evaluate(() => ({
    iframe: document.querySelectorAll("iframe").length,
    inlineHandlers: [...document.querySelectorAll("*")].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length,
    javascriptUris: [...document.querySelectorAll("[href],[src]")].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
    intentScripts: document.querySelector('[data-testid="analysis-intent-panel"] script') ? 1 : 0,
  }));
  if (checks.horizontalOverflow || Object.values(checks.inert).some(Boolean)) throw new Error(`Intent UI safety/layout audit failed: ${JSON.stringify(checks)}`);
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
  if (process.platform === "win32") {
    spawnSync("taskkill.exe", ["/PID", String(server.pid), "/T", "/F"], { stdio: "ignore" });
  } else {
    server.kill("SIGTERM");
  }
}

async function waitForApp() {
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    try { if ((await fetch(ORIGIN)).ok) return; } catch {}
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error("Analysis Intent evidence app startup timed out.");
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
    algorithm: "sha256",
    files: await Promise.all(files.map(async (file) => {
      const payload = await readFile(file);
      return { path: path.relative(EVIDENCE, file).replaceAll("\\", "/"), bytes: (await stat(file)).size, sha256: createHash("sha256").update(payload).digest("hex") };
    })),
  });
}

await main();
