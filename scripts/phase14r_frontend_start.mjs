import { fileURLToPath } from "node:url";
import path from "node:path";
import { execFileSync, spawn } from "node:child_process";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.resolve(scriptDirectory, "..", "apps", "web");
const repositoryRoot = path.resolve(scriptDirectory, "..");
const port = Number(process.env.MDI_FRONTEND_PORT || 3014);
if (!Number.isInteger(port) || port < 1024 || port > 65535) {
  throw new Error("MDI_FRONTEND_PORT must be an integer between 1024 and 65535");
}

const environment = {
  ...process.env,
  MDI_RELEASE_SHA:
    process.env.MDI_RELEASE_SHA ||
    execFileSync("git", ["rev-parse", "HEAD"], {
      cwd: repositoryRoot,
      encoding: "utf8",
    }).trim(),
  MDI_NEXT_DIST_DIR:
    process.env.MDI_NEXT_DIST_DIR || ".cache/next-production",
  MDI_API_PROXY_TARGET:
    process.env.MDI_API_PROXY_TARGET || "http://127.0.0.1:8005",
};
const nextBin = path.resolve(
  webRoot,
  "node_modules",
  "next",
  "dist",
  "bin",
  "next",
);
const child = spawn(process.execPath, [nextBin, "start", "-H", "127.0.0.1", "-p", String(port)], {
  cwd: webRoot,
  env: environment,
  stdio: "inherit",
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 1);
});
