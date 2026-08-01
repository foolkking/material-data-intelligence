import { spawn, spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PLAYWRIGHT = process.env.MDI_PLAYWRIGHT_MODULE
  || path.join(ROOT, "apps", "web", "node_modules", "playwright", "index.mjs");
const EVIDENCE = path.join(ROOT, "docs", "phase10l", "evidence", "phase10l5_natural_language_closure");
const OUTPUT = argumentValue("--output-dir") ? path.resolve(argumentValue("--output-dir")) : EVIDENCE;
const COMPARE_WITH = argumentValue("--compare-with");
const SCREENSHOTS = path.join(OUTPUT, "screenshots");
const PORT = Number(process.env.MDI_PHASE10L5_EVIDENCE_PORT || "3223");
const ORIGIN = `http://127.0.0.1:${PORT}`;
const API_ORIGIN = "http://localhost:8000";
const CHECK_ONLY = process.argv.includes("--validate-fixtures");
const CASE_IDS = Object.freeze(["case_1", "case_2", "case_3", "case_4", "case_5"]);
const LIVE_CASE_FILES = Object.freeze({
  case_1: "case_01_dataset.json",
  case_2: "case_02_structure.json",
  case_3: "case_03_materials_ml.json",
  case_4: "case_04_phonon.json",
  case_5: "case_05_volumetric.json",
});
const NON_READY_FILES = Object.freeze({
  needs_clarification: "case_41_multi_target_clarification.json",
  unsupported: "case_42_fermi_unsupported.json",
  capability_mismatch: "case_43_uncertainty_plot_mismatch.json",
});
const CASES = Object.freeze(await loadCases());
const NON_READY_STATE_IDS = Object.freeze(["needs_clarification", "unsupported", "capability_mismatch"]);
const NON_READY_STATES = Object.freeze(await loadNonReadyStates());
const REPLAY_DISCLOSURE = "Persisted real-DeepSeek capture replay. The browser makes no live API or provider call.";
const GENERATED_FILES = [
  "accessibility_audit.json",
  "browser_capture_index.json",
  "browser_matrix.json",
  "browser_semantic_contract.json",
  "console_audit.json",
  "deterministic_replay.json",
  "dom_snapshot.json",
  "inert_rendering_audit.json",
  "mobile_smoke.json",
  "network_audit.json",
  "overflow_audit.json",
];

async function loadCases() {
  const entries = await Promise.all(CASE_IDS.map(async (caseId) => {
    const live = JSON.parse(await readFile(path.join(EVIDENCE, "deepseek_live", LIVE_CASE_FILES[caseId]), "utf8"));
    validateLiveDeepSeekRecord(live, caseId);
    const capture = browserCaptureFromLive(live);
    const run = {
      runId: live.runId,
      runHash: live.runHash,
      userText: live.userText,
      verdict: live.verdict,
      provider: live.provider,
      model: live.model,
      plan: { planId: live.planId, planHash: live.planHash },
      interpretation: { recordId: live.interpretationResponse.interpretationId },
    };
    return [caseId, { caseId, capture, run }];
  }));
  return Object.fromEntries(entries);
}

function browserCaptureFromLive(live) {
  const plan = live.analysisPlan.analysisPlan;
  const recommendations = live.interpretationResponse.recommendations || [];
  return {
    artifacts: live.artifacts,
    decision: live.capabilityDecision,
    dependencies: live.dependencies,
    eligibility: live.eligibilityResolution,
    events: live.events,
    evidence: live.evidence,
    intent: live.intent,
    interpretation: live.interpretationResponse,
    invariants: {
      ...live.invariants,
      rawUserTextPreserved: live.invariants.rawGoalPreserved,
      recommendationsNonExecutable: recommendations.every((item) => item.executionAuthorized === false
        && item.planCreated === false && item.jobCreated === false),
      selectedToolsWithinApprovedDomain: live.invariants.selectionWithinApprovedDomain,
      noForbiddenFallback: live.invariants.noFallback,
    },
    job: live.job,
    plan,
    profile: live.profile,
    request: {
      baseUrl: null,
      datasetId: live.profile.datasetId,
      enqueue: false,
      execute: false,
      intentId: null,
      intentSchemaVersion: "1.0",
      maxTokens: 8192,
      model: live.model,
      profileId: live.profile.profileId,
      projectId: live.job.projectId,
      provider: live.provider,
      secretId: null,
      selectedResourceIds: (live.intent.dataScope?.resourceRefs || []).map((item) => item.objectId),
      selectedTargetIds: (live.intent.targetSemantics || []).map((item) => item.semanticId),
      temperature: 0,
      timeoutSeconds: 120,
      userPrompt: live.userText,
    },
    result: live.result,
    toolCalls: live.toolCalls,
  };
}

function validateLiveDeepSeekRecord(live, caseId) {
  if (live.provider !== "deepseek" || live.verdict !== "PASS") throw new Error(`${caseId}: live DeepSeek record is not PASS`);
  if (live.intent?.provenance?.provider !== "deepseek" || live.capabilityDecision?.provenance?.provider !== "deepseek") {
    throw new Error(`${caseId}: intent or planner provenance is not DeepSeek`);
  }
  if (!live.providerCallAudit?.length || live.providerCallAudit.some((item) => item.realCall !== true)) {
    throw new Error(`${caseId}: real provider call audit is missing`);
  }
  if (canonicalJson(live.providerVisibleToolIds) !== canonicalJson(live.eligibleToolIds)) {
    throw new Error(`${caseId}: provider-visible tools differ from eligible tools`);
  }
  if (live.selectedToolIds.some((toolId) => !live.eligibleToolIds.includes(toolId))) {
    throw new Error(`${caseId}: selected tool escaped the eligible set`);
  }
  const rejected = new Set(live.eligibilityResolution.rejectedToolIds || []);
  if (live.providerVisibleToolIds.some((toolId) => rejected.has(toolId))) {
    throw new Error(`${caseId}: rejected tool leaked to the provider-visible set`);
  }
  if (!live.events?.length) throw new Error(`${caseId}: persisted job events are missing`);
}

async function loadNonReadyStates() {
  const metadata = {
    needs_clarification: { expectedOutcome: "NEEDS_CLARIFICATION", panelTestId: "analysis-intent-panel", markerTestId: "analysis-intent-clarification" },
    unsupported: { expectedOutcome: "UNSUPPORTED", panelTestId: "analysis-intent-panel", markerTestId: "analysis-intent-unsupported" },
    capability_mismatch: { expectedOutcome: "CAPABILITY_MISMATCH", panelTestId: "capability-planning-panel", markerTestId: "capability-planning-diagnostics" },
  };
  const entries = await Promise.all(NON_READY_STATE_IDS.map(async (stateId) => {
    const record = JSON.parse(await readFile(path.join(EVIDENCE, "historical_deepseek_replay", NON_READY_FILES[stateId]), "utf8"));
    const contract = record.browserContract;
    if (record.provider !== "deepseek" || record.verdict !== "PASS" || !record.providerCallAudit?.every((item) => item.realCall === true)) {
      throw new Error(`${stateId}: historical real-DeepSeek source is invalid`);
    }
    if (!contract || !contract.noPlanJobEnqueue || contract.sourceProvider !== "deepseek") {
      throw new Error(`${stateId}: exact non-ready browser contract is missing`);
    }
    const response = contract.response;
    if (record.planningOutcome !== metadata[stateId].expectedOutcome) {
      throw new Error(`${stateId}: historical planning outcome mismatch`);
    }
    return [stateId, {
      stateId,
      sourceCaseId: "case_1",
      sourceRunId: record.runId,
      sourceRunHash: record.runHash,
      sourceProvider: record.provider,
      sourceModel: record.model,
      userText: contract.request.userPrompt,
      profile: contract.profile,
      expectedOutcome: metadata[stateId].expectedOutcome,
      panelTestId: metadata[stateId].panelTestId,
      markerTestId: metadata[stateId].markerTestId,
      response,
    }];
  }));
  return Object.fromEntries(entries);
}

async function main() {
  validateFixtures();
  if (CHECK_ONLY) {
    console.log("PHASE10L5_BROWSER_FIXTURE_VALIDATION_PASS");
    return;
  }
  const { chromium, firefox, webkit } = await import(pathToFileURL(PLAYWRIGHT).href);
  const available = { chromium, firefox, webkit };
  const requested = (process.env.MDI_PHASE10L5_BROWSERS || "chromium,firefox,webkit")
    .split(",").map((value) => value.trim()).filter(Boolean);
  const requiredBrowsers = ["chromium", "firefox", "webkit"];
  if (requested.length !== requiredBrowsers.length
    || requiredBrowsers.some((name) => !requested.includes(name))
    || requested.some((name) => !(name in available))) {
    throw new Error("Phase 10L-5 browser evidence requires Chromium, Firefox, and WebKit.");
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
    const deterministicReplay = validateCrossBrowserReplay(matrix);
    const semanticContract = browserSemanticContract(matrix);
    const domSnapshot = collect(matrix, "domText");
    const consoleAudit = {
      consoleErrors: Object.values(matrix).flatMap((item) => item.consoleErrors),
      pageErrors: Object.values(matrix).flatMap((item) => item.pageErrors),
      marker: "NO_PHASE10L5_BROWSER_CONSOLE_ERRORS",
    };
    const networkAudit = {
      externalRequestCount: Object.values(matrix).reduce((sum, item) => sum + item.externalRequests, 0),
      marker: "NO_PHASE10L5_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS",
    };
    await writeJson("browser_capture_index.json", captureIndex());
    await writeJson("browser_matrix.json", stripDomText(matrix));
    await writeJson("dom_snapshot.json", domSnapshot);
    await writeJson("console_audit.json", consoleAudit);
    await writeJson("network_audit.json", networkAudit);
    await writeJson("accessibility_audit.json", collect(matrix, "accessibility"));
    await writeJson("overflow_audit.json", collect(matrix, "overflow"));
    await writeJson("inert_rendering_audit.json", collect(matrix, "inert"));
    await writeJson("mobile_smoke.json", matrix.chromium ? {
      evidenceMode: matrix.chromium.evidenceMode,
      viewport: [390, 844],
      ready: matrix.chromium.mobile,
      nonReady: matrix.chromium.nonReadyMobile,
    } : { unavailable: true });
    await writeJson("deterministic_replay.json", deterministicReplay);
    await writeJson("browser_semantic_contract.json", semanticContract);
    if (COMPARE_WITH) await compareSemanticContract(semanticContract, path.resolve(COMPARE_WITH));
    await writeBrowserManifest();
    console.log("PHASE10L5_FIVE_CASE_BROWSER_MATRIX_PASS");
    console.log("PHASE10L5_NON_READY_BROWSER_MATRIX_PASS");
    console.log("PHASE10L5_CHROMIUM_FIREFOX_WEBKIT_SCREENSHOTS_PASS");
    console.log("PHASE10L5_CHROMIUM_390X844_MOBILE_PASS");
    console.log("NO_PHASE10L5_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS");
    console.log("NO_PHASE10L5_BROWSER_CONSOLE_ERRORS");
    console.log("NO_HORIZONTAL_OVERFLOW");
    console.log("NO_ARTIFACT_HTML_EXECUTION");
    console.log("NO_ARTIFACT_JAVASCRIPT");
    console.log("BROWSER_EVIDENCE_MODE=PERSISTED_CAPTURE_AND_TYPED_CONTRACT_REPLAY");
    console.log("BROWSER_EVIDENCE_REAL_DEEPSEEK_CALLS=0");
    console.log("BROWSER_EVIDENCE_LIVE_API_CALLS=0");
    console.log("NO_SECRET_PATTERN_HITS");
  } finally {
    stopServer(server);
  }
}

function validateFixtures() {
  const readyOutcomes = new Set(["INTERPRETATION_READY", "INTERPRETATION_READY_WITH_LIMITS"]);
  for (const caseId of CASE_IDS) {
    const { capture, run } = CASES[caseId];
    if (run.verdict !== "PASS") throw new Error(`${caseId}: run verdict is not PASS`);
    if (capture.intent?.rawGoal !== run.userText || capture.request?.userPrompt !== run.userText) {
      throw new Error(`${caseId}: frozen natural-language input mismatch`);
    }
    if (capture.intent?.outcome !== "READY" || capture.decision?.outcome !== "PLAN_READY") {
      throw new Error(`${caseId}: intent or capability planning is not ready`);
    }
    if (!readyOutcomes.has(capture.interpretation?.outcome) || !capture.interpretation?.interpretation) {
      throw new Error(`${caseId}: grounded interpretation is not ready`);
    }
    if (capture.job?.planHash !== run.plan?.planHash || capture.job?.planId !== run.plan?.planId) {
      throw new Error(`${caseId}: persisted plan identity mismatch`);
    }
    if (capture.interpretation.interpretationId !== run.interpretation?.recordId) {
      throw new Error(`${caseId}: interpretation identity mismatch`);
    }
    if (Object.values(capture.interpretation.noExecution || {}).some(Boolean)) {
      throw new Error(`${caseId}: interpretation gained execution authority`);
    }
    const evidenceIds = new Set((capture.evidence?.evidenceItems || []).map((item) => item.evidenceItemId));
    for (const claim of capture.interpretation.interpretation.claims) {
      if (!claim.supportingEvidenceIds.length || claim.supportingEvidenceIds.some((id) => !evidenceIds.has(id))) {
        throw new Error(`${caseId}: claim evidence is missing or foreign`);
      }
    }
    for (const invariant of ["rawUserTextPreserved", "selectedSubsetEligible", "claimsHaveEvidence", "recommendationsNonExecutable"]) {
      if (capture.invariants?.[invariant] !== true) throw new Error(`${caseId}: invariant ${invariant} failed`);
    }
    assertSanitized(JSON.stringify({ run, interpretation: capture.interpretation, evidence: capture.evidence }), caseId);
  }
  if (CASES.case_4.capture.plan.schemaVersion !== "0.2" || !CASES.case_4.capture.plan.dependencyBindings?.length) {
    throw new Error("case_4: bounded phonon dependency plan is missing");
  }
  for (const stateId of NON_READY_STATE_IDS) {
    const state = NON_READY_STATES[stateId];
    if (state.response.ok || state.response.job_id || state.response.plan_id || state.response.plan_hash
      || state.response.enqueued || state.response.executed) {
      throw new Error(`${stateId}: non-ready replay gained plan, job, execution, or enqueue authority`);
    }
    if (state.response.intent.rawGoal !== state.userText) throw new Error(`${stateId}: raw goal mismatch`);
    if (stateId === "capability_mismatch") {
      if (state.response.capability_outcome !== state.expectedOutcome
        || canonicalJson(state.response.provider_visible_tool_ids) !== canonicalJson(state.response.eligibility_resolution.eligibleToolIds)
        || state.response.capability_decision.selections.length) {
        throw new Error(`${stateId}: capability mismatch replay is not isolated`);
      }
    } else if (state.response.intent_outcome !== state.expectedOutcome) {
      throw new Error(`${stateId}: intent outcome mismatch`);
    }
  }
}

async function runBrowser(browser, browserName) {
  const result = {
    browser: browserName,
    version: browser.version(),
    evidenceMode: "OFFLINE_UI_REPLAY_NO_LIVE_API_OR_PROVIDER",
    backendMode: "INTERCEPTED_PERSISTED_CAPTURE_AND_TYPED_CONTRACT_REPLAY",
    disclosure: REPLAY_DISCLOSURE,
    liveApiCalls: 0,
    realDeepSeekCalls: 0,
    desktop: {},
    nonReadyDesktop: {},
    mobile: {},
    nonReadyMobile: {},
    externalRequests: 0,
    consoleErrors: [],
    pageErrors: [],
  };
  for (const caseId of CASE_IDS) {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
    const audit = newAudit(caseId);
    const page = await evidencePage(context, audit);
    result.desktop[caseId] = await runReadyFlow(page, audit, { browserName, mobile: false });
    mergeAudit(result, audit);
    assertAudit(audit);
    await context.close();
  }
  for (const stateId of NON_READY_STATE_IDS) {
    const state = NON_READY_STATES[stateId];
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 }, reducedMotion: "reduce" });
    const audit = newAudit(state.sourceCaseId, stateId);
    const page = await evidencePage(context, audit);
    result.nonReadyDesktop[stateId] = await runNonReadyFlow(page, audit, state, { browserName, mobile: false });
    mergeAudit(result, audit);
    assertAudit(audit);
    await context.close();
  }
  if (browserName === "chromium") {
    for (const caseId of CASE_IDS) {
      const context = await browser.newContext({
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        deviceScaleFactor: 2,
        reducedMotion: "reduce",
      });
      const audit = newAudit(caseId);
      const page = await evidencePage(context, audit);
      result.mobile[caseId] = await runReadyFlow(page, audit, { browserName, mobile: true });
      mergeAudit(result, audit);
      assertAudit(audit);
      await context.close();
    }
    for (const stateId of NON_READY_STATE_IDS) {
      const state = NON_READY_STATES[stateId];
      const context = await browser.newContext({
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        deviceScaleFactor: 2,
        reducedMotion: "reduce",
      });
      const audit = newAudit(state.sourceCaseId, stateId);
      const page = await evidencePage(context, audit);
      result.nonReadyMobile[stateId] = await runNonReadyFlow(page, audit, state, { browserName, mobile: true });
      mergeAudit(result, audit);
      assertAudit(audit);
      await context.close();
    }
  }
  return result;
}

