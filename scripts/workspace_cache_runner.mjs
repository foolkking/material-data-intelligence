import { mkdirSync } from "node:fs";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
const repositoryRoot = path.resolve(scriptDirectory, "..");
const webRoot = path.join(repositoryRoot, "apps", "web");

class WorkspaceCacheError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

function resolveInside(base, value, label) {
  const resolved = path.resolve(base, value);
  const relative = path.relative(repositoryRoot, resolved);
  if (
    relative === ".." ||
    relative.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relative)
  ) {
    throw new WorkspaceCacheError(
      "MDI_WORKSPACE_CACHE_OUTSIDE_REPOSITORY",
      `${label} must resolve inside the repository workspace.`,
    );
  }
  return resolved;
}

function cacheEnvironment(sourceEnvironment = process.env) {
  const cacheRoot = resolveInside(
    repositoryRoot,
    sourceEnvironment.MDI_WORKSPACE_CACHE_DIR || ".cache/tooling",
    "MDI_WORKSPACE_CACHE_DIR",
  );
  const npmCache = resolveInside(
    repositoryRoot,
    sourceEnvironment.MDI_NPM_CACHE_DIR || path.join(cacheRoot, "npm"),
    "MDI_NPM_CACHE_DIR",
  );
  const playwrightCache = resolveInside(
    repositoryRoot,
    sourceEnvironment.MDI_PLAYWRIGHT_CACHE_DIR ||
      path.join(cacheRoot, "playwright"),
    "MDI_PLAYWRIGHT_CACHE_DIR",
  );
  const temporaryRoot = resolveInside(
    repositoryRoot,
    sourceEnvironment.MDI_TOOL_TEMP_DIR || path.join(cacheRoot, "tmp"),
    "MDI_TOOL_TEMP_DIR",
  );
  const nextDist = resolveInside(
    webRoot,
    sourceEnvironment.MDI_NEXT_DIST_DIR || ".cache/next",
    "MDI_NEXT_DIST_DIR",
  );
  const nextRelative = path.relative(webRoot, nextDist);
  if (
    nextRelative === ".." ||
    nextRelative.startsWith(`..${path.sep}`) ||
    path.isAbsolute(nextRelative)
  ) {
    throw new WorkspaceCacheError(
      "MDI_NEXT_CACHE_OUTSIDE_WEB_ROOT",
      "MDI_NEXT_DIST_DIR must resolve inside apps/web.",
    );
  }
  for (const directory of [
    cacheRoot,
    npmCache,
    playwrightCache,
    temporaryRoot,
    nextDist,
  ]) {
    mkdirSync(directory, { recursive: true });
  }
  return {
    ...sourceEnvironment,
    NPM_CONFIG_CACHE: npmCache,
    PLAYWRIGHT_BROWSERS_PATH: playwrightCache,
    MDI_NEXT_DIST_DIR: nextRelative || ".cache/next",
    TMPDIR: temporaryRoot,
    TEMP: temporaryRoot,
    TMP: temporaryRoot,
  };
}

function commandFor(tool, arguments_) {
  const entries = {
    next: path.join(webRoot, "node_modules", "next", "dist", "bin", "next"),
    playwright: path.join(
      webRoot,
      "node_modules",
      "playwright",
      "cli.js",
    ),
    tsc: path.join(webRoot, "node_modules", "typescript", "bin", "tsc"),
    vitest: path.join(webRoot, "node_modules", "vitest", "vitest.mjs"),
  };
  if (tool === "node") {
    return [process.execPath, arguments_];
  }
  const entry = entries[tool];
  if (!entry) {
    throw new WorkspaceCacheError(
      "MDI_WORKSPACE_CACHE_TOOL_UNSUPPORTED",
      `Unsupported workspace-cache tool: ${tool}`,
    );
  }
  return [process.execPath, [entry, ...arguments_]];
}

function main() {
  const [tool, ...arguments_] = process.argv.slice(2);
  if (!tool) {
    throw new WorkspaceCacheError(
      "MDI_WORKSPACE_CACHE_TOOL_REQUIRED",
      "A bounded tool name is required.",
    );
  }
  const [executable, childArguments] = commandFor(tool, arguments_);
  const child = spawn(executable, childArguments, {
    cwd: webRoot,
    env: cacheEnvironment(),
    stdio: "inherit",
  });
  for (const signal of ["SIGINT", "SIGTERM"]) {
    process.on(signal, () => child.kill(signal));
  }
  child.on("error", (error) => {
    console.error(
      JSON.stringify({
        code: "MDI_WORKSPACE_CACHE_CHILD_START_FAILED",
        message: error.message,
      }),
    );
    process.exitCode = 70;
  });
  child.on("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }
    process.exitCode = code ?? 1;
  });
}

try {
  main();
} catch (error) {
  const code =
    error instanceof WorkspaceCacheError
      ? error.code
      : "MDI_WORKSPACE_CACHE_CONFIGURATION_INVALID";
  console.error(JSON.stringify({ code, message: error.message }));
  process.exitCode = 64;
}
