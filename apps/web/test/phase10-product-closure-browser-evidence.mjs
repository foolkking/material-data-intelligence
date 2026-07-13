import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const evidence = "docs/phase10/evidence/phase10_closure_regression_pack";
const browser = spawn(process.execPath, ["apps/web/test/viewer-scene-production-browser-evidence.mjs"], {
  cwd: root,
  env: {
    ...process.env,
    MDI_FORMAL_VIEWER_REGISTRATION: "1",
    MDI_PRODUCTION_VIEWER_EVIDENCE_DIR: evidence,
    MDI_VIEWER_PRODUCTION_EVIDENCE_PORT: process.env.MDI_PHASE10_CLOSURE_PORT || "3062",
  },
  stdio: "inherit",
});

browser.on("exit", (code) => {
  if (code !== 0) {
    process.exit(code ?? 1);
    return;
  }
  const generator = spawn("uv", ["run", "python", "apps/web/test/generate-phase10-closure-evidence.py", evidence], {
    cwd: root,
    env: { ...process.env, PYTHONIOENCODING: "utf-8" },
    stdio: "inherit",
  });
  generator.on("exit", (generatorCode) => {
    if (generatorCode === 0) console.log("PHASE10_PRODUCT_CLOSURE_BROWSER_PASS");
    process.exit(generatorCode ?? 1);
  });
  generator.on("error", (error) => {
    console.error(error);
    process.exit(1);
  });
});
browser.on("error", (error) => {
  console.error(error);
  process.exit(1);
});
