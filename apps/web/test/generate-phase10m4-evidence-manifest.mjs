import { createHash } from "node:crypto";
import { mkdir, readFile, readdir, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const EVIDENCE = path.join(ROOT, "docs", "phase10m", "evidence", "phase10m4_artifact_gallery_viewers");

async function main() {
  await mkdir(EVIDENCE, { recursive: true });
  const files = (await walk(EVIDENCE)).filter((item) => item !== "file_manifest.json").sort();
  const entries = [];
  for (const relative of files) {
    const bytes = await readFile(path.join(EVIDENCE, relative));
    const textLike = /\.(?:json|txt|md)$/iu.test(relative);
    const normalized = textLike ? Buffer.from(bytes.toString("utf8").replace(/\r\n/g, "\n"), "utf8") : bytes;
    entries.push({
      path: relative.replaceAll("\\", "/"),
      bytes: bytes.length,
      hashMode: textLike ? "lf_normalized_text" : "raw_binary",
      sha256: createHash("sha256").update(normalized).digest("hex"),
    });
  }
  await writeFile(path.join(EVIDENCE, "file_manifest.json"), `${JSON.stringify({ schemaVersion: "phase10m4.evidence_manifest.v1", rule: "LF-normalized UTF-8 text; raw PNG bytes", entries }, null, 2)}\n`, "utf8");
  console.log(`PHASE10M4_EVIDENCE_MANIFEST_PASS files=${entries.length}`);
}

async function walk(directory, prefix = "") {
  const output = [];
  for (const name of await readdir(directory)) {
    const relative = path.join(prefix, name);
    const information = await stat(path.join(directory, name));
    if (information.isDirectory()) output.push(...await walk(path.join(directory, name), relative));
    else output.push(relative);
  }
  return output;
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