function newAudit(caseId, stateId = null) {
  return {
    caseId,
    stateId,
    external: [],
    consoleErrors: [],
    pageErrors: [],
    httpErrors: [],
    plannerRequest: null,
    interpretationRequest: null,
    interceptedApiRequests: 0,
    forwardedToLiveApi: false,
    realDeepSeekCalls: 0,
  };
}

async function evidencePage(context, audit) {
  const page = await context.newPage();
  await page.addInitScript(() => {
    window.EventSource = class { close() {} addEventListener() {} removeEventListener() {} };
  });
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text()); });
  page.on("pageerror", (error) => audit.pageErrors.push(error.message));
  page.on("response", (response) => {
    if (response.status() >= 400) audit.httpErrors.push({ status: response.status(), path: new URL(response.url()).pathname });
  });
  await page.route("**/*", async (route) => {
    const url = new URL(route.request().url());
    if (url.origin === API_ORIGIN) return handleApi(route, url, audit);
    if (["127.0.0.1", "localhost"].includes(url.hostname) && url.port === String(PORT)) {
      if (url.pathname === "/favicon.ico") return route.fulfill({ status: 204, body: "" });
      return route.continue();
    }
    if (["data:", "blob:"].includes(url.protocol)) return route.continue();
    audit.external.push({ protocol: url.protocol, host: url.hostname, path: url.pathname });
    return route.abort();
  });
  return page;
}

