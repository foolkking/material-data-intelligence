import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const ORIGIN = process.env.MDI_ACCEPTANCE_ORIGIN || "http://127.0.0.1:3022";
const API_ORIGIN = process.env.MDI_ACCEPTANCE_API_ORIGIN || "http://127.0.0.1:8017";
const PACKAGE_ROOT = path.resolve(process.env.MDI_ACCEPTANCE_PACKAGE_ROOT || path.join(ROOT, "_qualification/work/phase_bc_r1_7/authority_package"));
const OUTPUT_ROOT = path.resolve(process.env.MDI_ACCEPTANCE_OUTPUT_DIR || path.join(ROOT, "_qualification/evidence/current_product_acceptance_16_cases", `run_${new Date().toISOString().replace(/[:.]/gu, "-")}`));
const PLAYWRIGHT_MODULE = process.env.MDI_PLAYWRIGHT_MODULE || path.join(ROOT, "apps/web/node_modules/playwright/index.mjs");
const CHROME = process.env.MDI_CHROMIUM_EXECUTABLE || "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const ACTION_TIMEOUT = Number(process.env.MDI_ACCEPTANCE_ACTION_TIMEOUT_MS || 120_000);
const JOB_TIMEOUT = Number(process.env.MDI_ACCEPTANCE_JOB_TIMEOUT_MS || 240_000);
const ONLY_CASE = process.argv.includes("--case") ? process.argv[process.argv.indexOf("--case") + 1] : null;

