import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE
  || path.join(ROOT, "apps", "web", "node_modules", "playwright", "index.mjs");
const EVIDENCE = path.join(ROOT, "docs", "phase10l", "evidence", "phase10l4_grounded_interpretation");
const L3_EVIDENCE = path.join(ROOT, "docs", "phase10l", "evidence", "phase10l3_bounded_multi_tool");
const OUTPUT = argumentValue("--output-dir") ? path.resolve(argumentValue("--output-dir")) : EVIDENCE;
const COMPARE_WITH = argumentValue("--compare-with");
const SCREENSHOTS = path.join(OUTPUT, "screenshots");
const PORT = Number(process.env.MDI_PHASE10L4_EVIDENCE_PORT || "3222");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const CHECK_ONLY = process.argv.includes("--validate-fixtures");
const CAPTURES = JSON.parse(await readFile(path.join(EVIDENCE, "browser", "fixtures.json"), "utf8"));
const L3 = JSON.parse(await readFile(path.join(L3_EVIDENCE, "browser", "fixtures.json"), "utf8"));
const READY = L3.ready;
const PROFILE = L3.profile;

const CASES = Object.freeze({
  deterministic: makeCase(CAPTURES.chain, CAPTURES.chain.api, CAPTURES.chain.evidence),
  strict_provider: makeCase(CAPTURES.chain, CAPTURES.chain.strictProviderApi, CAPTURES.chain.strictProviderEvidence),
  partial: makeCase(CAPTURES.partial, CAPTURES.partial.api, CAPTURES.partial.evidence),
  no_supported_evidence: makeCase(CAPTURES.chain, CAPTURES.noEvidence, null),
  validation_failure: makeCase(CAPTURES.chain, CAPTURES.validationFailure, null),
  source_integrity_failure: makeCase(CAPTURES.chain, CAPTURES.integrityFailure, null),
});

function makeCase(runtimeCapture, response, evidence) {
  return {
    jobId: runtimeCapture.runtime.job_id,
    planId: runtimeCapture.runtime.plan_id,
    planHash: runtimeCapture.planHash,
    plan: runtimeCapture.plan,
    jobStatus: runtimeCapture.runtime.status,
    execution: runtimeCapture.execution,
    lineage: runtimeCapture.lineage,
    response: normalizeResponse(response),
    evidence,
  };
}

function normalizeResponse(response) {
  if (response?.bundleId !== undefined) return response;
  return {
    outcome: response.outcome,
    interpretationId: null,
    bundleId: null,
    bundleHash: null,
    sourceJobId: null,
    sourcePlanId: null,
    sourcePlanHash: null,
    sourceGraphHash: null,
    mode: null,
    claims: [],
    warnings: [],
    limitations: [],
    recommendations: [],
    partialResultState: false,
    repairCount: 0,
    diagnostics: response.diagnostics || [],
    evidenceItemCount: 0,
    noExecution: {
      toolCallCreated: false,
      planCreated: false,
      jobCreated: false,
      enqueued: false,
      recommendationExecutionAuthorized: false,
    },
    execution: null,
    interpretation: null,
  };
}

