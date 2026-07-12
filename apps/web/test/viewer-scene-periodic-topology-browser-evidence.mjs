import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const child = spawn(process.execPath, ["apps/web/test/viewer-scene-inspection-browser-evidence.mjs"], {
  cwd: root,
  env: {
    ...process.env,
    MDI_TOPOLOGY_EVIDENCE: "1",
    MDI_INSPECTION_EVIDENCE_DIR: "docs/phase10f/evidence/phase10f18_periodic_bond_topology",
    MDI_VIEWER_INSPECTION_EVIDENCE_PORT: process.env.MDI_VIEWER_TOPOLOGY_EVIDENCE_PORT || "3053",
  },
  stdio: "inherit",
});

child.on("exit", (code) => process.exit(code ?? 1));
child.on("error", (error) => { console.error(error); process.exit(1); });
