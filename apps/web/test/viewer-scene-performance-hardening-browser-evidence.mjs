import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");

const cases = [
  {
    script: "apps/web/test/viewer-scene-production-browser-evidence.mjs",
    markers: [
      "VIEWER_SCENE_PRODUCTION_MINIMAL_VIEWER_BROWSER_EVIDENCE_PASS",
      "VIEWER_SCENE_MOBILE_VIEWER_EVIDENCE_PASS",
      "VIEWER_SCENE_RENDERER_PERFORMANCE_EVIDENCE_PASS",
      "NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS",
    ],
  },
  {
    script: "apps/web/test/viewer-scene-periodic-browser-evidence.mjs",
    markers: [
      "VIEWER_SCENE_PERIODIC_PERFORMANCE_EVIDENCE_PASS",
      "NO_PERIODIC_VIEWER_EXTERNAL_NETWORK_REQUESTS",
    ],
  },
];

for (const item of cases) {
  const output = await run(item.script);
  for (const marker of item.markers) {
    if (!output.includes(marker)) throw new Error(`Missing browser evidence marker: ${marker}`);
  }
}

console.log("VIEWER_SCENE_PERFORMANCE_HARDENING_BROWSER_EVIDENCE_PASS");
console.log("VIEWER_SCENE_PERFORMANCE_LIFECYCLE_EVIDENCE_PASS");
console.log("NO_EXTERNAL_NETWORK_REQUESTS");

function run(script) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [path.join(repo, script)], { cwd: repo, stdio: ["ignore", "pipe", "pipe"] });
    let output = "";
    child.stdout.on("data", (chunk) => { output += chunk; process.stdout.write(chunk); });
    child.stderr.on("data", (chunk) => { output += chunk; process.stderr.write(chunk); });
    child.on("error", reject);
    child.on("exit", (code) => code === 0 ? resolve(output) : reject(new Error(`${script} exited ${code}`)));
  });
}