async function readJson(file) { return JSON.parse(await readFile(file, "utf8")); }
async function writeJson(relative, value) {
  const target = path.join(OUTPUT_ROOT, relative);
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}
function projectIdOf(value) { return value?.projectId || value?.id || null; }
function redact(value) {
  if (Array.isArray(value)) return value.map(redact);
  if (!value || typeof value !== "object") return value;
  const result = {};
  for (const [key, item] of Object.entries(value)) {
    if (/authorization|api.?key|secret|password|token/i.test(key)) continue;
    result[key] = redact(item);
  }
  return result;
}
async function api(relative, options = {}) {
  const response = await fetch(`${API_ORIGIN}${relative}`, {
    ...options,
    headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...(options.headers || {}) },
  });
  const text = await response.text();
  let body = null;
  if (text) { try { body = JSON.parse(text); } catch { body = text.slice(0, 2000); } }
  if (!response.ok) throw new Error(`API ${options.method || "GET"} ${relative} ${response.status}: ${JSON.stringify(redact(body))}`);
  return body;
}
async function loadCases() {
  const index = await readJson(path.join(PACKAGE_ROOT, "CASE_INDEX.json"));
  const entries = [...index.cases].sort((a, b) => a.order - b.order).filter((item) => !ONLY_CASE || item.caseId === ONLY_CASE);
  return Promise.all(entries.map(async (entry) => ({
    ...entry,
    directoryPath: path.join(PACKAGE_ROOT, entry.directory),
    contract: await readJson(path.join(PACKAGE_ROOT, entry.directory, "CASE.json")),
  })));
}
function responsePath(response) { try { return new URL(response.url()).pathname; } catch { return ""; } }
async function openPage(browser, audit) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  page.setDefaultTimeout(ACTION_TIMEOUT);
  page.on("console", (message) => { if (message.type() === "error") audit.consoleErrors.push(message.text().slice(0, 500)); });
  page.on("pageerror", (error) => audit.pageErrors.push(String(error).slice(0, 500)));
  page.on("response", (response) => { if (response.status() >= 400) audit.failedResponses.push({ status: response.status(), method: response.request().method(), path: responsePath(response) }); });
  return { context, page };
}
async function createProjectFromUi(page, name) {
  await page.goto(`${ORIGIN}/projects`, { waitUntil: "networkidle" });
  const createResponse = page.waitForResponse((response) => response.request().method() === "POST" && responsePath(response) === "/projects", { timeout: ACTION_TIMEOUT });
  await page.getByLabel("项目名称").fill(name);
  await page.getByRole("button", { name: "创建项目" }).click();
  const response = await createResponse;
  const body = await response.json();
  if (!response.ok()) throw new Error(`Project creation failed: ${JSON.stringify(redact(body))}`);
  const projectId = projectIdOf(body);
  if (!projectId) throw new Error("Project creation returned no project id");
  return projectId;
}
async function uploadFromUi(page, item, projectId, caseOut) {
  await page.goto(`${ORIGIN}/projects/${projectId}/datasets/new`, { waitUntil: "networkidle" });
  const files = item.contract.assets.map((asset) => path.join(item.directoryPath, asset.filename));
  if (!files.length || files.some((file) => !existsSync(file))) throw new Error(`Missing fixture asset for ${item.caseId}`);
  await page.getByLabel("数据集名称").fill(`${item.caseId} scientific data`);
  await page.getByLabel("源文件").setInputFiles(files);
  const completeResponse = page.waitForResponse((response) => response.request().method() === "POST" && /^\/upload-sessions\/[^/]+\/complete$/u.test(responsePath(response)), { timeout: ACTION_TIMEOUT });
  await page.getByRole("button", { name: "上传并解析" }).click();
  const response = await completeResponse;
  const body = await response.json();
  if (!response.ok()) throw new Error(`Upload failed: ${JSON.stringify(redact(body))}`);
  const history = await api(`/projects/${encodeURIComponent(projectId)}/history`);
  const dataset = history.datasets.at(-1);
  if (!dataset?.datasetId) throw new Error("Upload completed without a durable dataset");
  await writeJson(path.join(caseOut, "import.json"), { caseId: item.caseId, projectId, datasetId: dataset.datasetId, profileId: dataset.profile?.profileId || null, files: item.contract.assets.map((asset) => ({ filename: asset.filename, semanticKind: asset.semanticKind, role: asset.assetRole || asset.role })), response: redact(body) });
  return { datasetId: dataset.datasetId, profileId: dataset.profile?.profileId || "" };
}
async function pollJob(jobId, turnOut) {
  const started = Date.now();
  let firstArtifactBeforeTerminal = false;
  let snapshots = [];
  while (Date.now() - started < JOB_TIMEOUT) {
    const [job, events, artifacts] = await Promise.all([api(`/planner/jobs/${encodeURIComponent(jobId)}`), api(`/planner/jobs/${encodeURIComponent(jobId)}/events`), api(`/planner/jobs/${encodeURIComponent(jobId)}/artifacts`)]);
    snapshots.push({ at: new Date().toISOString(), status: job.status, eventCount: events.length, artifactCount: artifacts.length });
    if (!["completed", "partial_success", "failed", "cancelled"].includes(String(job.status).toLowerCase()) && artifacts.length) firstArtifactBeforeTerminal = true;
    if (["completed", "partial_success", "failed", "cancelled"].includes(String(job.status).toLowerCase())) {
      const [toolCalls, dependencies, result, interpretations] = await Promise.all([
        api(`/planner/jobs/${encodeURIComponent(jobId)}/tool-calls`),
        api(`/planner/jobs/${encodeURIComponent(jobId)}/dependencies`),
        api(`/planner/jobs/${encodeURIComponent(jobId)}/result`),
        api(`/planner/jobs/${encodeURIComponent(jobId)}/interpretations`),
      ]);
      await writeJson(path.join(turnOut, "runtime.json"), { job: redact(job), events: redact(events), toolCalls: redact(toolCalls), dependencies: redact(dependencies), artifacts: redact(artifacts), result: redact(result), interpretations: redact(interpretations), polling: snapshots, firstArtifactBeforeTerminal });
      return { job, events, artifacts, toolCalls, interpretations, firstArtifactBeforeTerminal };
    }
    await new Promise((resolve) => setTimeout(resolve, 1400));
  }
  throw new Error(`Job ${jobId} did not terminate within ${JOB_TIMEOUT}ms`);
}
async function submitTurn(page, item, projectId, dataset, turn, turnOut) {
  await page.goto(`${ORIGIN}/projects/${projectId}/research`, { waitUntil: "networkidle" });
  await page.getByLabel("询问此项目中的数据").fill(turn.question);
  const model = page.getByLabel("本次分析模型");
  if (await model.isVisible().catch(() => false)) await model.selectOption({ index: 0 });
  const jobResponse = page.waitForResponse((response) => response.request().method() === "POST" && responsePath(response) === "/planner/jobs", { timeout: ACTION_TIMEOUT }).catch(() => null);
  await page.getByRole("button", { name: "开始分析" }).click();
  const response = await jobResponse;
  if (!response) {
    const text = await page.locator("main").innerText();
    await page.screenshot({ path: path.join(OUTPUT_ROOT, turnOut, "browser-state.png"), fullPage: true });
    await writeJson(path.join(turnOut, "turn.json"), { caseId: item.caseId, turnId: turn.turnId, question: turn.question, state: text.includes("需要确认") ? "NEEDS_CLARIFICATION" : text.includes("无法进行") ? "UNSUPPORTED" : "NO_PLANNER_RESPONSE", datasetId: dataset.datasetId, browserText: text.slice(0, 4000) });
    return { status: "NO_JOB", jobId: null };
  }
  const body = await response.json();
  await writeJson(path.join(turnOut, "planner.json"), { response: redact(body), question: turn.question, datasetId: dataset.datasetId, profileId: dataset.profileId });
  if (!response.ok() || !body.ok || !body.job_id) {
    await page.screenshot({ path: path.join(OUTPUT_ROOT, turnOut, "browser-state.png"), fullPage: true });
    return { status: body.error_code || "PLANNER_FAILED", jobId: null };
  }
  const evidence = await pollJob(body.job_id, turnOut);
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(OUTPUT_ROOT, turnOut, "browser-complete.png"), fullPage: true });
  await writeJson(path.join(turnOut, "turn.json"), { caseId: item.caseId, turnId: turn.turnId, question: turn.question, datasetId: dataset.datasetId, profileId: dataset.profileId, jobId: body.job_id, status: evidence.job.status, toolCallCount: evidence.toolCalls.length, artifactCount: evidence.artifacts.length, interpretationCount: evidence.interpretations?.interpretations?.length || 0, firstArtifactBeforeTerminal: evidence.firstArtifactBeforeTerminal });
  return { status: String(evidence.job.status).toUpperCase(), jobId: body.job_id, artifactCount: evidence.artifacts.length };
}
async function runCase(browser, item, runSummary) {
  const caseOut = path.join("cases", item.caseId);
  await mkdir(path.join(OUTPUT_ROOT, caseOut), { recursive: true });
  const audit = { consoleErrors: [], pageErrors: [], failedResponses: [] };
  const { context, page } = await openPage(browser, audit);
  const caseResult = { caseId: item.caseId, order: item.order, caseType: item.contract.caseType, analysisExecutionExpected: item.contract.analysisExecutionExpected, status: "PROCESSING", turns: [], audit, preserved: true };
  await writeJson(path.join(caseOut, "CASE_RUN.json"), caseResult);
  try {
    const projectId = await createProjectFromUi(page, `Current acceptance ${item.caseId} ${Date.now()}`);
    caseResult.projectId = projectId;
    const dataset = await uploadFromUi(page, item, projectId, caseOut);
    caseResult.datasetId = dataset.datasetId;
    if (!item.contract.analysisExecutionExpected) {
      const rejectionTurn = item.contract.executionTurns?.[0] || { turnId: "expected-rejection", question: item.contract.canonicalQuestion };
      const turnOut = path.join(caseOut, "turns", rejectionTurn.turnId);
      await mkdir(path.join(OUTPUT_ROOT, turnOut), { recursive: true });
      const result = await submitTurn(page, item, projectId, dataset, rejectionTurn, turnOut);
      caseResult.turns.push(result);
    } else {
      for (const [index, turn] of (item.contract.executionTurns || []).entries()) {
        const turnOut = path.join(caseOut, "turns", `${String(index + 1).padStart(2, "0")}_${turn.turnId}`);
        await mkdir(path.join(OUTPUT_ROOT, turnOut), { recursive: true });
        caseResult.turns.push(await submitTurn(page, item, projectId, dataset, turn, turnOut));
        await writeJson(path.join(caseOut, "CASE_RUN.json"), caseResult);
      }
    }
    const turnStatuses = caseResult.turns.map((turn) => String(turn.status || "").toUpperCase());
    const expectedRejection = !item.contract.analysisExecutionExpected;
    const validExpectedRejection = expectedRejection && turnStatuses.some((status) => ["NO_JOB", "UNSUPPORTED", "INTENT_UNSUPPORTED", "PLANNER_FAILED"].includes(status));
    const validExecution = item.contract.analysisExecutionExpected && turnStatuses.length === (item.contract.executionTurns || []).length && turnStatuses.every((status) => ["COMPLETED", "PARTIAL_SUCCESS"].includes(status));
    caseResult.status = validExecution || validExpectedRejection ? "PASS_OR_RECORDED" : "FAILED_RECORDED";
    if (caseResult.status === "FAILED_RECORDED") {
      caseResult.error = `Expected execution did not complete for all turns: ${turnStatuses.join(", ")}`;
    }
  } catch (error) {
    caseResult.status = "FAILED_RECORDED";
    caseResult.error = String(error);
  } finally {
    await writeJson(path.join(caseOut, "CASE_RUN.json"), caseResult);
    await context.close();
  }
  runSummary.cases.push(caseResult);
}
const playwright = await import(pathToFileURL(PLAYWRIGHT_MODULE).href);
await mkdir(OUTPUT_ROOT, { recursive: true });
const cases = await loadCases();
const runSummary = { schemaVersion: "CurrentProductAcceptance16CaseRun/1.0", mode: "CURRENT_PRODUCT_ACCEPTANCE", authorityReadOnly: "Phase_BC_R1_7_Qualification_Authority", outputRoot: path.relative(ROOT, OUTPUT_ROOT).replaceAll("\\", "/"), origin: ORIGIN, apiOrigin: API_ORIGIN, caseCount: cases.length, startedAt: new Date().toISOString(), cases: [] };
await writeJson("RUN_MANIFEST.json", { ...runSummary, caseIds: cases.map((item) => item.caseId), fixtureRoot: path.relative(ROOT, PACKAGE_ROOT).replaceAll("\\", "/") });
const browser = await playwright.chromium.launch({ executablePath: CHROME, headless: true });
try { for (const item of cases) { await runCase(browser, item, runSummary); await writeJson("SUMMARY.json", { ...runSummary, updatedAt: new Date().toISOString() }); } }
finally { await browser.close(); }
runSummary.finishedAt = new Date().toISOString();
runSummary.status = runSummary.cases.every((item) => item.status === "PASS_OR_RECORDED") ? "COMPLETED_RECORDED" : "COMPLETED_WITH_RECORDED_FAILURES";
await writeJson("SUMMARY.json", runSummary);
console.log(JSON.stringify({ outputRoot: OUTPUT_ROOT, status: runSummary.status, cases: runSummary.cases.map((item) => ({ caseId: item.caseId, status: item.status, projectId: item.projectId, datasetId: item.datasetId, turns: item.turns.length })) }, null, 2));