async function main() {
  validateFixtures();
  if (CHECK_ONLY) {
    console.log("PHASE10L4_BROWSER_FIXTURE_VALIDATION_PASS");
    return;
  }
  const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
  const available = { chromium, firefox, webkit };
  const requested = (process.env.MDI_PHASE10L4_BROWSERS || "chromium,firefox,webkit")
    .split(",").map((item) => item.trim()).filter(Boolean);
  if (!requested.length || requested.some((name) => !(name in available))) {
    throw new Error("MDI_PHASE10L4_BROWSERS must contain chromium, firefox, and/or webkit.");
  }
  await mkdir(SCREENSHOTS, { recursive: true });
  const server = startServer();
  try {
    await waitForApp();
    const matrix = {};
    for (const browserName of requested) {
      const browser = await available[browserName].launch({ headless: true });
      try {
        matrix[browserName] = await runBrowser(browser, browserName);
      } finally {
        await browser.close();
      }
    }
    await writeJson("browser_matrix.json", matrix);
    await writeJson("dom_snapshot.json", collect(matrix, "domText"));
    await writeJson("console_audit.json", {
      consoleErrors: Object.values(matrix).flatMap((item) => item.consoleErrors),
      pageErrors: Object.values(matrix).flatMap((item) => item.pageErrors),
    });
    await writeJson("network_audit.json", {
      externalRequests: Object.values(matrix).reduce((sum, item) => sum + item.externalRequests, 0),
      marker: "NO_PHASE10L4_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS",
    });
    await writeJson("mobile_smoke.json", matrix.chromium?.mobile || { unavailable: true });
    await writeJson("deterministic_replay.json", Object.fromEntries(
      Object.entries(matrix).map(([browser, value]) => [browser, value.deterministicReplay]),
    ));
    const semanticContract = browserSemanticContract(matrix);
    await writeJson("browser_semantic_contract.json", semanticContract);
    if (COMPARE_WITH) await compareSemanticContract(semanticContract, path.resolve(COMPARE_WITH));
    await hashEvidence();
    console.log("PHASE10L4_GROUNDED_INTERPRETATION_BROWSER_PASS");
    console.log("PHASE10L4_PARTIAL_AND_FAILURE_BROWSER_PASS");
    console.log("PHASE10L4_MOBILE_ACCESSIBILITY_PASS");
    console.log("NO_PHASE10L4_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_ARTIFACT_HTML_EXECUTION");
    console.log("NO_ARTIFACT_JAVASCRIPT");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    stopServer(server);
  }
}

function validateFixtures() {
  const readyOutcomes = new Set(["INTERPRETATION_READY", "INTERPRETATION_READY_WITH_LIMITS"]);
  if (!readyOutcomes.has(CASES.deterministic.response.outcome)) throw new Error("deterministic fixture is not ready");
  if (!readyOutcomes.has(CASES.strict_provider.response.outcome) || CASES.strict_provider.response.mode !== "STRICT_PROVIDER") throw new Error("strict-provider fixture is not ready");
  if (CASES.partial.response.outcome !== "INTERPRETATION_READY_WITH_LIMITS" || !CASES.partial.response.partialResultState) throw new Error("partial fixture is not limited");
  if (CASES.no_supported_evidence.response.outcome !== "NO_SUPPORTED_EVIDENCE") throw new Error("no-evidence fixture mismatch");
  if (CASES.validation_failure.response.outcome !== "VALIDATION_FAILED") throw new Error("validation fixture mismatch");
  if (CASES.source_integrity_failure.response.outcome !== "SOURCE_INTEGRITY_FAILED") throw new Error("integrity fixture mismatch");
  for (const [caseName, fixture] of Object.entries(CASES)) {
    const noExecution = fixture.response.noExecution;
    if (!noExecution || Object.values(noExecution).some(Boolean)) throw new Error(`${caseName}: interpretation gained execution authority`);
  }
  const visible = new Set(CAPTURES.chain.providerVisibleEvidenceIds);
  const projected = new Set((CAPTURES.chain.strictProviderEvidence?.evidenceItems || []).map((item) => item.evidenceItemId));
  if (visible.size !== projected.size || [...visible].some((item) => !projected.has(item))) throw new Error("provider-visible evidence isolation mismatch");
}

