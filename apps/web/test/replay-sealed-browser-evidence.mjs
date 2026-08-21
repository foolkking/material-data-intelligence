import { spawnSync } from "node:child_process";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const WEB_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const REPO_ROOT = path.resolve(WEB_ROOT, "../..");
const browserModule = process.env.MDI_PLAYWRIGHT_MODULE || path.join(WEB_ROOT, "node_modules/playwright/index.mjs");
const npmCommand = process.platform === "win32" ? "npm.cmd" : "npm";
const listOnly = process.argv.includes("--list");
const common = {
  ...process.env,
  MDI_PLAYWRIGHT_MODULE: browserModule,
};

function run(label, command, args, env = common, cwd = WEB_ROOT) {
  console.log(`\n=== ${label} ===`);
  if (listOnly) {
    console.log([command, ...args].join(" "));
    return;
  }
  const result = spawnSync(command, args, { cwd, env, stdio: "inherit", shell: false });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`${label} exited with status ${result.status}`);
}

run("Phase 10 closure evidence integrity", "node", ["test/phase10-closure-evidence-check.mjs"]);
run("Trajectory performance evidence integrity", npmCommand, ["run", "test:trajectory-performance-evidence"]);

run("Phase 10L-4 grounded interpretation", "node", [
  "test/grounded-interpretation-browser-evidence.mjs", "--validate-fixtures",
]);
run("Phase 10L-4 grounded interpretation replay", "node", [
  "test/grounded-interpretation-browser-evidence.mjs",
  "--output-dir", path.join(process.env.RUNNER_TEMP || path.join(WEB_ROOT, ".tmp"), "phase10l4-browser-replay"),
  "--compare-with", path.join(REPO_ROOT, "docs/phase10l/evidence/phase10l4_grounded_interpretation/browser_semantic_contract.json"),
], { ...common, MDI_PHASE10L4_BROWSERS: "chromium,firefox,webkit", MDI_PHASE10L4_EVIDENCE_PORT: "3222" });

run("Phase 10L-5 natural-language", "node", ["test/natural-language-closure-browser-evidence.mjs", "--validate-fixtures"]);
run("Phase 10L-5 natural-language replay", "node", [
  "test/natural-language-closure-browser-evidence.mjs",
  "--output-dir", path.join(process.env.RUNNER_TEMP || path.join(WEB_ROOT, ".tmp"), "phase10l5-browser-replay"),
  "--compare-with", path.join(REPO_ROOT, "docs/phase10l/evidence/phase10l5_natural_language_closure/browser_semantic_contract.json"),
], { ...common, MDI_PHASE10L5_BROWSERS: "chromium,firefox,webkit", MDI_PHASE10L5_EVIDENCE_PORT: "3223" });

run("Phase 10M-2 workspace shell", "node", ["test/workspace-shell-browser-evidence.mjs", "--validate-fixtures"]);
run("Phase 10M-2 workspace shell replay", "node", [
  "test/workspace-shell-browser-evidence.mjs",
  "--output-dir", path.join(process.env.RUNNER_TEMP || path.join(WEB_ROOT, ".tmp"), "phase10m2-browser-replay"),
  "--compare-with", path.join(REPO_ROOT, "docs/phase10m/evidence/phase10m2_workspace_shell/browser_semantic_contract.json"),
], { ...common, MDI_PHASE10M2_BROWSERS: "chromium,firefox,webkit", MDI_PHASE10M2_EVIDENCE_PORT: "3224" });

run("Phase 10M-3 canonical selection", "node", ["test/workspace-selection-browser-evidence.mjs", "--validate-fixtures"]);
run("Phase 10M-3 canonical selection replay", "node", [
  "test/workspace-selection-browser-evidence.mjs",
  "--output-dir", path.join(process.env.RUNNER_TEMP || path.join(WEB_ROOT, ".tmp"), "phase10m3-browser-replay"),
  "--compare-with", path.join(REPO_ROOT, "docs/phase10m/evidence/phase10m3_canonical_selection/browser_semantic_contract.json"),
], { ...common, MDI_PHASE10M3_BROWSERS: "chromium,firefox,webkit", MDI_PHASE10M3_EVIDENCE_PORT: "3225" });

