import { execFileSync } from "node:child_process";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const browserEvidence = path.join(
  root,
  "_qualification/evidence/phase_d/attempt_09_r1_6_reseal/browser/BROWSER_READINESS_SMOKE.json",
);
const packageRoot = path.join(root, "_qualification/work/phase_bc_r1_6/authority_package");
const output = path.join(
  root,
  "_qualification/evidence/phase_d/attempt_09_r1_6_reseal/browser/POST_RESTART_STORAGE_DURABILITY.json",
);
const sourceFiles = {
  "Q-TABLE-001": ["03_Q-TABLE-001/UPLOAD_materials_table.csv"],
  "Q-ARCHIVE-001": ["16_Q-ARCHIVE-001/UPLOAD_materials_table.zip"],
  "Q-XRD-001": [
    "10_Q-XRD-001/UPLOAD_experimental_xrd.json",
    "10_Q-XRD-001/UPLOAD_structure_COD_4317043_hydroxyapatite.cif",
  ],
  "Q-ELECTRONIC-001": [
    "15_Q-ELECTRONIC-001/UPLOAD_electronic_dos.json",
    "15_Q-ELECTRONIC-001/UPLOAD_electronic_band.json",
  ],
};

function assertSafeStorageKey(key) {
  if (!/^[A-Za-z0-9._/-]+$/u.test(key) || key.includes("..")) {
    throw new Error(`Unsafe object-storage key: ${key}`);
  }
}

function readObject(key) {
  assertSafeStorageKey(key);
  return execFileSync(
    "docker",
    ["exec", "mdi-phase-d-attempt4-minio-1", "mc", "cat", `local/mdi-artifacts/${key}`],
    { maxBuffer: 64 * 1024 * 1024 },
  );
}

const evidence = JSON.parse(await readFile(browserEvidence, "utf8"));
const observations = [];
for (const observation of evidence.observations) {
  const sourcePaths = sourceFiles[observation.caseId];
  if (!sourcePaths) continue;
  const sources = new Map();
  for (const relativePath of sourcePaths) {
    const absolutePath = path.join(packageRoot, relativePath);
    sources.set(path.basename(absolutePath), await readFile(absolutePath));
  }
  const files = observation.sanitizedCompletion.inputTransport.files.map((file) => {
    const source = sources.get(file.fileName);
    if (!source) throw new Error(`${observation.caseId}: no source for ${file.fileName}`);
    const objectBytes = readObject(file.storageKey);
    return {
      fileName: file.fileName,
      sourceByteSize: source.length,
      persistedByteSize: objectBytes.length,
      byteForByteEqual: Buffer.compare(source, objectBytes) === 0,
    };
  });
  observations.push({
    caseId: observation.caseId,
    datasetId: observation.datasetId,
    files,
    persistedResourcesByteStable: files.every((file) => file.byteForByteEqual),
  });
}

const result = {
  schemaVersion: "PhaseDR16PostRestartStorageDurability/1.0",
  integrityAuthority: "DIRECT_CONTENT_AND_RUNTIME_VALIDATION",
  storageContainer: "mdi-phase-d-attempt4-minio-1",
  observations,
  gates: {
    allDeclaredResourcesPersisted: observations.length === 4,
    allPersistedResourcesByteStable: observations.every((item) => item.persistedResourcesByteStable),
  },
};
await mkdir(path.dirname(output), { recursive: true });
await writeFile(output, `${JSON.stringify(result, null, 2)}\n`, "utf8");
console.log(JSON.stringify(result, null, 2));