async function runBrowser(browser, browserName) {
  const result = {
    browser: browserName,
    version: browser.version(),
    backendMode: "FIXTURE_REPLAY_FROM_PERSISTED_API_CASES",
    cases: {},
    mobile: {},
    externalRequests: 0,
    consoleErrors: [],
    pageErrors: [],
  };
  for (const caseName of Object.keys(CASES)) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
    const audit = newAudit(caseName);
    const page = await evidencePage(context, audit);
    result.cases[caseName] = await runFlow(page, audit, { mobile: false, screenshot: browserName === "chromium" });
    mergeAudit(result, audit);
    assertAudit(audit);
    await context.close();
  }
  const replayContext = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
  const replayAudit = newAudit("deterministic");
  const replayPage = await evidencePage(replayContext, replayAudit);
  const replay = await runFlow(replayPage, replayAudit, { mobile: false, screenshot: false });
  mergeAudit(result, replayAudit);
  assertAudit(replayAudit);
  await replayContext.close();
  result.deterministicReplay = {
    firstSemanticSha256: result.cases.deterministic.semanticReplaySha256,
    secondSemanticSha256: replay.semanticReplaySha256,
    firstDomSha256: result.cases.deterministic.domSha256,
    secondDomSha256: replay.domSha256,
    stable: result.cases.deterministic.semanticReplaySha256 === replay.semanticReplaySha256
      && result.cases.deterministic.domSha256 === replay.domSha256,
  };
  if (!result.deterministicReplay.stable) {
    throw new Error(`${browserName}: deterministic replay changed semantic output; ${describeTextDifference(result.cases.deterministic.domText, replay.domText)}; hashes=${JSON.stringify(result.deterministicReplay)}`);
  }
  if (browserName === "chromium") {
    for (const caseName of ["deterministic", "partial", "no_supported_evidence"]) {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2, reducedMotion: "reduce" });
      const audit = newAudit(caseName);
      const page = await evidencePage(context, audit);
      result.mobile[caseName] = await runFlow(page, audit, { mobile: true, screenshot: true });
      mergeAudit(result, audit);
      assertAudit(audit);
      await context.close();
    }
  }
  return result;
}

function newAudit(caseName) {
  return { caseName, external: [], consoleErrors: [], pageErrors: [], httpErrors: [] };
}

async function evidencePage(context, audit) {
  const page = await context.newPage();
  await page.addInitScript(() => {
    window.EventSource = class { close() {} addEventListener() {} removeEventListener() {} };
  });
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => { if (response.status() >= 400) audit.httpErrors.push({ status: response.status(), url: response.url() }); });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin === API_ORIGIN) return handleApi(route, url, audit);
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

async function handleApi(route, url, audit) {
  const fixture = CASES[audit.caseName];
  const method = route.request().method();
  const datasetId = fixture.plan.datasetId;
  if (url.pathname === "/health/runtime") return route.fulfill({ json: { api: { status: "ok" }, database: { status: "replay" }, redis: { status: "replay" }, artifactStorage: { status: "replay" }, worker: { status: "replay" }, llmProvider: { status: "mock" } } });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") return route.fulfill({ json: { id: datasetId, datasetId, projectId: "project_l3_runtime", name: "Phase 10L-4 grounded evidence", status: "ready", demo: true, profileId: fixture.plan.profileId, profile: PROFILE } });
  if (url.pathname === `/datasets/${datasetId}/profile`) return route.fulfill({ json: PROFILE });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "mock", label: "Mock Planner", provider: "mock", defaultModel: "mock", requiresSecret: false }] } });
  if (url.pathname.includes("/planner/providers/")) return route.fulfill({ json: { ok: true, provider: "mock", mode: "mock", secretConfigured: false } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") return route.fulfill({ json: createJobResponse(fixture) });
  if (url.pathname === `/planner/jobs/${fixture.jobId}`) return route.fulfill({ json: jobDetail(fixture) });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/events`) return route.fulfill({ json: jobEvents(fixture) });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/tool-calls`) return route.fulfill({ json: [] });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/artifacts`) return route.fulfill({ json: [] });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/result`) return route.fulfill({ json: { jobId: fixture.jobId, status: fixture.jobStatus, planId: fixture.planId, planHash: fixture.planHash, summary: fixture.execution.outcome, toolCallCount: fixture.execution.succeededCount + fixture.execution.failedCount, artifactCount: fixture.lineage.length, artifacts: [] } });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/dependencies`) return route.fulfill({ json: dependencyAudit(fixture) });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/interpretations` && method === "GET") return route.fulfill({ json: { jobId: fixture.jobId, interpretations: [], runs: [], count: 0, runCount: 0 } });
  if (url.pathname === `/planner/jobs/${fixture.jobId}/interpretations` && method === "POST") {
    const requestBody = route.request().postDataJSON();
    const expectedMode = audit.caseName === "strict_provider" ? "STRICT_PROVIDER" : "DETERMINISTIC";
    if (requestBody.mode !== expectedMode) throw new Error(`${audit.caseName}: expected ${expectedMode} request, received ${requestBody.mode}`);
    audit.interpretationRequestMode = requestBody.mode;
    return route.fulfill({ json: fixture.response });
  }
  if (fixture.response.interpretationId && url.pathname === `/planner/interpretations/${fixture.response.interpretationId}/evidence`) return route.fulfill({ json: fixture.evidence });
  return route.fulfill({ status: 404, json: { detail: "phase10l4 browser evidence route not found" } });
}