async function handleApi(route, url, audit) {
  const { capture, run } = CASES[audit.caseId];
  const nonReadyState = audit.stateId ? NON_READY_STATES[audit.stateId] : null;
  const activeProfile = nonReadyState?.profile || capture.profile;
  const method = route.request().method();
  audit.interceptedApiRequests += 1;
  const jobId = capture.job.jobId;
  const interpretationId = capture.interpretation.interpretationId;
  if (url.pathname === "/health/runtime") return route.fulfill({ json: runtimeHealth() });
  if (url.pathname === "/datasets" && method === "GET") return route.fulfill({ json: [] });
  if (url.pathname === "/datasets/demo" && method === "POST") {
    return route.fulfill({ json: { id: activeProfile.datasetId, datasetId: activeProfile.datasetId, projectId: capture.request.projectId, name: `Phase 10L-5 ${audit.stateId || audit.caseId}`, status: "ready", demo: true, profileId: activeProfile.profileId, profile: activeProfile } });
  }
  if (url.pathname === `/datasets/${activeProfile.datasetId}/profile`) return route.fulfill({ json: activeProfile });
  if (url.pathname === "/planner/providers") return route.fulfill({ json: { providers: [{ id: "deepseek", label: "DeepSeek (not called: capture replay)", provider: "deepseek", defaultModel: "deepseek-v4-flash", requiresSecret: false, description: REPLAY_DISCLOSURE }] } });
  if (url.pathname === "/planner/providers/test") return route.fulfill({ json: {
    ok: false,
    provider: "deepseek",
    model: "deepseek-v4-flash",
    validated: false,
    errorType: "BROWSER_CAPTURE_REPLAY_NO_LIVE_PROVIDER_CALL",
    redacted: true,
    message: REPLAY_DISCLOSURE,
  } });
  if (url.pathname.includes("/planner/providers/") || url.pathname.includes("/planner/provider")) return route.fulfill({ json: {
    ok: true,
    provider: "deepseek",
    model: "deepseek-v4-flash",
    mode: "intercepted_capture_replay",
    source: "offline_browser_evidence",
    status: "capture_replay_not_live",
    willUseLiveProvider: false,
    secretConfigured: false,
    redacted: true,
    message: REPLAY_DISCLOSURE,
  } });
  if (url.pathname === "/me/secrets") return route.fulfill({ json: [] });
  if (url.pathname === "/planner/jobs" && method === "POST") {
    const request = route.request().postDataJSON();
    const expectedText = audit.stateId ? NON_READY_STATES[audit.stateId].userText : run.userText;
    if (request.userPrompt !== expectedText || request.datasetId !== activeProfile.datasetId || request.profileId !== activeProfile.profileId) {
      throw new Error(`${audit.caseId}: Planner request drifted from frozen capture scope`);
    }
    audit.plannerRequest = {
      userPromptSha256: digestText(request.userPrompt),
      datasetId: request.datasetId,
      profileId: request.profileId,
      intercepted: true,
      forwardedToLiveApi: false,
      realDeepSeekCall: false,
    };
    if (audit.stateId) return route.fulfill({ json: NON_READY_STATES[audit.stateId].response });
    return route.fulfill({ json: createJobResponse(capture) });
  }
  if (url.pathname === `/planner/jobs/${jobId}`) return route.fulfill({ json: capture.job });
  if (url.pathname === `/planner/jobs/${jobId}/events`) return route.fulfill({ json: capture.events });
  if (url.pathname === `/planner/jobs/${jobId}/events/stream`) return route.fulfill({ status: 200, contentType: "text/event-stream", body: "" });
  if (url.pathname === `/planner/jobs/${jobId}/tool-calls`) return route.fulfill({ json: capture.toolCalls });
  if (url.pathname === `/planner/jobs/${jobId}/artifacts`) return route.fulfill({ json: [] });
  if (url.pathname === `/planner/jobs/${jobId}/result`) return route.fulfill({ json: { ...capture.result, artifacts: [] } });
  if (url.pathname === `/planner/jobs/${jobId}/dependencies`) return route.fulfill({ json: capture.dependencies });
  if (url.pathname === `/planner/jobs/${jobId}/interpretations` && method === "GET") {
    return route.fulfill({ json: { jobId, interpretations: [], runs: [], count: 0, runCount: 0 } });
  }
  if (url.pathname === `/planner/jobs/${jobId}/interpretations` && method === "POST") {
    const request = route.request().postDataJSON();
    if (request.mode !== "DETERMINISTIC" || request.expectedPlanHash !== capture.job.planHash) {
      throw new Error(`${audit.caseId}: interpretation request drifted from frozen capture`);
    }
    audit.interpretationRequest = { mode: request.mode, expectedPlanHash: request.expectedPlanHash };
    return route.fulfill({ json: capture.interpretation });
  }
  if (url.pathname === `/planner/interpretations/${interpretationId}/evidence`) return route.fulfill({ json: capture.evidence });
  return route.fulfill({ status: 404, json: { detail: "phase10l5 browser evidence route not found" } });
}

