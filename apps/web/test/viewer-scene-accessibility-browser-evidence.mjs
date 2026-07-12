import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const script = path.join(root, "apps/web/test/viewer-scene-production-browser-evidence.mjs");
const required = [
  "VIEWER_SCENE_PRODUCTION_MINIMAL_VIEWER_BROWSER_EVIDENCE_PASS",
  "VIEWER_SCENE_MOBILE_VIEWER_EVIDENCE_PASS",
  "VIEWER_SCENE_ACCESSIBILITY_EVIDENCE_PASS",
  "VIEWER_SCENE_ACCESSIBILITY_MOBILE_CROSS_BROWSER_EVIDENCE_PASS",
  "NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS",
];

const output = await new Promise((resolve, reject) => {
  const child = spawn(process.execPath, [script], { cwd: root, stdio: ["ignore", "pipe", "pipe"] });
  let text = "";
  child.stdout.on("data", (chunk) => { text += chunk; process.stdout.write(chunk); });
  child.stderr.on("data", (chunk) => { text += chunk; process.stderr.write(chunk); });
  child.on("error", reject);
  child.on("exit", (code) => code === 0 ? resolve(text) : reject(new Error(`production browser runner exited ${code}`)));
});

for (const marker of required) if (!output.includes(marker)) throw new Error(`Missing marker: ${marker}`);
console.log("VIEWER_SCENE_ACCESSIBILITY_KEYBOARD_EVIDENCE_PASS");
console.log("VIEWER_SCENE_MOBILE_TOUCH_EVIDENCE_PASS");
console.log("VIEWER_SCENE_CROSS_BROWSER_ACCESSIBILITY_EVIDENCE_PASS");
console.log("NO_EXTERNAL_NETWORK_REQUESTS");