function createJobResponse(fixture) {
  return {
    ...READY,
    job_id: fixture.jobId,
    plan_id: fixture.planId,
    plan_hash: fixture.planHash,
    plan: fixture.plan,
    plan_schema_version: fixture.plan.schemaVersion,
    graph_hash: fixture.plan.graphHash,
    dependency_bindings: fixture.plan.dependencyBindings,
    topological_order: fixture.execution.topologicalOrder,
  };
}

function jobDetail(fixture) {
  return {
    jobId: fixture.jobId,
    projectId: "project_l3_runtime",
    datasetId: fixture.plan.datasetId,
    status: fixture.jobStatus,
    planId: fixture.planId,
    planHash: fixture.planHash,
    planSource: "mock",
    analysisPlan: fixture.plan,
    validationStatus: "validated",
    toolCallCount: fixture.execution.succeededCount + fixture.execution.failedCount,
    artifactCount: fixture.lineage.length,
    eventCount: 2,
    intentId: READY.intent_id,
    intentOutcome: "READY",
    analysisIntent: READY.intent,
    capabilityPlanningOutcome: "PLAN_READY",
    eligibilityResolution: READY.eligibility_resolution,
    capabilityDecision: READY.capability_decision,
    dependencyExecutionSummary: {
      executionId: fixture.execution.executionId,
      outcome: fixture.execution.outcome,
      graphHash: fixture.plan.graphHash,
      succeededCount: fixture.execution.succeededCount,
      failedCount: fixture.execution.failedCount,
      blockedCount: fixture.execution.blockedCount,
      notStartedCount: fixture.execution.notStartedCount,
    },
  };
}

function dependencyAudit(fixture) {
  return {
    jobId: fixture.jobId,
    planId: fixture.planId,
    planHash: fixture.planHash,
    planSchemaVersion: fixture.plan.schemaVersion,
    graphHash: fixture.plan.graphHash,
    dependencyBindings: fixture.plan.dependencyBindings,
    plannedBindingRecords: [],
    topologicalOrder: fixture.execution.topologicalOrder,
    execution: fixture.execution,
    bindingResolutions: fixture.execution.bindings,
    artifactLineage: fixture.lineage,
  };
}

function jobEvents(fixture) {
  return [
    { jobId: fixture.jobId, seq: 1, eventType: "plan.loaded", status: "success", message: "Exact plan loaded.", payload: {}, createdAt: "2026-07-30T00:00:00Z" },
    { jobId: fixture.jobId, seq: 2, eventType: fixture.jobStatus === "completed" ? "job.completed" : "job.partial_success", status: fixture.jobStatus, message: fixture.execution.outcome, payload: {}, createdAt: "2026-07-30T00:00:01Z" },
  ];
}