function runtimeHealth() {
  return {
    api: { status: "ok" },
    database: { status: "capture_replay" },
    redis: { status: "capture_replay" },
    artifactStorage: { status: "capture_replay" },
    worker: { status: "capture_replay" },
    llmProvider: { status: "capture_replay_not_live", provider: "deepseek", model: "deepseek-v4-flash", reason: REPLAY_DISCLOSURE },
  };
}

function createJobResponse(capture) {
  return {
    ok: true,
    job_id: capture.job.jobId,
    plan_id: capture.job.planId,
    plan_hash: capture.job.planHash,
    validation_errors: [],
    plan: capture.plan,
    plan_source: "capability_planner",
    planner_provider: capture.decision.provenance.provider,
    enqueued: true,
    executed: true,
    intent_id: capture.intent.intentId,
    intent_outcome: capture.intent.outcome,
    intent: capture.intent,
    capability_outcome: capture.decision.outcome,
    eligibility_resolution: capture.eligibility,
    capability_decision: capture.decision,
    provider_visible_tool_ids: capture.eligibility.eligibleToolIds,
    plan_schema_version: capture.plan.schemaVersion,
    graph_hash: capture.plan.graphHash || null,
    dependency_bindings: capture.plan.dependencyBindings || [],
    topological_order: capture.dependencies.topologicalOrder || [],
  };
}

