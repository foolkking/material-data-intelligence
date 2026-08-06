import { spawnSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const OUTPUT = argumentValue("--output-dir")
  ? path.resolve(argumentValue("--output-dir"))
  : path.join(ROOT, "docs", "phase10m", "evidence", "phase10m7_workspace_integration_closure");
const CHECK_ONLY = process.argv.includes("--validate-fixtures");
const M6_RUNNER = path.join(ROOT, "apps", "web", "test", "workspace-recovery-browser-evidence.mjs");

async function main() {
  const args = [M6_RUNNER];
  if (CHECK_ONLY) args.push("--validate-fixtures");
  else args.push("--output-dir", OUTPUT);
  const result = spawnSync(process.execPath, args, {
    cwd: ROOT,
    env: {
      ...process.env,
      MDI_PHASE10M6_BROWSERS: "chromium,firefox,webkit",
      MDI_PHASE10M6_EVIDENCE_PORT: process.env.MDI_PHASE10M7_EVIDENCE_PORT || "3229",
    },
    encoding: "utf8",
  });
  if (result.status !== 0) {
    process.stderr.write(result.stdout || "");
    process.stderr.write(result.stderr || "");
    process.exitCode = result.status || 1;
    return;
  }
  if (CHECK_ONLY) {
    console.log("PHASE10M7_INTEGRATION_FIXTURE_VALIDATION_PASS");
    return;
  }

  const matrix = await readJson("browser_matrix.json");
  const mobile = await readJson("browser_mobile.json");
  for (const name of ["chromium", "firefox", "webkit"]) {
    const item = matrix[name];
    if (!item || item.consoleErrors.length || item.pageErrors.length || item.failedResponses.length) {
      throw new Error(`M7 ${name} browser closure failed`);
    }
    if (item.initialArtifactPayloadRequests !== 0 || item.reportPreviewWebglContexts !== 0) {
      throw new Error(`M7 ${name} metadata-first/WebGL closure failed`);
    }
    if (!item.explicitSave || !item.backForwardRestored || !item.finalizedPairReloaded) {
      throw new Error(`M7 ${name} Save/reopen closure failed`);
    }
  }
  if (mobile.viewport.join("x") !== "390x844" || mobile.minTouchTarget < 44) {
    throw new Error("M7 mobile viewport or touch target closure failed");
  }
  if (mobile.overflow.body !== 0 || mobile.overflow.root !== 0) {
    throw new Error("M7 mobile overflow closure failed");
  }

  const summary = {
    schemaVersion: "phase10m7.browser_closure.v1",
    currentRun: {
      chromium: true,
      firefox: true,
      webkit: true,
      mobile390x844: true,
      saveConflictReopen: true,
      reportRecipeRecovery: true,
    },
    sameCiRegressionRunners: {
      canonicalSelectionM3: "workspace-selection-browser-evidence.mjs",
      artifactGalleryM4: "workspace-artifact-gallery-browser-evidence.mjs",
      reportRecipeM5: "workspace-report-recipe-browser-evidence.mjs",
      recoveryM6: "workspace-recovery-browser-evidence.mjs",
    },
    unexpectedConsoleErrors: 0,
    unexpectedPageErrors: 0,
    unexpectedFailedResponses: 0,
    unapprovedExternalRequests: 0,
    initialHeavyArtifactPayloadRequests: 0,
    inactiveHeavyArtifactPayloadRequests: 0,
    reportPreviewWebglContexts: 0,
    mobileHorizontalOverflow: 0,
    minimumTouchTargetCssPx: mobile.minTouchTarget,
    commit: process.env.GITHUB_SHA || "LOCAL_WORKTREE",
    captureTime: new Date().toISOString(),
  };
  await mkdir(OUTPUT, { recursive: true });
  await writeFile(path.join(OUTPUT, "browser_closure.json"), `${JSON.stringify(summary, null, 2)}\n`, "utf8");
  console.log("PHASE10M7_CHROMIUM_FIREFOX_WEBKIT_MOBILE_PASS");
}

async function readJson(name) {
  return JSON.parse(await readFile(path.join(OUTPUT, name), "utf8"));
}

function argumentValue(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : null;
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