async function runFlow(page, audit, { mobile, screenshot }) {
  const fixture = CASES[audit.caseName];
  const started = Date.now();
  await page.goto(ORIGIN, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".global-context-bar .context-button").first().click();
  await page.getByRole("dialog").getByRole("button").nth(1).click();
  const form = page.getByTestId("planner-form");
  await form.locator("textarea").fill("Interpret the completed scientific results using only grounded evidence.");
  await form.locator("button").last().click();
  await page.getByRole("button", { name: "结果与导出" }).click();
  const panel = page.getByTestId("grounded-interpretation-panel");
  await panel.waitFor();
  if (audit.caseName === "strict_provider") {
    const strictMode = panel.getByRole("button", { name: "Strict provider" });
    await strictMode.focus();
    await page.keyboard.press("Enter");
    if ((await strictMode.getAttribute("aria-pressed")) !== "true") throw new Error("strict-provider mode was not keyboard selected");
  }
  const generateButton = panel.getByRole("button", { name: "Generate grounded interpretation", exact: true });
  await generateButton.click();
  await generateButton.waitFor({ state: "visible" });
  await panel.getByText(fixture.response.outcome, { exact: true }).waitFor();
  const text = await panel.innerText();
  if (fixture.response.interpretation) {
    const claims = panel.getByTestId("grounded-claim");
    if (await claims.count() !== fixture.response.interpretation.claims.length) throw new Error(`${audit.caseName}: claim count mismatch`);
    const firstDisclosure = panel.locator("details").filter({ hasText: "Show evidence" }).first();
    await firstDisclosure.locator("summary").focus();
    await page.keyboard.press("Enter");
    const evidence = panel.locator(".interpretation-evidence").first();
    await evidence.waitFor();
    await evidence.focus();
    const evidenceText = await evidence.innerText();
    const normalizedEvidenceText = evidenceText.toLocaleLowerCase("en-US");
    const requiredEvidenceLabels = ["Calculated result", "Source tool", "Artifact contract", "Field locator"];
    const missingEvidenceLabels = requiredEvidenceLabels.filter((label) => !normalizedEvidenceText.includes(label.toLocaleLowerCase("en-US")));
    if (missingEvidenceLabels.length) throw new Error(`${audit.caseName}: evidence drill-down is missing ${missingEvidenceLabels.join(", ")}; text=${JSON.stringify(evidenceText)}`);
    if (fixture.response.partialResultState && !text.includes("Limitations")) throw new Error("partial interpretation omitted limitations");
  } else if (fixture.response.outcome === "NO_SUPPORTED_EVIDENCE" && !text.includes("No grounded findings are available")) {
    throw new Error("no-supported-evidence state emitted findings");
  }
  await page.locator(".developer-toggle input").check();
  let auditText = "";
  if (fixture.response.interpretation) {
    const details = panel.getByTestId("interpretation-audit-json");
    await details.locator("summary").click();
    auditText = await details.locator("pre").innerText();
    if (!auditText.includes(fixture.response.interpretation.interpretationId) || /storageKey|bucket|localPath|api[_-]?key/i.test(auditText)) throw new Error(`${audit.caseName}: audit JSON is unsafe or incomplete`);
  }
  const inert = await page.evaluate(() => ({
    iframes: document.querySelectorAll("iframe").length,
    scriptsInPanel: document.querySelectorAll('[data-testid="grounded-interpretation-panel"] script').length,
    inlineHandlers: [...document.querySelectorAll('[data-testid="grounded-interpretation-panel"] *')].filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length,
    javascriptUris: [...document.querySelectorAll('[data-testid="grounded-interpretation-panel"] [href],[data-testid="grounded-interpretation-panel"] [src]')].filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
  }));
  const horizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (horizontalOverflow || Object.values(inert).some(Boolean)) throw new Error(`${audit.caseName}: inert/mobile layout audit failed`);
  const secretHits = `${text}\n${auditText}`.match(/(?:sk-[A-Za-z0-9_-]{16,}|api[_-]?key\s*[:=]|bearer\s+[A-Za-z0-9._-]{16,})/gi) || [];
  if (secretHits.length) throw new Error(`${audit.caseName}: secret-shaped DOM content found`);
  if (screenshot) await panel.screenshot({ path: path.join(SCREENSHOTS, `${mobile ? "mobile" : "desktop"}_${audit.caseName}.png`) });
  const semanticReplay = {
    case: audit.caseName,
    outcome: fixture.response.outcome,
    mode: fixture.response.mode,
    requestMode: audit.interpretationRequestMode,
    mobile,
    claimCount: fixture.response.claims.length,
    evidenceItemCount: fixture.response.evidenceItemCount,
    repairCount: fixture.response.repairCount,
    noExecution: fixture.response.noExecution,
    horizontalOverflow,
    inert,
    domSha256: createHash("sha256").update(text).digest("hex"),
  };
  return {
    case: audit.caseName,
    outcome: fixture.response.outcome,
    mode: fixture.response.mode,
    requestMode: audit.interpretationRequestMode,
    mobile,
    elapsedMs: Date.now() - started,
    claimCount: fixture.response.claims.length,
    evidenceItemCount: fixture.response.evidenceItemCount,
    repairCount: fixture.response.repairCount,
    noExecution: fixture.response.noExecution,
    horizontalOverflow,
    inert,
    focusedTag: await page.evaluate(() => document.activeElement?.tagName || null),
    domText: text,
    domSha256: semanticReplay.domSha256,
    semanticReplaySha256: createHash("sha256").update(JSON.stringify(semanticReplay)).digest("hex"),
  };
}

