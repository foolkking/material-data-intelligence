import path from "node:path";
import { pathToFileURL } from "node:url";

const root = process.cwd();
const origin = process.env.MDI_ACCEPTANCE_ORIGIN || "http://127.0.0.1:3002";
const api = process.env.MDI_ACCEPTANCE_API || "http://127.0.0.1:8000";
const email = process.env.MDI_ACCEPTANCE_EMAIL;
const password = process.env.MDI_ACCEPTANCE_PASSWORD;
const executable = process.env.MDI_BROWSER_EXECUTABLE;
const project = process.env.MDI_ACCEPTANCE_PROJECT || "agent2-phase4-project-ca096d85f356";
const objectId = process.env.MDI_ACCEPTANCE_OBJECT_ID || "773089f9-3ce8-4645-92dd-2f62c64cba89";
const versionId = process.env.MDI_ACCEPTANCE_VERSION_ID || "65f56d10-008d-445d-ab2f-228aebf1835b";
const objectType = process.env.MDI_ACCEPTANCE_OBJECT_TYPE || "structure.crystal";
const objectName = process.env.MDI_ACCEPTANCE_OBJECT_NAME || "Phase10 Fe3O4";
const prompt = process.env.MDI_ACCEPTANCE_PROMPT || "请分别使用 CrystalNN 和 VoronoiNN 两种独立的局部配位算法分析这个结构，并比较它们的结果。";
const playwrightModule = process.env.MDI_PLAYWRIGHT_MODULE || path.join(root, "apps/web/node_modules/playwright/index.mjs");
if (!email || !password || !executable) throw new Error("acceptance credentials and browser executable are required");

const pw = await import(pathToFileURL(playwrightModule).href);
const browser = await pw.chromium.launch({ headless: true, executablePath: executable, args: ["--no-sandbox"] });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
const page = await context.newPage();
const fatalErrors = [];
const consoleErrors = [];
const failedRequests = [];
const expectedOptionalRequests = [];
page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text().slice(0, 300)); });
page.on("pageerror", (error) => fatalErrors.push(String(error).slice(0, 300)));
page.on("response", (response) => {
  const pathname = new URL(response.url()).pathname;
  if (response.status() >= 400 && !pathname.endsWith("/favicon.ico")) {
    if (response.status() === 404 && pathname.endsWith("/report")) {
      expectedOptionalRequests.push({ status: response.status(), pathname });
    } else {
      failedRequests.push({ status: response.status(), pathname });
    }
  }
});

await page.goto(origin, { waitUntil: "networkidle" });
const login = page.getByRole("button", { name: "登录", exact: true });
if (await login.count()) {
  await login.click();
  await page.getByLabel("邮箱", { exact: true }).fill(email);
  await page.getByLabel("密码", { exact: true }).fill(password);
  const loginResponse = page.waitForResponse((response) => new URL(response.url()).pathname.endsWith("/auth/login"));
  await page.getByRole("dialog").getByRole("button", { name: "登录", exact: true }).click();
  const response = await loginResponse;
  if (!response.ok()) throw new Error(`login failed: ${response.status()}`);
}
fatalErrors.length = 0;
consoleErrors.length = 0;
failedRequests.length = 0;
expectedOptionalRequests.length = 0;

const turnResponse = page.waitForResponse((response) => {
  const pathname = new URL(response.url()).pathname;
  return response.request().method() === "POST" && pathname.includes("/research/sessions/") && pathname.endsWith("/turns");
});
const researchUrl = `${origin}/projects/${project}/research?object=${objectId}&version=${versionId}&type=${encodeURIComponent(objectType)}&name=${encodeURIComponent(objectName)}`;
const sessionResponse = await page.request.post(`${api}/projects/${encodeURIComponent(project)}/research-sessions`, {
  data: { title: `Phase 10 browser ${objectName}` },
});
if (!sessionResponse.ok()) throw new Error(`session creation failed: ${sessionResponse.status()}`);
const sessionPayload = await sessionResponse.json();
const sessionId = String(sessionPayload.id || sessionPayload.session_id || "");
if (!sessionId) throw new Error(`missing session id: ${JSON.stringify(sessionPayload)}`);
await page.goto(`${origin}/projects/${project}/research/${encodeURIComponent(sessionId)}?object=${encodeURIComponent(objectId)}&version=${encodeURIComponent(versionId)}&type=${encodeURIComponent(objectType)}&name=${encodeURIComponent(objectName)}`, { waitUntil: "networkidle" });
const question = page.getByLabel("询问此项目中的数据");
await question.fill(prompt);
await page.getByRole("button", { name: "开始分析", exact: true }).click();
const created = await turnResponse;
const turnPayload = await created.json();
const turnId = String(turnPayload.turn_id || turnPayload.turnId || "");
if (!turnId) throw new Error(`missing turn id: ${JSON.stringify(turnPayload)}`);
let dispatchResponse = null;
for (let attempt = 0; attempt < 90; attempt += 1) {
  const stateResponse = await page.request.get(`${api}/api/research/turns/${encodeURIComponent(turnId)}`);
  const state = stateResponse.ok() ? await stateResponse.json() : {};
  const status = String(state.status || "");
  if (["PLAN_READY", "QUEUED", "RUNNING", "RESULT_PENDING", "RESULT_READY", "COMPLETED", "PARTIAL", "FAILED", "CANCELED", "UNSUPPORTED", "PLAN_REJECTED"].includes(status)) {
    if (status === "PLAN_READY") {
      dispatchResponse = await page.request.post(`${api}/api/research/turns/${encodeURIComponent(turnId)}/dispatch`);
      if (!dispatchResponse.ok() && dispatchResponse.status() !== 409) throw new Error(`dispatch failed: ${dispatchResponse.status()}`);
    }
    break;
  }
  await page.waitForTimeout(1000);
}

const deadline = Date.now() + 180_000;
let terminal = null;
while (Date.now() < deadline) {
  const response = await page.request.get(`${api}/api/research/turns/${encodeURIComponent(turnId)}`);
  if (response.ok()) {
    const value = await response.json();
    const status = String(value.status || "");
    if (["COMPLETED", "PARTIAL", "FAILED", "CANCELED", "UNSUPPORTED", "PLAN_REJECTED"].includes(status)) {
      terminal = value;
      break;
    }
  }
  await page.waitForTimeout(2000);
}
const progressPayload = terminal
  ? { status: String(terminal.status), terminal: true }
  : await (async () => {
      const progress = await page.request.get(`${api}/api/research/turns/${encodeURIComponent(turnId)}/progress`);
      return progress.ok() ? progress.json() : { status: progress.status() };
    })();
console.log(JSON.stringify({
  schema: "phase10.stage0.browser_dispatch_smoke.v1",
  turnId,
  created: turnPayload,
  terminal,
  progress: progressPayload,
  fatalErrors,
  consoleErrors,
  failedRequests,
  expectedOptionalRequests,
  pass: Boolean(terminal && ["COMPLETED", "PARTIAL"].includes(String(terminal.status)) && fatalErrors.length === 0 && failedRequests.length === 0),
}, null, 2));
await context.close();
await browser.close();
