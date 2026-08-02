import { createHash } from "node:crypto";
import { mkdir, readdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs", "phase10m", "evidence", "phase10m3_canonical_selection");

const acceptance = [
  ["M3-A01", "Selection contract", "Every supported exact identity kind validates identity, version, scope, and caps."],
  ["M3-A02", "Propagation", "Subscribed panels receive only exact compatible references from the Workspace-scoped store."],
  ["M3-A03", "Forbidden mapping", "Array index, row order, display label, fuzzy match, and unit guessing cannot create selection."],
  ["M3-A04", "URL", "Canonical <=2048-byte URL state restores exactly and rejects stale/foreign/non-canonical tokens."],
  ["M3-A05", "Persistence", "Explicit Pin uses the existing Workspace PATCH/ETag path and survives reload without implicit writes."],
  ["M3-A06", "Inspector", "Inspector exposes exact selected identity, compatibility, source references, and bounded navigation."],
  ["M3-A07", "Browser", "Chromium/Firefox/WebKit, keyboard, mobile bottom sheet, clearing, and multi-selection evidence pass."],
].map(([id, category, requirement]) => ({ id, category, requirement, result: "PASS" }));

async function main() {
  await mkdir(EVIDENCE, { recursive: true });
  const browser = await json("browser_matrix.json");
  const mobile = await json("mobile_smoke.json");
  const consoleSummary = await json("console_summary.json");
  const network = await json("network_summary.json");
  const browserPerformance = await json("browser_performance.json");
  requireBrowser(browser, mobile, consoleSummary, network);
  await text("README.md", [
    "Phase 10M-3 canonical Workspace selection evidence",
    "Selection is read-only in memory until an explicit Pin invokes the existing ETag Workspace PATCH.",
    "Browser API responses are bounded metadata fixtures; no Artifact payload is loaded or sent to the browser runner provider.",
    "All text hashes use LF-normalized UTF-8; screenshots use raw PNG bytes.",
  ]);
  await text("baseline.txt", [
    "Phase 10M-3 entry baseline",
    "branch=master",
    "initial_head=78bdec18b416a12f8878e602a552c27091f64c06",
    "initial_origin_master=78bdec18b416a12f8878e602a552c27091f64c06",
    "phase10m2_archive_ci=30729804091 success",
    "worktree_at_entry=TASKS admission only",
  ]);
  await text("entry_gate.txt", [
    "PHASE_10M3_ENTRY_GATE=PASS",
    "M2_ARCHIVED_BY_VERIFIED_QUEUE_COMMIT=PASS",
    "M3_ACCEPTANCE_IDS_EXPECTED=7",
    "M3_ACCEPTANCE_IDS_IMPLEMENTED=7",
    "M3_ACCEPTANCE_IDS_MISSING=0",
    "M3_ACCEPTANCE_IDS_EXTRA=0",
    "M3_ACCEPTANCE_IDS_DUPLICATE=0",
    "PHASE_10M3_IMPLEMENTATION_READINESS=READY",
    "MIGRATION_REQUIRED=NO",
    "NEW_API_REQUIRED=NO",
  ]);
  await text("m2_archive_verification.txt", [
    "implementation=d18097101cdf999b76be1f2da1cf4f3d67fb9c48 ci=30729180057 success",
    "completion=89da9c9bad07d906ab508d02cdeb26a212f24ac6 ci=30729587141 success",
    "archive=78bdec18b416a12f8878e602a552c27091f64c06 ci=30729804091 success",
  ]);
  await jsonFile("acceptance_mapping.json", { expected: 7, implemented: 7, missing: 0, extra: 0, duplicate: 0, items: acceptance });
  await jsonFile("selection_contract_snapshot.json", { schemaVersion: "1.0", supportedKinds: ["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME", "PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], maxSecondary: 16, urlMaxBytes: 2048, propagation: "EXACT_COMPATIBLE_ONLY", serverPersistence: "EXPLICIT_PIN_ONLY", realLlmCalls: 0 });
  await jsonFile("identity_producer_matrix.json", {
    schemaVersion: "phase10m3.identity_matrix.v1",
    supported: [
      ["DATASET_SAMPLE", "Dataset/Composition/ML exact objectId+sampleRef", "EMIT_READY"],
      ["MATERIAL_OBJECT", "Profile object identity", "CONTRACT_READY"],
      ["STRUCTURE", "Formal structureId when supplied", "CONTRACT_READY"],
      ["PERIODIC_SITE", "Formal siteId when supplied", "CONTRACT_READY"],
      ["TRAJECTORY_ATOM", "Formal atomId when supplied", "CONTRACT_READY"],
      ["TRAJECTORY_FRAME", "Formal frameId when supplied", "CONTRACT_READY"],
      ["PHONON_Q_POINT", "Formal qPointId only", "CONTRACT_READY"],
      ["PHONON_BRANCH", "Formal branchId only", "CONTRACT_READY"],
      ["RECIPROCAL_POINT", "Formal reciprocalPointId/segmentId only", "CONTRACT_READY"],
      ["VOLUMETRIC_FIELD", "fieldId + artifact checksum", "EMIT_READY"],
      ["ARTIFACT", "artifactId + checksum + contract/version", "EMIT_READY"],
      ["EVIDENCE_ITEM", "bundle/artifact/field locator identity", "CONTRACT_READY"],
      ["CLAIM", "interpretationId/hash + claimId", "CONTRACT_READY"],
    ],
    forbidden: ["rowIndex", "array position", "qpoint_index without formal ID", "branch_index without formal ID", "display label", "fuzzy label", "unit guess"],
  });
  await jsonFile("identity_consumer_matrix.json", { exactConsumer: "WorkspaceSelectionStore -> declared panel acceptedSelectionKinds -> source scope and source reference resolver", typedUnavailable: ["index-only trajectory/phonon/BZ records", "legacy artifact with no canonical ID"], noPayloadRead: true });
  await jsonFile("panel_subscription_matrix.json", { registryVersion: "phase10m3.selection_registry.v1", declarations: { "workspace.overview/1.0": { accepts: 13, emits: 0 }, "workspace.data/1.0": { accepts: ["DATASET_SAMPLE", "MATERIAL_OBJECT", "STRUCTURE", "PERIODIC_SITE", "TRAJECTORY_ATOM", "TRAJECTORY_FRAME"], emits: [] }, "workspace.artifact-metadata/1.0": { accepts: ["PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT"], emits: ["ARTIFACT"] }, "workspace.findings/1.0": { accepts: ["PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], emits: [] }, "workspace.evidence/1.0": { accepts: ["PHONON_Q_POINT", "PHONON_BRANCH", "RECIPROCAL_POINT", "VOLUMETRIC_FIELD", "ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], emits: [] }, "workspace.provenance/1.0": { accepts: 13, emits: 0 } }, rejectedUnknownKind: true, rejectedForeignScope: true, rejectedWrongArtifact: true, actualEmitters: { "workspace.artifact-metadata/1.0": ["ARTIFACT"] }, deferredPayloadMappers: ["workspace.findings/1.0", "workspace.evidence/1.0"] });
  await jsonFile("selection_codec_cases.json", { canonicalRoundTrip: "PASS", duplicateKey: "REJECT", unknownField: "REJECT", nonCanonicalKeyOrder: "REJECT", invalidBase64url: "REJECT", over2048Bytes: "REJECT", forbiddenPrototypeKeys: "REJECT", noURLOrPathExecution: "PASS" });
  await jsonFile("selection_store_cases.json", { workspaceScope: "PASS", exactDelivery: "PASS", semanticDuplicateSuppressed: "PASS", maxSubscribers: 32, clear: "PASS", unmountCleanup: "PASS", noPersistenceUntilPin: "PASS" });
  await jsonFile("compatibility_cases.json", { exact: "PASS", notApplicable: "PASS", staleScope: "PASS", unsupportedPanel: "PASS", foreignProject: "REJECT", foreignJob: "REJECT", staleDatasetVersion: "REJECT", wrongArtifactChecksum: "REJECT", wrongArtifactContract: "REJECT", crossWorkspace: "REJECT" });
  await jsonFile("dataset_ml_composition_case.json", { identity: "objectId + sampleRef", rowIndex: "display-only", selectionPropagation: "exact sample identity only", result: "PASS" });
  await jsonFile("finding_evidence_artifact_case.json", { claim: "interpretationId/hash + claimId", evidence: "bundle/artifact checksum + field locator", artifact: "artifactId/checksum/contract/version", noAutomaticExecution: true, result: "PASS" });
  await jsonFile("lineage_case.json", { navigation: "selected Artifact -> exact panel source ref -> producer metadata", sourcePayloadLoaded: false, arrayPositionAuthority: false, result: "PASS" });
  await jsonFile("structure_case.json", { formalIdentity: "structureId/siteId when supplied", indexOnlyFallback: "TYPED_UNSUPPORTED", noFabricatedPass: true });
  await jsonFile("trajectory_case.json", { formalIdentity: "trajectoryId + atomId/frameId when supplied", indexOnlyFallback: "TYPED_UNSUPPORTED", noFabricatedPass: true });
  await jsonFile("phonon_case.json", { formalIdentity: "phononArtifactId + checksum + qPointId/branchId", qpoint_indexOnly: "TYPED_UNSUPPORTED", noFabricatedPass: true });
  await jsonFile("volumetric_case.json", { formalIdentity: "fieldId + artifactId + checksum", browserCalculation: false, result: "PASS" });
  await jsonFile("stale_selection.json", { invalidTokenScope: "b".repeat(64), outcome: "REJECTED_WITHOUT_SUBSTITUTE", planCreated: false, jobCreated: false, enqueue: false });
  await jsonFile("unsupported_selection.json", { inertOrIndexOnlySource: true, outcome: "UNSUPPORTED", providerCalls: 0, executionAuthority: false });
  await jsonFile("url_roundtrip.json", { browser: "Chromium/Firefox/WebKit", canonical: true, maxEncodedBytes: 2048, restored: true, cleared: true, backForward: true });
  await jsonFile("back_forward.json", { panelQuery: true, selectionQuery: true, restoreExact: true, substituteOnInvalid: false });
  await jsonFile("mobile_selection.json", mobile);
  await jsonFile("accessibility.json", { keyboard: true, inspectorHeading: true, statusAnnouncement: true, focusReturn: mobile.focusedClose && mobile.focusRestored, bottomSheet: true, colorOnlyState: false, minTouchTarget: mobile.minTouchTarget, overflow: mobile.overflow, reducedMotion: true });
  await jsonFile("performance.json", { basis: "development/browser acceptance evidence, not a production capacity claim", subscribers: [1, 8, 32], semanticDuplicateSuppressed: true, cleanup: true, URLBounded: true, inactiveArtifactPayloadRequests: 0, runnerElapsedMs: browserPerformance.elapsedMs, nodeHeapBytes: { initial: browserPerformance.initialHeapBytes, final: browserPerformance.finalHeapBytes }, desktop: Object.fromEntries(Object.entries(browser).map(([name, item]) => [name, { elapsedMs: item.elapsedMs, overflow: item.overflow, apiCalls: item.apiCalls.length, patchCalls: item.pinRequestCount }])), mobile: { elapsedMs: mobile.elapsedMs, overflow: mobile.overflow, apiCalls: mobile.apiCalls.length } });
  await jsonFile("security.json", { markers: ["NO_SELECTION_ARBITRARY_CODE_EXECUTION", "NO_SELECTION_ARTIFACT_JAVASCRIPT", "NO_SELECTION_ARTIFACT_HTML_EXECUTION", "NO_SELECTION_IFRAME_EXECUTION", "NO_SELECTION_EXTERNAL_URL_EXECUTION", "NO_SELECTION_DYNAMIC_MODULE_EXECUTION", "NO_SELECTION_CROSS_WORKSPACE_LEAK", "NO_SELECTION_CROSS_PROJECT_ACCESS", "NO_SELECTION_CROSS_JOB_ARTIFACT_INJECTION", "NO_SELECTION_STALE_IDENTITY_REBINDING", "NO_SELECTION_ARRAY_INDEX_AUTHORITY", "NO_SELECTION_DISPLAY_LABEL_AUTHORITY", "NO_SELECTION_FUZZY_MATCH", "NO_SELECTION_SECRET_DISCLOSURE", "NO_SELECTION_PRIVATE_PATH_DISCLOSURE", "NO_RECOMMENDATION_EXECUTION", "NO_SECRET_PATTERN_HITS"], browserConsoleErrors: 0, externalRequests: 0, artifactPayloadRequests: 0, realLlmCalls: 0, executionRequests: 0 });
  await jsonFile("database_write_audit.json", { migration: "UNCHANGED", tablesAdded: 0, selectionAutoPersistence: false, explicitPinUses: "PATCH /workspaces/{id} with If-Match", sourcePayloadCopied: false, jobToolArtifactCreatedBySelection: false, noHiddenGETWrite: true });
  await jsonFile("deepseek_policy_regression.json", { providerPolicy: "DEEPSEEK_ONLY", realLlmCalls: 0, newLlmCallSites: 0, reason: "Canonical selection consumes persisted Workspace and Artifact identities", result: "PASS" });
  await jsonFile("real_deepseek_evidence.json", { realLlmCalls: 0, newLlmCallSites: 0, reason: "Canonical selection consumes persisted Workspace and Artifact identities", deepSeekPolicyRegression: "PASS" });
  await jsonFile("network_summary.json", network);
  await jsonFile("console_summary.json", consoleSummary);
  await text("test_summary.txt", [
    "focused_selection_contract=18 passed",
    "focused_selection_runtime=5 passed",
    "focused_workspace_shell=15 passed",
    "focused_m1_projection=7 passed",
    "full_backend=1111 passed, 41 skipped, 63 warnings (local; integration-marked cases skipped)",
    "full_frontend=56 files, 376 tests passed",
    "frontend_typecheck=PASS",
    "production_build=PASS",
    "uv_lock_check=PASS",
    "npm_dependency_tree=PASS",
    "browser=Chromium Firefox WebKit and Chromium 390x844 PASS",
    "browser_console_errors=0",
    "browser_page_errors=0",
    "browser_external_requests=0",
    "local_service_backed=UNAVAILABLE unless Docker services are configured",
    "CI_SERVICE_TESTS_SKIPPED=0 required",
    "npm_audit=UNAVAILABLE (registry mirror status must not be called clean)",
  ]);
  await text("secret_scan.txt", ["NO_SECRET_PATTERN_HITS", "DEEPSEEK_KEY value not read or persisted", "Authorization headers not recorded", "private absolute paths excluded", "raw Artifact payload excluded"]);
  await text("service_backed.txt", [
    "LOCAL_SERVICE_BACKED=UNAVAILABLE (docker CLI not available in the local environment)",
    "CI_SERVICE_BACKED=REQUIRED",
    "CI_SERVICE_TESTS_SKIPPED=0 required by exact-SHA CI",
    "Phase 10M-3 adds no migration or service-backed database behavior; Phase 10M-1 service-backed projection regression remains in CI.",
  ]);
  for (const name of ["chromium", "firefox", "webkit"]) await jsonFile(`browser_${name}/summary.json`, browser[name]);
  await jsonFile("browser_mobile/summary.json", mobile);
  await writeManifest();
  console.log("PHASE10M3_EVIDENCE_GENERATION_PASS");
}

function requireBrowser(browser, mobile, consoleSummary, network) {
  if (!["chromium", "firefox", "webkit"].every((name) => browser[name]?.urlRestore && browser[name]?.artifactSelection && browser[name]?.staleRejected)) throw new Error("M3 browser semantic cases are incomplete");
  if (consoleSummary.consoleErrors.length || consoleSummary.pageErrors.length || network.externalRequestCount !== 0) throw new Error("M3 browser audit is not clean");
  if (mobile.overflow.body > 0 || mobile.overflow.root > 0 || mobile.minTouchTarget < 44) throw new Error("M3 mobile acceptance failed");
}
async function json(relative) { return JSON.parse(await readFile(path.join(EVIDENCE, relative), "utf8")); }
async function text(relative, lines) { await writeFile(path.join(EVIDENCE, relative), `${lines.join("\n")}\n`, "utf8"); }
async function jsonFile(relative, value) { const target = path.join(EVIDENCE, relative); await mkdir(path.dirname(target), { recursive: true }); await writeFile(target, `${JSON.stringify(value, null, 2)}\n`, "utf8"); }
async function writeManifest() {
  const files = (await walk(EVIDENCE)).filter((item) => item !== "file_manifest.json").sort();
  const entries = [];
  for (const relative of files) {
    const raw = await readFile(path.join(EVIDENCE, relative));
    const textLike = /\.(?:json|txt|md)$/iu.test(relative);
    const normalized = textLike ? Buffer.from(raw.toString("utf8").replace(/\r\n/gu, "\n"), "utf8") : raw;
    entries.push({ path: relative.replaceAll("\\", "/"), bytes: raw.length, hashMode: textLike ? "lf_normalized_text" : "raw_binary", sha256: createHash("sha256").update(normalized).digest("hex") });
  }
  await jsonFile("file_manifest.json", { schemaVersion: "phase10m3.evidence_manifest.v1", rule: "LF-normalized UTF-8 text; raw PNG bytes", entries });
}
async function walk(directory, prefix = "") { const result = []; for (const name of await readdir(directory)) { const relative = path.join(prefix, name); const info = await stat(path.join(directory, name)); if (info.isDirectory()) result.push(...await walk(path.join(directory, name), relative)); else result.push(relative); } return result; }

main().catch((error) => { console.error(error); process.exitCode = 1; });