function mergeAudit(result, audit) {
  result.externalRequests += audit.external.length;
  result.consoleErrors.push(...audit.consoleErrors);
  result.pageErrors.push(...audit.pageErrors);
}

function assertAudit(audit) {
  if (audit.external.length || audit.consoleErrors.length || audit.pageErrors.length || audit.httpErrors.length) throw new Error(`Browser audit failed: ${JSON.stringify(audit)}`);
}

function collect(matrix, key) {
  return Object.fromEntries(Object.entries(matrix).map(([browser, result]) => [browser, {
    desktop: Object.fromEntries(Object.entries(result.cases).map(([name, value]) => [name, value[key]])),
    mobile: Object.fromEntries(Object.entries(result.mobile).map(([name, value]) => [name, value[key]])),
  }]));
}

function browserSemanticContract(matrix) {
  const caseProjection = (value) => ({
    outcome: value.outcome,
    mode: value.mode,
    requestMode: value.requestMode,
    mobile: value.mobile,
    claimCount: value.claimCount,
    evidenceItemCount: value.evidenceItemCount,
    repairCount: value.repairCount,
    noExecution: value.noExecution,
    horizontalOverflow: value.horizontalOverflow,
    inert: value.inert,
  });
  return {
    schemaVersion: "1.0",
    fixtureContractHash: createHash("sha256").update(canonicalJson(CAPTURES)).digest("hex"),
    browsers: Object.fromEntries(Object.entries(matrix).map(([name, result]) => [name, {
      backendMode: result.backendMode,
      cases: Object.fromEntries(Object.entries(result.cases).map(([caseName, value]) => [caseName, caseProjection(value)])),
      mobile: Object.fromEntries(Object.entries(result.mobile).map(([caseName, value]) => [caseName, caseProjection(value)])),
      deterministicReplayStable: result.deterministicReplay.stable,
      externalRequests: result.externalRequests,
      consoleErrorCount: result.consoleErrors.length,
      pageErrorCount: result.pageErrors.length,
    }])),
  };
}

async function compareSemanticContract(actual, baselinePath) {
  const baseline = JSON.parse(await readFile(baselinePath, "utf8"));
  if (canonicalJson(actual) !== canonicalJson(baseline)) {
    throw new Error(`Browser semantic replay differs from committed contract: ${baselinePath}`);
  }
  console.log("PHASE10L4_COMMITTED_BROWSER_SEMANTIC_REPLAY_PASS");
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function describeTextDifference(first, second) {
  let index = 0;
  while (index < first.length && index < second.length && first[index] === second[index]) index += 1;
  const start = Math.max(0, index - 80);
  const end = index + 120;
  return `firstDifference=${index} first=${JSON.stringify(first.slice(start, end))} second=${JSON.stringify(second.slice(start, end))}`;
}

function argumentValue(name) {
  const index = process.argv.indexOf(name);
  if (index < 0) return null;
  const value = process.argv[index + 1];
  if (!value || value.startsWith("--")) throw new Error(`${name} requires a value.`);
  return value;
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
  throw new Error("Phase 10L-4 browser evidence app startup timed out.");
}

async function writeJson(relative, value) {
  const target = path.join(OUTPUT, relative);
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function listFiles(directory) {
  const output = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) output.push(...await listFiles(target));
    else output.push(target);
  }
  return output.sort();
}

async function hashEvidence() {
  const files = (await listFiles(OUTPUT)).filter((file) => !file.endsWith("evidence_manifest.json"));
  await writeJson("evidence_manifest.json", {
    algorithm: "sha256-lf-normalized-text-v1",
    files: await Promise.all(files.map(async (file) => {
      const raw = await readFile(file);
      const canonical = file.toLowerCase().endsWith(".png") ? raw : Buffer.from(raw.toString("utf8").replaceAll("\r\n", "\n"), "utf8");
      return { path: path.relative(OUTPUT, file).replaceAll("\\", "/"), bytes: canonical.length, sha256: createHash("sha256").update(canonical).digest("hex") };
    })),
  });
}

await main();
