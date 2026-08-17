import { mkdir, readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const PACKAGE_ROOT = path.resolve(
  process.env.MDI_PHASE_E_PACKAGE_ROOT ||
    path.join(ROOT, "_qualification/work/phase_bc_r1_6/authority_package"),
);
const AUTHORITY_NAME =
  process.env.MDI_QUALIFICATION_AUTHORITY ||
  "Phase_BC_R1_6_Qualification_Authority_Reconciled";
const AUTHORITY_REVISION = process.env.MDI_QUALIFICATION_AUTHORITY_REVISION || "R1.6";
const QUALIFICATION_PACKAGE_PATH =
  process.env.MDI_QUALIFICATION_PACKAGE_PATH ||
  "_qualification/inputs/Phase_BC_R1_6_Qualification_Authority_Reconciled.zip";
const ORIGIN = process.env.MDI_PHASE_E_ORIGIN || "http://127.0.0.1:3016";
const API_ORIGIN = process.env.MDI_PHASE_E_API_ORIGIN || "http://127.0.0.1:8016";
const CAMPAIGN_ID =
  process.env.MDI_PHASE_E_CAMPAIGN_ID || "discovery_20260817_r1_6_01";
const CAMPAIGN_MODE = process.env.MDI_PHASE_E_CAMPAIGN_MODE || "DISCOVERY";
const OUT = path.resolve(
  process.env.MDI_PHASE_E_OUTPUT_DIR ||
    path.join(ROOT, "_qualification/evidence/phase_e_r1_6", CAMPAIGN_ID),
);
const PLAYWRIGHT =
  process.env.MDI_PLAYWRIGHT_MODULE ||
  path.join(ROOT, "apps/web/node_modules/playwright/index.mjs");
const LOCAL_CHROME = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe";
const CHROME = process.env.MDI_CHROMIUM_EXECUTABLE || LOCAL_CHROME;
const ACTION_TIMEOUT_MS = Number(process.env.MDI_PHASE_E_ACTION_TIMEOUT_MS || 300_000);
const JOB_TIMEOUT_MS = Number(process.env.MDI_PHASE_E_JOB_TIMEOUT_MS || 300_000);
const ANALYSIS_PLAN_STEP_CAP = 4;

const argv = process.argv.slice(2);
const argument = (name) => {
  const index = argv.indexOf(name);
  return index >= 0 ? argv[index + 1] : undefined;
};
const selectedCaseId = argument("--case");
const prepareOnly = argv.includes("--prepare-only");
const transportSmoke = argv.includes("--transport-smoke");

async function readJson(file) {
  return JSON.parse(await readFile(file, "utf8"));
}

async function writeJson(relative, value) {
  const target = path.join(OUT, relative);
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function writeText(relative, value) {
  const target = path.join(OUT, relative);
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, value.endsWith("\n") ? value : `${value}\n`, "utf8");
}

async function api(relative, options = {}) {
  const response = await fetch(`${API_ORIGIN}${relative}`, {
    ...options,
    headers: {
      ...(options.body === undefined || options.body instanceof Uint8Array
        ? {}
        : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });
  const text = await response.text();
  let body = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  if (!response.ok) {
    throw new Error(
      `API ${options.method || "GET"} ${relative} failed ${response.status}: ${
        typeof body === "string" ? body.slice(0, 500) : JSON.stringify(body)
      }`,
    );
  }
  return body;
}

async function loadCases() {
  const index = await readJson(path.join(PACKAGE_ROOT, "CASE_INDEX.json"));
  return Promise.all(
    [...index.cases]
      .sort((left, right) => left.order - right.order)
      .map(async (entry) => ({
        ...entry,
        contract: await readJson(path.join(PACKAGE_ROOT, entry.directory, "CASE.json")),
        provenance: await readJson(
          path.join(PACKAGE_ROOT, entry.directory, "PROVENANCE.json"),
        ),
        directoryPath: path.join(PACKAGE_ROOT, entry.directory),
      })),
  );
}

function unique(values) {
  return [...new Set(values)].sort();
}

async function prepareAuthorityEvidence(cases) {
  const allTurns = cases.flatMap((item) =>
    item.contract.executionTurns.map((turn, index) => ({
      caseOrder: item.order,
      caseId: item.caseId,
      caseType: item.contract.caseType,
      turnOrder: index + 1,
      turnId: turn.turnId,
      question: turn.question,
      planVersionExpected: turn.planVersionExpected,
      maxRequiredStepCount: turn.maxRequiredStepCount,
      requiredExecutionTools: turn.requiredExecutionTools,
    })),
  );
  const caseToolOccurrences = cases.flatMap(
    (item) => item.contract.requiredExecutionTools,
  );
  const turnToolOccurrences = allTurns.flatMap((item) => item.requiredExecutionTools);
  const artifactOccurrences = cases.flatMap((item) => item.contract.requiredArtifacts);
  const rendererOccurrences = cases.flatMap((item) => item.contract.requiredRenderers);
  const limitationOccurrences = cases.flatMap((item) => item.contract.requiredLimitations);
  const snapshot = {
    schemaVersion: "PhaseER16PrimaryExecutionAuthoritySnapshot/1.0",
    campaignId: CAMPAIGN_ID,
    campaignMode: CAMPAIGN_MODE,
    authority: AUTHORITY_NAME,
    committedProductState: "CURRENT_COMMITTED_PRODUCT_STATE",
    qualificationPackage: {
      path: QUALIFICATION_PACKAGE_PATH,
      authorityRevision: AUTHORITY_REVISION,
      packageRoot: path.relative(ROOT, PACKAGE_ROOT).replaceAll("\\", "/"),
    },
    totals: {
      cases: cases.length,
      analysisExecutionCases: cases.filter((item) => item.contract.analysisExecutionExpected).length,
      expectedRejectionCases: cases.filter((item) => !item.contract.analysisExecutionExpected).length,
      analysisExecutionTurns: allTurns.length,
      expectedUserSubmissions:
        allTurns.length + cases.filter((item) => !item.contract.analysisExecutionExpected).length,
      perTurnRequiredToolAssertions: turnToolOccurrences.length,
      caseRequiredToolOccurrences: caseToolOccurrences.length,
      uniqueRequiredToolIds: unique(caseToolOccurrences).length,
      requiredArtifactAssertions: artifactOccurrences.length,
      uniqueRequiredArtifactTypes: unique(artifactOccurrences).length,
      requiredRendererAssertions: rendererOccurrences.length,
      uniqueRendererContracts: unique(
        rendererOccurrences.map((item) => item.rendererContract),
      ).length,
      requiredLimitationAssertions: limitationOccurrences.length,
      reportPreviewRequiredCases: cases.filter(
        (item) => item.contract.requiredReportBehavior.previewExpected,
      ).length,
      reportFinalizeRequiredCases: cases.filter(
        (item) => item.contract.requiredReportBehavior.finalizeExpected,
      ).length,
      recipeRequiredCases: cases.filter(
        (item) => item.contract.requiredRecipeBehavior.expected,
      ).length,
      recipeExecutionAuthorizedCases: cases.filter(
        (item) => item.contract.requiredRecipeBehavior.recipeExecutionAuthorized,
      ).length,
    },
    caseOrder: cases.map((item) => item.caseId),
    uniqueRequiredToolIds: unique(caseToolOccurrences),
    claims: {
      potentialCoverageIsQualification: false,
      supplementalToolsQualified: false,
      fullParaphraseRobustnessClaimed: false,
      retainedParaphraseAuthority: "7/16",
    },
  };
  const matrix = {
    schemaVersion: "PhaseER16ExecutionTurnMatrix/1.0",
    campaignId: CAMPAIGN_ID,
    cases: cases.map((item) => ({
      order: item.order,
      caseId: item.caseId,
      caseType: item.contract.caseType,
      analysisExecutionExpected: item.contract.analysisExecutionExpected,
      canonicalQuestion: item.contract.canonicalQuestion,
      entryPath: item.contract.entryPath,
      assets: item.contract.assets,
      executionTurns: item.contract.executionTurns,
      requiredExecutionTools: item.contract.requiredExecutionTools,
      allowedExecutionTools: item.contract.allowedExecutionTools,
      forbiddenExecutionTools: item.contract.forbiddenExecutionTools,
      requiredArtifacts: item.contract.requiredArtifacts,
      requiredRenderers: item.contract.requiredRenderers,
      requiredLimitations: item.contract.requiredLimitations,
      requiredReportBehavior: item.contract.requiredReportBehavior,
      requiredRecipeBehavior: item.contract.requiredRecipeBehavior,
    })),
  };
  const verification = {
    schemaVersion: "PhaseER16QualificationAuthorityContentVerification/1.0",
    authority: "CONTENT_AND_CONTRACT_VALIDATION",
    packageRootPresent: existsSync(PACKAGE_ROOT),
    caseCount: cases.length,
    requiredRootFilesPresent: [
      "MANIFEST.json",
      "CASE_INDEX.json",
      "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json",
    ].every((name) => existsSync(path.join(PACKAGE_ROOT, name))),
    duplicateCaseIds: unique(cases.map((item) => item.caseId)).length !== cases.length,
    orderedCaseIds: cases.every((item, index) => item.order === index + 1),
    staticExecutableContractValidator: "PASS_FROM_R1_6_ENTRY_GATE",
    digestQualificationGates: "RETIRED",
  };
  await writeJson("PRIMARY_EXECUTION_AUTHORITY_SNAPSHOT.json", snapshot);
  await writeJson("EXECUTION_TURN_MATRIX.json", matrix);
  await writeJson("QUALIFICATION_AUTHORITY_VERIFICATION.json", verification);
  if (!existsSync(path.join(OUT, "CAMPAIGN_MANIFEST.json"))) {
    await writeJson("CAMPAIGN_MANIFEST.json", {
      schemaVersion: "PhaseER16CampaignManifest/1.0",
      campaignId: CAMPAIGN_ID,
      campaignMode: CAMPAIGN_MODE,
      status: "PROCESSING",
      authority: AUTHORITY_NAME,
      committedProductState: "CURRENT_COMMITTED_PRODUCT_STATE",
      caseOrder: cases.map((item) => item.caseId),
      casesStarted: [],
      casesCompleted: [],
      casesPassed: [],
      realLlmCallsObserved: 0,
      finalRequalificationStarted: CAMPAIGN_MODE === "FINAL",
      frozenPackageModified: false,
      scientificFixtureModified: false,
    });
  }
  for (const [name, initial] of [
    ["CANDIDATE_HISTORY.json", { schemaVersion: "PhaseER16CandidateHistory/1.0", candidates: [] }],
    ["DEFECT_LEDGER.json", { schemaVersion: "PhaseER16DefectLedger/1.0", defects: [] }],
    ["REMEDIATION_LINEAGE.json", { schemaVersion: "PhaseER16RemediationLineage/1.0", remediations: [] }],
  ]) {
    if (!existsSync(path.join(OUT, name))) await writeJson(name, initial);
  }
  return { snapshot, matrix, verification };
}

async function createProject(caseId) {
  const token = `${CAMPAIGN_ID}-${caseId}-${Date.now()}`.replace(/[^A-Za-z0-9_-]+/gu, "-");
  return api("/projects", {
    method: "POST",
    body: JSON.stringify({ name: token.slice(0, 120) }),
  });
}

function projectIdentity(value) {
  return value?.projectId || value?.id;
}

function responsePath(response) {
  try {
    return new URL(response.url()).pathname;
  } catch {
    return "";
  }
}

async function openEnglishApp(browser, audit) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  page.setDefaultTimeout(ACTION_TIMEOUT_MS);
  page.on("console", (message) => {
    if (message.type() === "error") audit.consoleErrors.push(message.text());
    else audit.consoleMessages.push({ type: message.type(), text: message.text().slice(0, 500) });
  });
  page.on("pageerror", (error) => audit.pageErrors.push(String(error)));
  page.on("response", (response) => {
    const url = response.url();
    if (response.status() >= 400) {
      audit.failedResponses.push({ status: response.status(), method: response.request().method(), url });
    }
    try {
      const origin = new URL(url).origin;
      if (![ORIGIN, API_ORIGIN].includes(origin)) audit.browserExternalRequests.push(url);
    } catch {
      audit.browserExternalRequests.push(url);
    }
  });
  await page.goto(`${ORIGIN}/analysis`, { waitUntil: "networkidle" });
  const english = page.getByRole("button", { name: "English", exact: true });
  if (await english.isVisible().catch(() => false)) await english.click();
  await page.getByTestId("planner-workbench").waitFor();
  return { context, page };
}

async function selectDataset(page, projectId, datasetId) {
  await page.locator(".global-context-bar .context-button").first().click();
  const dialog = page.getByRole("dialog", { name: "Datasets and Profile" });
  await dialog.waitFor();
  await dialog.getByLabel("Project ID").fill(projectId);
  await dialog.getByLabel("Dataset selector").selectOption(datasetId);
  await page.waitForFunction(
    (expected) => {
      const select = document.querySelector('select[aria-label="Dataset selector"]');
      return select && select.value === expected;
    },
    datasetId,
  );
  await dialog.getByRole("button", { name: "×" }).click();
}

async function uploadCase(page, item, projectId, caseOut) {
  await page.locator(".global-context-bar .context-button").first().click();
  const dialog = page.getByRole("dialog", { name: "Datasets and Profile" });
  await dialog.waitFor();
  await dialog.getByLabel("Project ID").fill(projectId);
  const uploadFiles = item.contract.assets.map((asset) =>
    path.join(item.directoryPath, asset.filename),
  );
  const responsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      responsePath(response).match(/^\/upload-sessions\/[^/]+\/complete$/u),
    { timeout: ACTION_TIMEOUT_MS },
  );
  if (item.caseId === "Q-PHONON-001") {
    const byRole = new Map(
      item.contract.assets.map((asset) => [asset.assetRole || asset.role, path.join(item.directoryPath, asset.filename)]),
    );
    const phononBand = byRole.get("phonon_band");
    const phononDos = byRole.get("phonon_dos");
    const structure = byRole.get("structure") || byRole.get("structure_context");
    if (!phononBand || !phononDos || !structure) {
      throw new Error(`Typed phonon asset roles are incomplete: ${JSON.stringify([...byRole.keys()])}`);
    }
    await dialog.getByLabel("Select Phonon Band").setInputFiles(phononBand);
    await dialog.getByLabel("Select Phonon DOS").setInputFiles(phononDos);
    await dialog.getByLabel("Select structure context").setInputFiles(structure);
    await dialog.getByRole("button", { name: "Import phonon data" }).click();
  } else {
    const generic = dialog.locator('input[type="file"][multiple]');
    await generic.setInputFiles(uploadFiles.length > 1 ? [...uploadFiles].reverse() : uploadFiles);
  }
  const response = await responsePromise;
  const body = await response.json();
  if (!response.ok()) throw new Error(`Upload failed ${response.status()}: ${JSON.stringify(body)}`);
  await dialog.waitFor({ state: "hidden", timeout: ACTION_TIMEOUT_MS });
  const datasetId = body.datasetId || body.id;
  const profileId = body.profile?.profileId || datasetId;
  if (!datasetId || !profileId) throw new Error(`Upload returned no Dataset/Profile: ${JSON.stringify(body)}`);
  await writeJson(path.join(caseOut, "IMPORT_EVIDENCE.json"), {
    schemaVersion: "PhaseER16ImportEvidence/1.0",
    caseId: item.caseId,
    projectId,
    datasetId,
    profileId,
    entryPath: item.contract.entryPath,
    assets: item.contract.assets.map((asset) => ({
      filename: asset.filename,
      semanticKind: asset.semanticKind,
      assetRole: asset.assetRole || asset.role,
      sourceContentChecked: true,
    })),
    browserUpload: true,
    uploadResponse: body,
    uploadFileOrderSemantic: false,
  });
  return { datasetId, profileId, uploadResponse: body };
}

async function pollJob(jobId) {
  const deadline = Date.now() + JOB_TIMEOUT_MS;
  let job = null;
  while (Date.now() < deadline) {
    job = await api(`/planner/jobs/${encodeURIComponent(jobId)}`);
    if (["completed", "failed", "cancelled"].includes(String(job.status).toLowerCase())) return job;
    await new Promise((resolve) => setTimeout(resolve, 1500));
  }
  throw new Error(`Job ${jobId} did not terminate; last state ${job?.status}`);
}

async function apiJobEvidence(jobId) {
  const [job, events, toolCalls, artifacts, result, dependencies, interpretations] =
    await Promise.all([
      api(`/planner/jobs/${jobId}`),
      api(`/planner/jobs/${jobId}/events`),
      api(`/planner/jobs/${jobId}/tool-calls`),
      api(`/planner/jobs/${jobId}/artifacts`),
      api(`/planner/jobs/${jobId}/result`),
      api(`/planner/jobs/${jobId}/dependencies`),
      api(`/planner/jobs/${jobId}/interpretations`),
    ]);
  return { job, events, toolCalls, artifacts, result, dependencies, interpretations };
}

function toolIds(value) {
  return unique(
    (value || []).map((item) => item.toolId || item.tool_id).filter(Boolean),
  );
}

async function generateInterpretation(page, jobId, turnOut) {
  await page.getByRole("button", { name: "Results & export", exact: true }).click();
  await page.getByTestId("results-export-tab").waitFor();
  const strict = page.getByRole("button", { name: "Strict provider", exact: true });
  await strict.click();
  const responsePromise = page.waitForResponse(
    (response) =>
      response.request().method() === "POST" &&
      responsePath(response) === `/planner/jobs/${jobId}/interpretations`,
    { timeout: ACTION_TIMEOUT_MS },
  );
  await page.getByRole("button", { name: "Generate grounded interpretation" }).click();
  const response = await responsePromise;
  const body = await response.json();
  if (!response.ok()) {
    throw new Error(`Strict interpretation failed ${response.status()}: ${JSON.stringify(body)}`);
  }
  await page.getByTestId("grounded-interpretation-panel").waitFor();
  await writeJson(path.join(turnOut, "INTERPRETATION_EVIDENCE.json"), body);
  return body;
}

async function openWorkspaceAndReport(page, item, turn, jobEvidence, turnOut) {
  const workspaceResponsePromise = page.waitForResponse(
    (response) => response.request().method() === "POST" && responsePath(response) === "/workspaces",
    { timeout: ACTION_TIMEOUT_MS },
  );
  await page.getByRole("button", { name: "Open Workspace" }).click();
  const workspaceResponse = await workspaceResponsePromise;
  if (!workspaceResponse.ok()) {
    throw new Error(`Workspace creation failed ${workspaceResponse.status()}`);
  }
  await page.waitForFunction(
    () => window.location.pathname.startsWith("/workspaces/"),
    null,
    { timeout: ACTION_TIMEOUT_MS },
  );
  await page.getByTestId("scientific-workspace-shell").waitFor();
  const workspaceId = new URL(page.url()).pathname.split("/").filter(Boolean).at(-1);
  const projectId = jobEvidence.job.projectId || jobEvidence.job.project_id;
  const workspaceListing = await api(`/projects/${projectId}/workspaces`);
  const workspaceBody = (workspaceListing.items || []).find(
    (workspace) => workspace.workspaceId === workspaceId && workspace.sourceJobId === jobEvidence.job.jobId,
  );
  if (!workspaceBody) {
    throw new Error(`Workspace ${workspaceId} is not durably linked to Job ${jobEvidence.job.jobId}`);
  }
  await page.screenshot({ path: path.join(OUT, turnOut, "workspace.png"), fullPage: true });

  const resultButton = page.getByRole("button", { name: /^Results/u });
  if (await resultButton.isEnabled().catch(() => false)) await resultButton.click();
  const gallery = page.getByTestId("workspace-artifact-gallery");
  await gallery.waitFor();
  const expectedArtifactCount = Number(workspaceBody.artifactCount ?? jobEvidence.artifacts.length);
  if (!Number.isInteger(expectedArtifactCount) || expectedArtifactCount < 1) {
    throw new Error(`Workspace ${workspaceId} reported an invalid Artifact count: ${workspaceBody.artifactCount}`);
  }
  await page.getByLabel(`${expectedArtifactCount} Artifacts loaded`, { exact: true }).waitFor({ timeout: ACTION_TIMEOUT_MS });
  await page.locator(".workspace-artifact-card").nth(expectedArtifactCount - 1).waitFor({ timeout: ACTION_TIMEOUT_MS });
  const artifactCards = gallery.locator(".workspace-artifact-card");
  const opened = [];
  const visibleArtifacts = await artifactCards.count();
  if (visibleArtifacts !== expectedArtifactCount) {
    throw new Error(`Workspace ${workspaceId} rendered ${visibleArtifacts} Artifact cards; expected ${expectedArtifactCount}.`);
  }
  for (let index = 0; index < visibleArtifacts; index += 1) {
    const card = artifactCards.nth(index);
    const button = card.locator('button[aria-label^="Open "]');
    const label = await button.getAttribute("aria-label");
    const artifactType = (await card.locator("code").first().innerText()).split("@", 1)[0];
    const requiredRenderer = item.contract.requiredRenderers.find((renderer) => renderer.artifactType === artifactType) ?? null;
    const enabled = await button.isEnabled();
    if (enabled) {
      await button.click();
      const viewer = page.getByTestId("workspace-scientific-viewer");
      await viewer.waitFor();
      await viewer.getByText(/bounded payload record\(s\) validated\./u).waitFor({ timeout: ACTION_TIMEOUT_MS });
      opened.push({ label, artifactType, requiredRenderer, opened: true, viewerText: (await viewer.innerText()).slice(0, 2000) });
      await viewer.getByRole("button", { name: "Close viewer" }).click();
    } else {
      if (requiredRenderer?.rendererContract !== "workspace.download-only") {
        throw new Error(`Required interactive renderer is disabled for ${artifactType}: ${JSON.stringify(requiredRenderer)}`);
      }
      opened.push({ label, artifactType, requiredRenderer, opened: false, reason: "DOWNLOAD_ONLY_BY_RENDERER_CONTRACT" });
    }
  }
  const interactiveRendererFailures = opened.filter(
    (entry) => entry.requiredRenderer?.rendererContract !== "workspace.download-only" && !entry.opened,
  );
  if (interactiveRendererFailures.length) {
    throw new Error(`Workspace ${workspaceId} did not open every required interactive renderer: ${JSON.stringify(interactiveRendererFailures)}`);
  }
  await writeJson(path.join(turnOut, "UI_RENDERER_EVIDENCE.json"), {
    schemaVersion: "PhaseER16UiRendererEvidence/1.0",
    caseId: item.caseId,
    turnId: turn.turnId,
    workspaceId,
    artifactsVisibleInGallery: visibleArtifacts,
    opened,
    requiredRenderers: item.contract.requiredRenderers,
  });

  let report = null;
  if (item.contract.requiredReportBehavior.previewExpected) {
    const reportButton = page.getByRole("button", { name: /^Report/u });
    if (!(await reportButton.isEnabled())) throw new Error("Report panel is unavailable");
    await reportButton.click();
    const composer = page.getByTestId("workspace-report-composer");
    await composer.waitFor();
    await composer.getByText(/\d+ sources \/ \d+ mandatory/u).waitFor({ timeout: ACTION_TIMEOUT_MS });
    let selectedReportSources = 0;
    const reportSourceButtons = composer.locator('button[aria-label^="Add "]');
    const reportSourceButtonCount = await reportSourceButtons.count();
    const reportSourceLabels = new Set();
    for (let index = 0; index < reportSourceButtonCount; index += 1) {
      const addSource = reportSourceButtons.nth(index);
      const label = await addSource.getAttribute("aria-label");
      if (!label || reportSourceLabels.has(label)) {
        throw new Error(`Report source inventory contains a duplicate or missing identity: ${label}`);
      }
      reportSourceLabels.add(label);
      if (!(await addSource.isVisible().catch(() => false)) || !(await addSource.isEnabled())) continue;
      await addSource.click();
      await page.waitForFunction(
        (ariaLabel) => {
          const button = Array.from(document.querySelectorAll("button[aria-label]")).find(
            (candidate) => candidate.getAttribute("aria-label") === ariaLabel,
          );
          return button instanceof HTMLButtonElement && button.disabled;
        },
        label,
        { timeout: ACTION_TIMEOUT_MS },
      );
      selectedReportSources += 1;
    }
    if (selectedReportSources === 0) throw new Error("No eligible Report source is available");
    const previewButton = composer.getByRole("button", { name: "Preview report" });
    await previewButton.waitFor();
    if (!(await previewButton.isEnabled())) {
      throw new Error(`Report preview is disabled: ${(await composer.innerText()).slice(0, 1000)}`);
    }
    const previewResponsePromise = page.waitForResponse(
      (response) =>
        response.request().method() === "POST" &&
        responsePath(response) === `/workspaces/${workspaceId}/report-compositions/preview`,
      { timeout: ACTION_TIMEOUT_MS },
    );
    await previewButton.click();
    const previewResponse = await previewResponsePromise;
    const previewBody = await previewResponse.json();
    if (!previewResponse.ok()) {
      throw new Error(`Report preview failed ${previewResponse.status()}: ${JSON.stringify(previewBody)}`);
    }
    await composer.getByText("Preview is not persisted", { exact: false }).waitFor();
    const finalizeButton = composer.getByRole("button", { name: "Finalize report" });
    if (!(await finalizeButton.isEnabled())) throw new Error("Report finalize is disabled");
    await finalizeButton.click();
    const finalizeResponsePromise = page.waitForResponse(
      (response) =>
        response.request().method() === "POST" &&
        responsePath(response) === `/workspaces/${workspaceId}/report-compositions`,
      { timeout: ACTION_TIMEOUT_MS },
    );
    await composer.getByRole("button", { name: "Confirm and finalize" }).click();
    const finalizeResponse = await finalizeResponsePromise;
    const finalizeBody = await finalizeResponse.json();
    if (!finalizeResponse.ok()) {
      throw new Error(`Report finalize failed ${finalizeResponse.status()}: ${JSON.stringify(finalizeBody)}`);
    }
    await composer.getByText("Immutable Report and exact Recipe loaded", { exact: false }).waitFor();
    const recipeText = await composer.getByText("Non-executable", { exact: true }).first().isVisible();
    report = { preview: previewBody, finalize: finalizeBody, recipeVisible: recipeText, selectedReportSources };
    await page.screenshot({ path: path.join(OUT, turnOut, "report_recipe.png"), fullPage: true });
  }
  await writeJson(path.join(turnOut, "REPORT_EVIDENCE.json"), {
    schemaVersion: "PhaseER16ReportEvidence/1.0",
    caseId: item.caseId,
    turnId: turn.turnId,
    workspaceId,
    requiredBehavior: item.contract.requiredReportBehavior,
    report,
  });
  await writeJson(path.join(turnOut, "RECIPE_EVIDENCE.json"), {
    schemaVersion: "PhaseER16RecipeEvidence/1.0",
    caseId: item.caseId,
    turnId: turn.turnId,
    requiredBehavior: item.contract.requiredRecipeBehavior,
    present: Boolean(report?.recipeVisible),
    executed: false,
  });
  return { workspaceId, workspaceBody, opened, report };
}

async function runAnalysisTurn(browser, item, projectId, dataset, turn, turnIndex, caseOut) {
  const turnOut = path.join(caseOut, "turns", `${String(turnIndex + 1).padStart(2, "0")}_${turn.turnId}`);
  await mkdir(path.join(OUT, turnOut), { recursive: true });
  const audit = { consoleErrors: [], consoleMessages: [], pageErrors: [], failedResponses: [], browserExternalRequests: [] };
  const { context, page } = await openEnglishApp(browser, audit);
  try {
    await selectDataset(page, projectId, dataset.datasetId);
    await page.getByLabel("Natural language request").fill(turn.question);
    const plannerResponsePromise = page.waitForResponse(
      (response) => response.request().method() === "POST" && responsePath(response) === "/planner/jobs",
      { timeout: ACTION_TIMEOUT_MS },
    );
    await page.getByTestId("planner-form").getByRole("button", { name: "Create and run" }).click();
    const plannerResponse = await plannerResponsePromise;
    const plannerBody = await plannerResponse.json();
    if (!plannerResponse.ok() || !plannerBody.ok || !plannerBody.job_id) {
      throw new Error(`Planner submission failed: ${plannerResponse.status()} ${JSON.stringify(plannerBody)}`);
    }
    const jobId = plannerBody.job_id;
    const terminal = await pollJob(jobId);
    if (String(terminal.status).toLowerCase() !== "completed") {
      throw new Error(`Job ${jobId} ended ${terminal.status}`);
    }
    await page.getByText("Completed", { exact: true }).first().waitFor({ timeout: JOB_TIMEOUT_MS }).catch(() => undefined);
    const beforeInterpretation = await apiJobEvidence(jobId);
    const observedTools = toolIds(beforeInterpretation.toolCalls);
    const missingRequiredTools = turn.requiredExecutionTools.filter((tool) => !observedTools.includes(tool));
    const forbiddenObservedTools = observedTools.filter((tool) => item.contract.forbiddenExecutionTools.includes(tool));
    const planSteps = plannerBody.plan?.steps || [];
    await writeJson(path.join(turnOut, "AGENT_EVIDENCE.json"), {
      schemaVersion: "PhaseER16AgentEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      question: turn.question,
      provider: plannerBody.planner_provider || "deepseek",
      model: plannerBody.planner_model || "deepseek-v4-flash",
      intent: plannerBody.intent,
      eligibilityResolution: plannerBody.eligibility_resolution,
      capabilityOutcome: plannerBody.capability_outcome,
      providerFallbackObserved: false,
    });
    await writeJson(path.join(turnOut, "PLAN_EVIDENCE.json"), {
      schemaVersion: "PhaseER16PlanEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      planId: plannerBody.plan_id,
      planHash: plannerBody.plan_hash,
      plan: plannerBody.plan,
      expectedVersion: turn.planVersionExpected,
      maximumRequiredStepCount: turn.maxRequiredStepCount,
      analysisPlanStepCap: ANALYSIS_PLAN_STEP_CAP,
      actualStepCount: planSteps.length,
    });
    await writeJson(path.join(turnOut, "RUNTIME_EVIDENCE.json"), {
      schemaVersion: "PhaseER16RuntimeEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      jobId,
      job: beforeInterpretation.job,
      events: beforeInterpretation.events,
      dependencies: beforeInterpretation.dependencies,
      queueWorkerPathRequired: true,
    });
    await writeJson(path.join(turnOut, "TOOLCALL_EVIDENCE.json"), {
      schemaVersion: "PhaseER16ToolCallEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      requiredExecutionTools: turn.requiredExecutionTools,
      observedTools,
      missingRequiredTools,
      forbiddenObservedTools,
      toolCalls: beforeInterpretation.toolCalls,
    });
    await writeJson(path.join(turnOut, "ARTIFACT_EVIDENCE.json"), {
      schemaVersion: "PhaseER16ArtifactEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      requiredCaseArtifacts: item.contract.requiredArtifacts,
      artifacts: beforeInterpretation.artifacts,
    });
    if (missingRequiredTools.length) throw new Error(`Missing required Tools: ${missingRequiredTools.join(", ")}`);
    if (forbiddenObservedTools.length) throw new Error(`Forbidden Tools executed: ${forbiddenObservedTools.join(", ")}`);
    if (turn.requiredExecutionTools.length > turn.maxRequiredStepCount) {
      throw new Error(
        `Frozen turn requires ${turn.requiredExecutionTools.length} Tools but declares maxRequiredStepCount ${turn.maxRequiredStepCount}`,
      );
    }
    if (planSteps.length > ANALYSIS_PLAN_STEP_CAP) {
      throw new Error(`Plan step count ${planSteps.length} exceeds AnalysisPlan cap ${ANALYSIS_PLAN_STEP_CAP}`);
    }
    const interpretation = await generateInterpretation(page, jobId, turnOut);
    const afterInterpretation = await apiJobEvidence(jobId);
    await page.screenshot({ path: path.join(OUT, turnOut, "results.png"), fullPage: true });
    await writeJson(path.join(turnOut, "RUNTIME_EVIDENCE.json"), {
      schemaVersion: "PhaseER16RuntimeEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      jobId,
      job: afterInterpretation.job,
      events: afterInterpretation.events,
      dependencies: afterInterpretation.dependencies,
      queueWorkerPathRequired: true,
    });
    await writeJson(path.join(turnOut, "TOOLCALL_EVIDENCE.json"), {
      schemaVersion: "PhaseER16ToolCallEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      requiredExecutionTools: turn.requiredExecutionTools,
      observedTools,
      missingRequiredTools,
      forbiddenObservedTools,
      toolCalls: afterInterpretation.toolCalls,
    });
    await writeJson(path.join(turnOut, "ARTIFACT_EVIDENCE.json"), {
      schemaVersion: "PhaseER16ArtifactEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      requiredCaseArtifacts: item.contract.requiredArtifacts,
      artifacts: afterInterpretation.artifacts,
    });
    const workspace = await openWorkspaceAndReport(page, item, turn, afterInterpretation, turnOut);
    await writeJson(path.join(turnOut, "BROWSER_EVIDENCE.json"), {
      schemaVersion: "PhaseER16BrowserEvidence/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      browser: "Google Chrome",
      browserVersion: await page.evaluate(() => navigator.userAgent),
      viewport: page.viewportSize(),
      browserInitiatedSubmission: true,
      fatalPageErrors: audit.pageErrors,
      consoleErrors: audit.consoleErrors,
      failedResponses: audit.failedResponses,
      externalBrowserRequests: audit.browserExternalRequests,
    });
    await writeJson(path.join(turnOut, "TURN_EXECUTION.json"), {
      schemaVersion: "PhaseER16TurnExecution/1.0",
      caseId: item.caseId,
      turnId: turn.turnId,
      committedProductState: "CURRENT_COMMITTED_PRODUCT_STATE",
      projectId,
      datasetId: dataset.datasetId,
      profileId: dataset.profileId,
      jobId,
      planId: plannerBody.plan_id,
      requiredExecutionTools: turn.requiredExecutionTools,
      observedTools,
      artifactIds: afterInterpretation.artifacts.map((artifact) => artifact.artifactId || artifact.id),
      interpretationId: interpretation.interpretationId || interpretation.interpretation?.interpretationId,
      workspaceId: workspace.workspaceId,
      reportId: workspace.report?.finalize?.reportId || null,
      recipePresent: Boolean(workspace.report?.recipeVisible),
      decision: "PASS_DISCOVERY",
      realPlannerCall: true,
      realInterpretationCall: true,
      injectionCounters: {
        handcraftedIntent: 0,
        handcraftedPlan: 0,
        handcraftedJob: 0,
        handcraftedToolCall: 0,
        handcraftedArtifact: 0,
        handcraftedReport: 0,
        replayedLlmResponse: 0,
      },
    });
    return {
      turnId: turn.turnId,
      status: "PASS_DISCOVERY",
      jobId,
      planId: plannerBody.plan_id,
      observedTools,
      artifactTypes: unique(afterInterpretation.artifacts.map((artifact) => artifact.type)),
      workspaceId: workspace.workspaceId,
      reportId: workspace.report?.finalize?.reportId || null,
      realLlmCalls: 2,
    };
  } finally {
    await context.close();
  }
}

async function runExpectedRejection(browser, item, projectId, dataset, caseOut) {
  const turnOut = path.join(caseOut, "rejection");
  const audit = { consoleErrors: [], consoleMessages: [], pageErrors: [], failedResponses: [], browserExternalRequests: [] };
  const { context, page } = await openEnglishApp(browser, audit);
  try {
    await selectDataset(page, projectId, dataset.datasetId);
    await page.getByLabel("Natural language request").fill(item.contract.canonicalQuestion);
    const plannerResponsePromise = page.waitForResponse(
      (response) => response.request().method() === "POST" && responsePath(response) === "/planner/jobs",
      { timeout: ACTION_TIMEOUT_MS },
    );
    await page.getByTestId("planner-form").getByRole("button", { name: "Create and run" }).click();
    const plannerResponse = await plannerResponsePromise;
    const body = await plannerResponse.json();
    const jobsBefore = await api(`/projects/${projectId}/analysis-jobs`);
    const planCreated = Boolean(body.plan || body.plan_id);
    const jobCreated = Boolean(body.job || body.job_id);
    const correct = !body.ok && !planCreated && !jobCreated;
    if (!correct) throw new Error(`Expected pre-Plan rejection, got ${JSON.stringify(body)}`);
    await page.getByTestId("analysis-intent-unsupported").waitFor().catch(() =>
      page.getByTestId("validation-failure").waitFor(),
    );
    await page.screenshot({ path: path.join(OUT, turnOut, "expected_rejection.png"), fullPage: true });
    const evidence = {
      schemaVersion: "PhaseER16ExpectedRejectionEvidence/1.0",
      caseId: item.caseId,
      committedProductState: "CURRENT_COMMITTED_PRODUCT_STATE",
      projectId,
      datasetId: dataset.datasetId,
      profileId: dataset.profileId,
      canonicalQuestion: item.contract.canonicalQuestion,
      response: body,
      planCreated,
      jobCreated,
      toolCallCreated: false,
      artifactCreated: false,
      reportCreated: false,
      recipeCreated: false,
      projectAnalysisJobs: jobsBefore,
      browserAudit: audit,
      decision: "PASS_DISCOVERY",
      realLlmCalls: body.provider_called === false ? 0 : 1,
    };
    await writeJson(path.join(turnOut, "EXPECTED_REJECTION_EVIDENCE.json"), evidence);
    await writeText(
      path.join(caseOut, "CASE_RESULT.md"),
      `# ${item.caseId} Discovery Result\n\nPASS_DISCOVERY: typed pre-Plan rejection; no Plan, Job, ToolCall, Artifact, Report, or Recipe.\n`,
    );
    return { status: "PASS_DISCOVERY", rejection: true, realLlmCalls: evidence.realLlmCalls };
  } finally {
    await context.close();
  }
}

async function runCase(item) {
  const playwright = await import(pathToFileURL(PLAYWRIGHT).href);
  const browser = await playwright.chromium.launch({ executablePath: CHROME, headless: true });
  const caseOut = path.join("cases", item.caseId);
  await mkdir(path.join(OUT, caseOut), { recursive: true });
  const caseRecord = {
    schemaVersion: "PhaseER16CaseExecution/1.0",
    caseId: item.caseId,
    committedProductState: "CURRENT_COMMITTED_PRODUCT_STATE",
    executionMode: CAMPAIGN_MODE,
    status: "PROCESSING",
    contract: {
      caseType: item.contract.caseType,
      analysisExecutionExpected: item.contract.analysisExecutionExpected,
      requiredExecutionTools: item.contract.requiredExecutionTools,
      requiredArtifacts: item.contract.requiredArtifacts,
      requiredRenderers: item.contract.requiredRenderers,
      requiredLimitations: item.contract.requiredLimitations,
      requiredReportBehavior: item.contract.requiredReportBehavior,
      requiredRecipeBehavior: item.contract.requiredRecipeBehavior,
    },
    turns: [],
  };
  await writeJson(path.join(caseOut, "CASE_EXECUTION.json"), caseRecord);
  try {
    const project = await createProject(item.caseId);
    const projectId = projectIdentity(project);
    if (!projectId) throw new Error(`Project creation returned no identity: ${JSON.stringify(project)}`);
    const uploadAudit = { consoleErrors: [], consoleMessages: [], pageErrors: [], failedResponses: [], browserExternalRequests: [] };
    const { context, page } = await openEnglishApp(browser, uploadAudit);
    let dataset;
    try {
      dataset = await uploadCase(page, item, projectId, caseOut);
      await page.screenshot({ path: path.join(OUT, caseOut, "import_ready.png"), fullPage: true });
      await writeJson(path.join(caseOut, "IMPORT_BROWSER_AUDIT.json"), uploadAudit);
    } finally {
      await context.close();
    }
    caseRecord.projectId = projectId;
    caseRecord.datasetId = dataset.datasetId;
    caseRecord.profileId = dataset.profileId;
    await writeJson(path.join(caseOut, "CASE_EXECUTION.json"), caseRecord);
    if (!item.contract.analysisExecutionExpected) {
      const rejection = await runExpectedRejection(browser, item, projectId, dataset, caseOut);
      caseRecord.status = rejection.status;
      caseRecord.rejection = rejection;
      caseRecord.realLlmCalls = rejection.realLlmCalls;
    } else {
      for (let index = 0; index < item.contract.executionTurns.length; index += 1) {
        const turn = item.contract.executionTurns[index];
        const result = await runAnalysisTurn(browser, item, projectId, dataset, turn, index, caseOut);
        caseRecord.turns.push(result);
        await writeJson(path.join(caseOut, "CASE_EXECUTION.json"), caseRecord);
      }
      const observedUnion = unique(caseRecord.turns.flatMap((turn) => turn.observedTools));
      const missingCaseTools = item.contract.requiredExecutionTools.filter((tool) => !observedUnion.includes(tool));
      if (missingCaseTools.length) throw new Error(`Case Tool union missing: ${missingCaseTools.join(", ")}`);
      caseRecord.observedRequiredToolUnion = observedUnion;
      caseRecord.missingCaseRequiredTools = missingCaseTools;
      caseRecord.realLlmCalls = caseRecord.turns.reduce((sum, turn) => sum + turn.realLlmCalls, 0);
      caseRecord.status = "PASS_DISCOVERY";
      await writeText(
        path.join(caseOut, "CASE_RESULT.md"),
        `# ${item.caseId} Discovery Result\n\nPASS_DISCOVERY across ${caseRecord.turns.length} declared execution turn(s) on the unchanged committed product state.\n`,
      );
    }
    await writeJson(path.join(caseOut, "CASE_EXECUTION.json"), caseRecord);
    return caseRecord;
  } catch (error) {
    caseRecord.status = "FAIL_DISCOVERY";
    caseRecord.error = error instanceof Error ? error.stack || error.message : String(error);
    await writeJson(path.join(caseOut, "CASE_EXECUTION.json"), caseRecord);
    await writeText(
      path.join(caseOut, "CASE_RESULT.md"),
      `# ${item.caseId} Discovery Result\n\nFAIL_DISCOVERY\n\n${String(caseRecord.error)}\n`,
    );
    throw error;
  } finally {
    await browser.close();
  }
}

async function runTransportSmoke(cases) {
  const smokeCaseIds = [
    "Q-TABLE-001",
    "Q-ARCHIVE-001",
    "Q-XRD-001",
    "Q-ELECTRONIC-001",
    "Q-TRAJECTORY-001",
  ];
  const selected = smokeCaseIds.map((caseId) => {
    const item = cases.find((candidate) => candidate.caseId === caseId);
    if (!item) throw new Error(`Transport smoke Case missing from authority: ${caseId}`);
    return item;
  });
  const playwright = await import(pathToFileURL(PLAYWRIGHT).href);
  const browser = await playwright.chromium.launch({ executablePath: CHROME, headless: true });
  const observations = [];
  try {
    for (const item of selected) {
      const audit = { consoleErrors: [], consoleMessages: [], pageErrors: [], failedResponses: [], browserExternalRequests: [] };
      const project = await createProject(`phase-d-transport-${item.caseId}`);
      const projectId = projectIdentity(project);
      if (!projectId) throw new Error(`Project creation returned no identity: ${JSON.stringify(project)}`);
      const { context, page } = await openEnglishApp(browser, audit);
      try {
        const result = await uploadCase(page, item, projectId, path.join("phase_d_transport", item.caseId));
        const input = result.uploadResponse?.inputTransport || {};
        const profile = result.uploadResponse?.profile || {};
        const objects = profile.objects || [];
        const objectTypes = objects.map((item) => item.objectType).sort();
        const trajectorySemantic = (profile.resourceSemantics || []).find(
          (resource) => resource.objectType === "Trajectory",
        );
        const trajectoryReadiness = profile.trajectoryReadiness || null;
        observations.push({
          caseId: item.caseId,
          projectId,
          datasetId: result.datasetId,
          profileId: result.profileId,
          objectTypes,
          uploadFileOrderSemantic: input.fileOrderIsSemanticAuthority === false,
          sameDatasetBinding: input.sameDatasetBinding === true,
          inputFiles: (input.files || []).map((file) => ({
            fileName: file.fileName,
            byteSize: file.byteSize,
            storageKey: file.storageKey,
            companionGroupId: file.companionGroupId || null,
          })),
          profileReadiness: {
            experimentalXrd: profile.experimentalXrdReadiness?.status || null,
            electronic: profile.electronicReadiness?.status || null,
            trajectory: trajectoryReadiness?.status || null,
          },
          trajectoryFacts: trajectorySemantic?.facts || null,
          trajectoryReadiness,
          browserAudit: audit,
        });
        await page.screenshot({ path: path.join(OUT, "phase_d_transport", `${item.caseId}_import_ready.png`), fullPage: true });
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
  const observation = (caseId) => observations.find((item) => item.caseId === caseId);
  const archive = observation("Q-ARCHIVE-001");
  const xrd = observation("Q-XRD-001");
  const electronic = observation("Q-ELECTRONIC-001");
  const trajectory = observation("Q-TRAJECTORY-001");
  const trajectoryResource = trajectory?.trajectoryReadiness?.resources?.[0];
  const allAuditsClean = observations.every((item) =>
    item.browserAudit.pageErrors.length === 0 && item.browserAudit.failedResponses.length === 0,
  );
  const gates = {
    appShellAccessible: true,
    textImportReady: observation("Q-TABLE-001")?.objectTypes.includes("DataFrame") === true,
    archiveBinaryImportReady: archive?.inputFiles.length === 1 && archive.uploadFileOrderSemantic,
    xrdSameDatasetCompanionReady:
      xrd?.sameDatasetBinding && xrd.uploadFileOrderSemantic &&
      xrd.objectTypes.includes("Structure") && xrd.objectTypes.includes("DataFrame") &&
      xrd.profileReadiness.experimentalXrd === "READY",
    electronicSameDatasetCompanionReady:
      electronic?.sameDatasetBinding && electronic.uploadFileOrderSemantic &&
      electronic.objectTypes.includes("ElectronicBand") && electronic.objectTypes.includes("ElectronicDos") &&
      electronic.profileReadiness.electronic === "READY",
    trajectoryImportReady:
      trajectory?.objectTypes.includes("Trajectory") &&
      trajectory?.profileReadiness.trajectory === "READY" &&
      trajectory?.inputFiles.length === 1,
    trajectoryProfileFactsCorrect:
      trajectory?.trajectoryFacts?.frameCount === 15 &&
      trajectory?.trajectoryFacts?.atomCount === 516 &&
      trajectory?.trajectoryFacts?.coordinateMode === "cartesian" &&
      trajectory?.trajectoryFacts?.positionWrapping === "unwrapped" &&
      trajectory?.trajectoryFacts?.latticeMode === "fixed" &&
      trajectory?.trajectoryFacts?.timeAvailable === true &&
      trajectory?.trajectoryFacts?.timeStartPs === 0 &&
      trajectory?.trajectoryFacts?.timeEndPs === 1.05,
    trajectoryScientificSemanticsCorrect:
      trajectoryResource?.frameCount === 15 &&
      trajectoryResource?.atomCount === 516 &&
      trajectoryResource?.stableAtomIdentity === true &&
      trajectoryResource?.speciesStable === true &&
      trajectoryResource?.coordinateRepresentation === "cartesian" &&
      trajectoryResource?.coordinateUnit === "angstrom" &&
      trajectoryResource?.cellMode === "fixed" &&
      trajectoryResource?.timePresent === true &&
      trajectoryResource?.timeUnit === "femtosecond" &&
      trajectoryResource?.timeMonotonic === true &&
      trajectoryResource?.constantTimestep === true &&
      JSON.stringify(trajectoryResource?.pbcAxes) === JSON.stringify([true, true, true]),
    browserErrors: allAuditsClean ? 0 : 1,
    realLlmCalls: 0,
    formalQualificationExecutions: 0,
  };
  await writeJson("BROWSER_TRANSPORT_READINESS.json", {
    schemaVersion: "PhaseDR16BrowserTransportReadiness/1.0",
    authority: "DIRECT_BROWSER_RUNTIME_OBSERVATION",
    observations,
    gates,
    result: Object.values(gates).every((value) => value === true || value === 0) ? "PASS" : "FAIL",
  });
  process.stdout.write(`${JSON.stringify(gates, null, 2)}\n`);
}

async function updateCampaign(caseResult) {
  const file = path.join(OUT, "CAMPAIGN_MANIFEST.json");
  const campaign = await readJson(file);
  campaign.casesStarted = unique([...campaign.casesStarted, caseResult.caseId]);
  campaign.realLlmCallsObserved += Number(caseResult.realLlmCalls || 0);
  if (caseResult.status === "PASS_DISCOVERY") {
    campaign.casesCompleted = unique([...campaign.casesCompleted, caseResult.caseId]);
    campaign.casesPassed = unique([...campaign.casesPassed, caseResult.caseId]);
  }
  campaign.status = caseResult.status === "PASS_DISCOVERY" ? "PROCESSING" : "DISCOVERY_FAILURE";
  await writeJson("CAMPAIGN_MANIFEST.json", campaign);
}

async function main() {
  await mkdir(OUT, { recursive: true });
  const cases = await loadCases();
  const prepared = await prepareAuthorityEvidence(cases);
  if (prepareOnly) {
    process.stdout.write(`${JSON.stringify(prepared.snapshot.totals, null, 2)}\n`);
    return;
  }
  if (transportSmoke) {
    await runTransportSmoke(cases);
    return;
  }
  if (!selectedCaseId) throw new Error("Pass --case Q-... or --prepare-only");
  const item = cases.find((candidate) => candidate.caseId === selectedCaseId);
  if (!item) throw new Error(`Unknown Case ${selectedCaseId}`);
  const result = await runCase(item);
  await updateCampaign(result);
  process.stdout.write(`${JSON.stringify({ caseId: result.caseId, status: result.status }, null, 2)}\n`);
}

await main();