const galleryCases = [
  ["Phase 10M-4 Artifact Gallery", "", "phase10m4-browser-replay", "3226"],
  ["Phase 10N-1 coordination", "--n1-coordination-only", "phase10n1-coordination-browser-replay", "3229"],
  ["Phase 10N-2 local environment", "--n2-local-environment-only", "phase10n2-local-environment-browser-replay", "3230"],
  ["Phase 10N-3 experimental XRD", "--n3-experimental-xrd-only", "phase10n3-experimental-xrd-browser-replay", "3231"],
  ["Phase 10N-4 trajectory analytics", "--n4-trajectory-analytics-only", "phase10n4-trajectory-analytics-browser-replay", "3232"],
  ["Phase 10N-5 electronic Band/DOS", "--n5-electronic-only", "phase10n5-electronic-browser-replay", "3233"],
  ["Phase 10N-6 professional closure", "--n6-professional-closure-only", "phase10n6-professional-browser-replay", "3234"],
];
for (const [label, selector, output, port] of galleryCases) {
  const flags = selector ? ["--validate-fixtures", selector] : ["--validate-fixtures"];
  run(`${label} fixture validation`, "node", ["test/workspace-artifact-gallery-browser-evidence.mjs", ...flags]);
  run(`${label} replay`, "xvfb-run", ["--auto-servernum", "node", "test/workspace-artifact-gallery-browser-evidence.mjs", ...(selector ? [selector] : []), "--output-dir", path.join(process.env.RUNNER_TEMP || path.join(WEB_ROOT, ".tmp"), output)], {
    ...common,
    MDI_PHASE10M4_BROWSERS: "chromium,firefox,webkit",
    MDI_PHASE10M4_EVIDENCE_PORT: port,
    MDI_PHASE10M4_HEADLESS: "false",
  });
}

run("Phase 10M-5 Report/Recipe", "node", ["test/workspace-report-recipe-browser-evidence.mjs", "--validate-fixtures"], { ...common, DEEPSEEK_KEY: "", MDI_PHASE10M5_BROWSERS: "chromium,firefox,webkit", MDI_PHASE10M5_EVIDENCE_PORT: "3227" });
run("Phase 10M-5 Report/Recipe replay", "node", ["test/workspace-report-recipe-browser-evidence.mjs", "--output-dir", path.join(process.env.RUNNER_TEMP || path.join(WEB_ROOT, ".tmp"), "phase10m5-browser-replay")], { ...common, DEEPSEEK_KEY: "", MDI_PHASE10M5_BROWSERS: "chromium,firefox,webkit", MDI_PHASE10M5_EVIDENCE_PORT: "3227" });
run("Phase 12-5 Report/Recipe experience", "node", ["test/workspace-report-recipe-browser-evidence.mjs", "--validate-fixtures"]);
run("Phase 12-5 Report/Recipe replay", "node", ["test/workspace-report-recipe-browser-evidence.mjs", "--output-dir", path.join(REPO_ROOT, "docs/phase12/evidence/phase12_5_report_recipe_experience")], { ...common, DEEPSEEK_KEY: "", MDI_PHASE10M5_BROWSERS: "chromium,firefox,webkit", MDI_PHASE10M5_EVIDENCE_PORT: "3239" });
run("Phase 12-5 evidence manifest", "python", ["scripts/generate_phase12_5_report_recipe_evidence.py"], common, REPO_ROOT);
run("Phase 10M-6 workspace recovery", "node", ["test/workspace-recovery-browser-evidence.mjs", "--validate-fixtures"]);
run("Phase 10M-6 workspace recovery replay", "node", ["test/workspace-recovery-browser-evidence.mjs", "--output-dir", path.join(process.env.RUNNER_TEMP || path.join(WEB_ROOT, ".tmp"), "phase10m6-browser-replay")], { ...common, DEEPSEEK_KEY: "", MDI_PHASE10M6_BROWSERS: "chromium,firefox,webkit", MDI_PHASE10M6_EVIDENCE_PORT: "3228" });
run("Phase 10M-7 workspace integration", "node", ["test/workspace-integration-browser-evidence.mjs", "--validate-fixtures"]);
run("Phase 10M-7 workspace integration replay", "node", ["test/workspace-integration-browser-evidence.mjs", "--output-dir", path.join(process.env.RUNNER_TEMP || path.join(WEB_ROOT, ".tmp"), "phase10m7-browser-replay")], { ...common, MDI_PLAYWRIGHT_MODULE: browserModule, MDI_PHASE10M7_EVIDENCE_PORT: "3229" });