async function preparePlanner(page, audit, userText) {
  const { capture } = CASES[audit.caseId];
  const activeProfile = audit.stateId ? NON_READY_STATES[audit.stateId].profile : capture.profile;
  await page.goto(`${ORIGIN}/?phase10l5BrowserEvidence=${audit.stateId || audit.caseId}`, { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle");
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.getByText(/capture_replay_not_live/).first().waitFor();
  const bodyText = await page.locator("body").innerText();
  if (!bodyText.includes("capture_replay_not_live")) {
    throw new Error(`${audit.stateId || audit.caseId}: replay disclosure is not visible before interaction`);
  }
  await page.locator(".global-context-bar .context-button").first().click();
  const dialog = page.getByRole("dialog");
  await dialog.waitFor();
  await dialog.getByRole("button").nth(1).click();
  await dialog.waitFor({ state: "hidden" });
  const form = page.getByTestId("planner-form");
  await form.locator("textarea").fill(userText);
  await form.locator("button").last().click();
  if (!audit.plannerRequest || audit.plannerRequest.forwardedToLiveApi || audit.plannerRequest.realDeepSeekCall) {
    throw new Error(`${audit.stateId || audit.caseId}: intercepted replay request audit is missing`);
  }
  if (audit.plannerRequest.datasetId !== activeProfile.datasetId) throw new Error("Replay dataset scope changed");
}

async function runReadyFlow(page, audit, { browserName, mobile }) {
  const { capture, run } = CASES[audit.caseId];
  const started = Date.now();
  await preparePlanner(page, audit, run.userText);
  await page.getByTestId("main-workspace").locator(".main-tab-list button").nth(2).click();
  const panel = page.getByTestId("grounded-interpretation-panel");
  await panel.waitFor();
  const generate = panel.getByRole("button", { name: "Generate grounded interpretation", exact: true });
  if (!(await generate.isEnabled())) throw new Error(`${audit.caseId}: interpretation action is disabled`);
  await generate.focus();
  await page.keyboard.press("Enter");
  await panel.getByText(capture.interpretation.outcome, { exact: true }).waitFor();
  const claims = panel.getByTestId("grounded-claim");
  const expectedClaimCount = capture.interpretation.interpretation.claims.length;
  if (await claims.count() !== expectedClaimCount) throw new Error(`${audit.caseId}: rendered claim count mismatch`);
  const firstDisclosure = panel.locator("details").filter({ hasText: "Show evidence" }).first();
  await firstDisclosure.locator("summary").focus();
  await page.keyboard.press("Enter");
  const evidence = panel.locator(".interpretation-evidence").first();
  await evidence.waitFor();
  await page.keyboard.press("Tab");
  const evidenceFocusedByKeyboardFlow = await evidence.evaluate((node) => document.activeElement === node);
  const evidenceText = await evidence.innerText();
  for (const label of ["Calculated result", "Source tool", "Artifact contract", "Field locator", "Lineage"]) {
    if (!evidenceText.toLocaleLowerCase("en-US").includes(label.toLocaleLowerCase("en-US"))) {
      throw new Error(`${audit.caseId}: evidence drill-down is missing ${label}`);
    }
  }
  await page.locator(".developer-toggle input").check();
  const auditDetails = panel.getByTestId("interpretation-audit-json");
  await auditDetails.locator("summary").click();
  const auditText = await auditDetails.locator("pre").innerText();
  if (!auditText.includes(capture.interpretation.interpretationId)) throw new Error(`${audit.caseId}: audit JSON identity is missing`);
  await auditDetails.locator("summary").click();
  const panelText = await panel.innerText();
  const pageText = await page.getByTestId("main-workspace").innerText();
  assertSanitized(`${panelText}\n${auditText}`, `${audit.caseId} DOM`);
  const inert = await inertAudit(page, '[data-testid="grounded-interpretation-panel"]');
  const overflow = await overflowAudit(page, panel);
  const accessibility = await accessibilityAudit(page, panel, evidence, expectedClaimCount, evidenceFocusedByKeyboardFlow);
  if (Object.values(inert).some((value) => typeof value === "number" ? value !== 0 : value === true)) {
    throw new Error(`${audit.caseId}: inert rendering audit failed`);
  }
  if (overflow.document || overflow.viewportEscapingElements) throw new Error(`${audit.caseId}: horizontal overflow detected: ${JSON.stringify(overflow)}`);
  if (!accessibility.pass) throw new Error(`${audit.caseId}: accessibility basics failed: ${JSON.stringify(accessibility)}`);
  const screenshotFile = `${browserName}_${mobile ? "mobile_390x844" : "desktop"}_ready_${audit.caseId}.png`;
  await panel.screenshot({ path: path.join(SCREENSHOTS, screenshotFile) });
  const semantic = {
    caseId: audit.caseId,
    runId: run.runId,
    userTextSha256: digestText(run.userText),
    intentId: capture.intent.intentId,
    selectedToolIds: capture.decision.selections.map((item) => item.toolId),
    planId: capture.job.planId,
    planHash: capture.job.planHash,
    planSchemaVersion: capture.plan.schemaVersion,
    graphHash: capture.plan.graphHash || null,
    jobId: capture.job.jobId,
    jobStatus: capture.job.status,
    interpretationId: capture.interpretation.interpretationId,
    interpretationOutcome: capture.interpretation.outcome,
    claimCount: expectedClaimCount,
    evidenceItemCount: capture.interpretation.evidenceItemCount,
    noExecution: capture.interpretation.noExecution,
    inert,
    overflow,
    accessibility,
  };
  return {
    ...semantic,
    evidenceMode: "PERSISTED_CAPTURE_UI_REPLAY_NO_LIVE_API_OR_PROVIDER",
    replayDisclosure: REPLAY_DISCLOSURE,
    screenshotFile: `screenshots/${screenshotFile}`,
    liveApiCalls: 0,
    realDeepSeekCalls: 0,
    mobile,
    viewport: page.viewportSize(),
    elapsedMs: Date.now() - started,
    plannerRequest: audit.plannerRequest,
    interpretationRequest: audit.interpretationRequest,
    focusedTag: await page.evaluate(() => document.activeElement?.tagName || null),
    domText: pageText,
    domSha256: digestText(pageText),
    semanticSha256: digestText(canonicalJson(semantic)),
  };
}

async function runNonReadyFlow(page, audit, state, { browserName, mobile }) {
  const started = Date.now();
  await preparePlanner(page, audit, state.userText);
  const panel = page.getByTestId(state.panelTestId);
  await panel.waitFor();
  await panel.getByText(state.expectedOutcome, { exact: true }).waitFor();
  await panel.getByTestId(state.markerTestId).waitFor();
  const runControl = page.getByTestId("run-controls").getByRole("button");
  if (await runControl.isEnabled()) throw new Error(`${state.stateId}: Run is enabled for a non-ready replay`);

  const developerToggle = page.locator(".developer-toggle input");
  await developerToggle.focus();
  await page.keyboard.press("Space");
  const focusedByKeyboard = await developerToggle.evaluate((node) => document.activeElement === node);
  const auditDetails = panel.locator("details.raw-json");
  await auditDetails.locator("summary").focus();
  await page.keyboard.press("Enter");
  const auditText = await auditDetails.locator("pre").innerText();
  if (!auditText.includes(state.response.intent_id)) throw new Error(`${state.stateId}: inert audit JSON identity is missing`);
  assertSanitized(auditText, `${state.stateId} non-ready DOM`);
  await auditDetails.locator("summary").focus();
  await page.keyboard.press("Enter");

  const inert = await inertAudit(page, `[data-testid="${state.panelTestId}"]`);
  const overflow = await overflowAudit(page, panel);
  const accessibility = await nonReadyAccessibilityAudit(page, panel, focusedByKeyboard, state.markerTestId);
  if (Object.values(inert).some((value) => typeof value === "number" ? value !== 0 : value === true)) {
    throw new Error(`${state.stateId}: inert rendering audit failed`);
  }
  if (overflow.document || overflow.viewportEscapingElements) {
    throw new Error(`${state.stateId}: horizontal overflow detected: ${JSON.stringify(overflow)}`);
  }
  if (!accessibility.pass) throw new Error(`${state.stateId}: accessibility basics failed: ${JSON.stringify(accessibility)}`);

  const screenshotFile = `${browserName}_${mobile ? "mobile_390x844" : "desktop"}_non_ready_${state.stateId}.png`;
  await panel.screenshot({ path: path.join(SCREENSHOTS, screenshotFile) });
  const semantic = {
    stateId: state.stateId,
    sourceCaseId: state.sourceCaseId,
    userTextSha256: digestText(state.userText),
    outcome: state.expectedOutcome,
    intentId: state.response.intent_id,
    jobId: null,
    planId: null,
    enqueued: false,
    executed: false,
    runEnabled: false,
    evidenceMode: "TYPED_NON_READY_UI_CONTRACT_REPLAY_NO_LIVE_API_OR_PROVIDER",
    replayDisclosure: REPLAY_DISCLOSURE,
    liveApiCalls: 0,
    realDeepSeekCalls: 0,
    inert,
    overflow,
    accessibility,
  };
  return {
    ...semantic,
    screenshotFile: `screenshots/${screenshotFile}`,
    mobile,
    viewport: page.viewportSize(),
    elapsedMs: Date.now() - started,
    plannerRequest: audit.plannerRequest,
    domText: await panel.innerText(),
    semanticSha256: digestText(canonicalJson(semantic)),
  };
}

async function inertAudit(page, panelSelector) {
  return page.evaluate((selector) => {
    const panel = document.querySelector(selector);
    const nodes = panel ? [...panel.querySelectorAll("*")] : [];
    return {
      iframes: document.querySelectorAll("iframe").length,
      scriptsInPanel: panel?.querySelectorAll("script").length || 0,
      inlineHandlers: nodes.filter((node) => [...node.attributes].some((attribute) => /^on/i.test(attribute.name))).length,
      javascriptUris: nodes.filter((node) => /javascript:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
      externalUris: nodes.filter((node) => /^https?:/i.test(node.getAttribute("href") || node.getAttribute("src") || "")).length,
      rawHtmlElements: panel?.querySelectorAll("object,embed").length || 0,
    };
  }, panelSelector);
}

async function overflowAudit(page, panel) {
  return {
    document: await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1),
    panelInternalScroll: await panel.evaluate((node) => node.scrollWidth > node.clientWidth + 1),
    viewportEscapingElements: await page.evaluate(() => [...document.querySelectorAll("body *")].filter((node) => {
      const style = window.getComputedStyle(node);
      if (style.display === "none" || style.visibility === "hidden" || style.position === "fixed") return false;
      const rect = node.getBoundingClientRect();
      if (!(rect.width > 0 && (rect.left < -1 || rect.right > document.documentElement.clientWidth + 1))) return false;
      let parent = node.parentElement;
      while (parent && parent !== document.body) {
        const parentStyle = window.getComputedStyle(parent);
        const parentRect = parent.getBoundingClientRect();
        if (["auto", "scroll", "hidden", "clip"].includes(parentStyle.overflowX)
          && parentRect.left >= -1 && parentRect.right <= document.documentElement.clientWidth + 1) return false;
        parent = parent.parentElement;
      }
      return true;
    }).length),
    documentWidth: await page.evaluate(() => document.documentElement.clientWidth),
    documentScrollWidth: await page.evaluate(() => document.documentElement.scrollWidth),
  };
}

async function accessibilityAudit(page, panel, evidence, claimCount, evidenceFocusedByKeyboardFlow) {
  const ariaLive = await panel.getAttribute("aria-live");
  const tabCount = await page.getByTestId("main-workspace").locator(".main-tab-list button").count();
  const unnamedControls = await panel.locator("button,summary,input,select,textarea").evaluateAll((nodes) => nodes.filter((node) => {
    const labelledBy = (node.getAttribute("aria-labelledby") || "").split(/\s+/).filter(Boolean)
      .map((id) => document.getElementById(id)?.textContent || "").join(" ");
    const labels = "labels" in node ? [...node.labels].map((label) => label.textContent || "").join(" ") : "";
    const wrappedLabel = node.closest("label")?.textContent || "";
    const name = node.getAttribute("aria-label") || node.getAttribute("title") || labelledBy || labels || wrappedLabel || node.textContent || "";
    return !name.trim();
  }).length);
  const evidenceFocusable = await evidence.getAttribute("tabindex");
  return {
    pass: ariaLive === "polite" && tabCount === 3 && unnamedControls === 0 && evidenceFocusable === "0" && evidenceFocusedByKeyboardFlow && claimCount > 0,
    ariaLive,
    tabCount,
    unnamedControls,
    evidenceFocusable,
    evidenceFocusedByKeyboardFlow,
    claimCount,
  };
}

async function nonReadyAccessibilityAudit(page, panel, focusedByKeyboard, markerTestId) {
  const ariaLive = await panel.getAttribute("aria-live");
  const statusOrAlertCount = await panel.locator('[role="status"], [role="alert"]').count();
  const stateMarkerCount = await panel.getByTestId(markerTestId).count();
  const headingCount = await panel.locator("h2,h3").count();
  const unnamedControls = await panel.locator("button,summary,input,select,textarea").evaluateAll((nodes) => nodes.filter((node) => {
    const labelledBy = (node.getAttribute("aria-labelledby") || "").split(/\s+/).filter(Boolean)
      .map((id) => document.getElementById(id)?.textContent || "").join(" ");
    const labels = "labels" in node ? [...node.labels].map((label) => label.textContent || "").join(" ") : "";
    const name = node.getAttribute("aria-label") || node.getAttribute("title") || labelledBy || labels || node.textContent || "";
    return !name.trim();
  }).length);
  return {
    pass: ariaLive === "polite" && stateMarkerCount === 1 && headingCount > 0 && unnamedControls === 0 && focusedByKeyboard,
    ariaLive,
    statusOrAlertCount,
    stateMarkerCount,
    headingCount,
    unnamedControls,
    focusedByKeyboard,
  };
}

function mergeAudit(result, audit) {
  result.externalRequests += audit.external.length;
  result.consoleErrors.push(...audit.consoleErrors);
  result.pageErrors.push(...audit.pageErrors);
}

function assertAudit(audit) {
  if (audit.external.length || audit.consoleErrors.length || audit.pageErrors.length || audit.httpErrors.length) {
    throw new Error(`Browser audit failed: ${JSON.stringify(audit)}`);
  }
}

function validateCrossBrowserReplay(matrix) {
  const browsers = Object.keys(matrix);
  const baseline = matrix[browsers[0]];
  const cases = {};
  for (const caseId of CASE_IDS) {
    const desktopHashes = Object.fromEntries(browsers.map((browser) => [browser, matrix[browser].desktop[caseId].semanticSha256]));
    const stable = Object.values(desktopHashes).every((hash) => hash === baseline.desktop[caseId].semanticSha256);
    if (!stable) throw new Error(`${caseId}: cross-browser semantic replay changed`);
    cases[caseId] = { desktopHashes, stable };
  }
  const nonReadyStates = {};
  for (const stateId of NON_READY_STATE_IDS) {
    const desktopHashes = Object.fromEntries(browsers.map((browser) => [browser, matrix[browser].nonReadyDesktop[stateId].semanticSha256]));
    const stable = Object.values(desktopHashes).every((hash) => hash === baseline.nonReadyDesktop[stateId].semanticSha256);
    if (!stable) throw new Error(`${stateId}: cross-browser non-ready semantic replay changed`);
    nonReadyStates[stateId] = { desktopHashes, stable };
  }
  return {
    schemaVersion: "1.0",
    evidenceMode: "OFFLINE_UI_REPLAY_NO_LIVE_API_OR_PROVIDER",
    cases,
    nonReadyStates,
    allStable: [...Object.values(cases), ...Object.values(nonReadyStates)].every((item) => item.stable),
  };
}

function browserSemanticContract(matrix) {
  const projection = (value) => ({
    caseId: value.caseId,
    runId: value.runId,
    userTextSha256: value.userTextSha256,
    intentId: value.intentId,
    selectedToolIds: value.selectedToolIds,
    planId: value.planId,
    planHash: value.planHash,
    planSchemaVersion: value.planSchemaVersion,
    graphHash: value.graphHash,
    jobId: value.jobId,
    jobStatus: value.jobStatus,
    interpretationId: value.interpretationId,
    interpretationOutcome: value.interpretationOutcome,
    claimCount: value.claimCount,
    evidenceItemCount: value.evidenceItemCount,
    noExecution: value.noExecution,
    inert: value.inert,
    overflow: value.overflow,
    accessibility: value.accessibility,
    mobile: value.mobile,
    viewport: value.viewport,
    evidenceMode: value.evidenceMode,
    screenshotFile: value.screenshotFile,
  });
  const nonReadyProjection = (value) => ({
    stateId: value.stateId,
    sourceCaseId: value.sourceCaseId,
    userTextSha256: value.userTextSha256,
    outcome: value.outcome,
    intentId: value.intentId,
    jobId: value.jobId,
    planId: value.planId,
    enqueued: value.enqueued,
    executed: value.executed,
    runEnabled: value.runEnabled,
    inert: value.inert,
    overflow: value.overflow,
    accessibility: value.accessibility,
    mobile: value.mobile,
    viewport: value.viewport,
    evidenceMode: value.evidenceMode,
    screenshotFile: value.screenshotFile,
  });
  return {
    schemaVersion: "1.0",
    evidenceMode: "OFFLINE_UI_REPLAY_NO_LIVE_API_OR_PROVIDER",
    disclosure: REPLAY_DISCLOSURE,
    liveApiCalls: 0,
    realDeepSeekCalls: 0,
    captureContractHash: digestText(canonicalJson(captureIndex())),
    browsers: Object.fromEntries(Object.entries(matrix).map(([browser, result]) => [browser, {
      evidenceMode: result.evidenceMode,
      backendMode: result.backendMode,
      desktop: Object.fromEntries(Object.entries(result.desktop).map(([caseId, value]) => [caseId, projection(value)])),
      nonReadyDesktop: Object.fromEntries(Object.entries(result.nonReadyDesktop).map(([stateId, value]) => [stateId, nonReadyProjection(value)])),
      mobile: Object.fromEntries(Object.entries(result.mobile).map(([caseId, value]) => [caseId, projection(value)])),
      nonReadyMobile: Object.fromEntries(Object.entries(result.nonReadyMobile).map(([stateId, value]) => [stateId, nonReadyProjection(value)])),
      externalRequestCount: result.externalRequests,
      consoleErrorCount: result.consoleErrors.length,
      pageErrorCount: result.pageErrors.length,
    }])),
  };
}

function captureIndex() {
  return {
    schemaVersion: "1.0",
    evidenceMode: "OFFLINE_UI_REPLAY_NO_LIVE_API_OR_PROVIDER",
    disclosure: REPLAY_DISCLOSURE,
    liveApiCalls: 0,
    realDeepSeekCalls: 0,
    replayMode: "PERSISTED_CAPTURE_UI_REPLAY",
    cases: CASE_IDS.map((caseId) => {
      const { capture, run } = CASES[caseId];
      return {
        caseId,
        runId: run.runId,
        userTextSha256: digestText(run.userText),
        intentId: capture.intent.intentId,
        eligibleToolIds: capture.eligibility.eligibleToolIds,
        selectedToolIds: capture.decision.selections.map((item) => item.toolId),
        planId: capture.job.planId,
        planHash: capture.job.planHash,
        planSchemaVersion: capture.plan.schemaVersion,
        graphHash: capture.plan.graphHash || null,
        jobId: capture.job.jobId,
        interpretationId: capture.interpretation.interpretationId,
        interpretationOutcome: capture.interpretation.outcome,
        sourceProvider: capture.request.provider,
        intentProvider: capture.intent.provenance.provider,
        plannerProvider: capture.decision.provenance.provider,
        artifactProjection: "METADATA_INDEX_ONLY_NO_RAW_ARTIFACT_CONTENT",
        artifacts: capture.artifacts.map((artifact) => ({
          artifactId: artifact.id,
          artifactType: artifact.type,
          contentHash: artifact.contentHash,
          sizeBytes: artifact.sizeBytes,
        })),
      };
    }),
    nonReadyStates: NON_READY_STATE_IDS.map((stateId) => {
      const state = NON_READY_STATES[stateId];
      return {
        stateId,
        source: "PERSISTED_REAL_DEEPSEEK_NON_READY_CONTRACT",
        sourceRunId: state.sourceRunId,
        sourceRunHash: state.sourceRunHash,
        expectedOutcome: state.expectedOutcome,
        userTextSha256: digestText(state.userText),
        intentId: state.response.intent_id,
        jobId: null,
        planId: null,
        enqueued: false,
        executed: false,
        provider: state.sourceProvider,
        model: state.sourceModel,
        sourceRealDeepSeekCall: true,
        browserReplayRealDeepSeekCall: false,
      };
    }),
  };
}

function stripDomText(matrix) {
  return Object.fromEntries(Object.entries(matrix).map(([browser, result]) => [browser, {
    ...result,
    desktop: Object.fromEntries(Object.entries(result.desktop).map(([caseId, value]) => [caseId, { ...value, domText: undefined }])),
    nonReadyDesktop: Object.fromEntries(Object.entries(result.nonReadyDesktop).map(([stateId, value]) => [stateId, { ...value, domText: undefined }])),
    mobile: Object.fromEntries(Object.entries(result.mobile).map(([caseId, value]) => [caseId, { ...value, domText: undefined }])),
    nonReadyMobile: Object.fromEntries(Object.entries(result.nonReadyMobile).map(([stateId, value]) => [stateId, { ...value, domText: undefined }])),
  }]));
}

function collect(matrix, key) {
  return Object.fromEntries(Object.entries(matrix).map(([browser, result]) => [browser, {
    desktop: Object.fromEntries(Object.entries(result.desktop).map(([caseId, value]) => [caseId, value[key]])),
    nonReadyDesktop: Object.fromEntries(Object.entries(result.nonReadyDesktop).map(([stateId, value]) => [stateId, value[key]])),
    mobile: Object.fromEntries(Object.entries(result.mobile).map(([caseId, value]) => [caseId, value[key]])),
    nonReadyMobile: Object.fromEntries(Object.entries(result.nonReadyMobile).map(([stateId, value]) => [stateId, value[key]])),
  }]));
}

function assertSanitized(value, label) {
  const patterns = [
    /(?:sk-[A-Za-z0-9_-]{16,}|api[_-]?key\s*[:=]|bearer\s+[A-Za-z0-9._-]{16,})/i,
    /DEEPSEEK_KEY/i,
    /(?:[A-Za-z]:\\Users\\|\/home\/[^/]+\/|\/Users\/[^/]+\/)/i,
  ];
  if (patterns.some((pattern) => pattern.test(value))) throw new Error(`${label}: secret or private path detected`);
}

async function compareSemanticContract(actual, baselinePath) {
  const baseline = JSON.parse(await readFile(baselinePath, "utf8"));
  if (canonicalJson(actual) !== canonicalJson(baseline)) {
    throw new Error(`Browser semantic replay differs from committed contract: ${baselinePath}`);
  }
  console.log("PHASE10L5_COMMITTED_BROWSER_SEMANTIC_REPLAY_PASS");
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

function digestText(value) {
  return createHash("sha256").update(value).digest("hex");
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
  throw new Error("Phase 10L-5 browser evidence app startup timed out.");
}

async function writeJson(relative, value) {
  const serialized = `${JSON.stringify(value, null, 2)}\n`;
  assertSanitized(serialized, relative);
  const target = path.join(OUTPUT, relative);
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, serialized, "utf8");
}

async function writeBrowserManifest() {
  const screenshotFiles = ["chromium", "firefox", "webkit"].flatMap((browserName) => [
    ...CASE_IDS.map((caseId) => `screenshots/${browserName}_desktop_ready_${caseId}.png`),
    ...NON_READY_STATE_IDS.map((stateId) => `screenshots/${browserName}_desktop_non_ready_${stateId}.png`),
    ...(browserName === "chromium" ? [
      ...CASE_IDS.map((caseId) => `screenshots/chromium_mobile_390x844_ready_${caseId}.png`),
      ...NON_READY_STATE_IDS.map((stateId) => `screenshots/chromium_mobile_390x844_non_ready_${stateId}.png`),
    ] : []),
  ]);
  const files = [...GENERATED_FILES, ...screenshotFiles];
  const records = [];
  for (const relative of files) {
    const raw = await readFile(path.join(OUTPUT, relative));
    const canonical = relative.endsWith(".png") ? raw : Buffer.from(raw.toString("utf8").replaceAll("\r\n", "\n"), "utf8");
    records.push({ path: relative, bytes: canonical.length, sha256: createHash("sha256").update(canonical).digest("hex") });
  }
  await writeJson("browser_evidence_manifest.json", {
    algorithm: "sha256-lf-normalized-text-v1-raw-png",
    evidenceMode: "OFFLINE_UI_REPLAY_NO_LIVE_API_OR_PROVIDER",
    disclosure: REPLAY_DISCLOSURE,
    liveApiCalls: 0,
    realDeepSeekCalls: 0,
    requiredBrowsers: ["chromium", "firefox", "webkit"],
    requiredMobileViewport: [390, 844],
    readyScreenshotCount: CASE_IDS.length * 3 + CASE_IDS.length,
    nonReadyScreenshotCount: NON_READY_STATE_IDS.length * 3 + NON_READY_STATE_IDS.length,
    files: records,
  });
}

await main();
