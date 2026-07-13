import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

import { validatePhononBandReference, validatePhononDosReference } from "../app/lib/phononContract";

const root = resolve(process.cwd(), "../..");
const fixture = (name: string) => resolve(root, "docs/phase10h/fixtures/phonon_contract", name);
const evidenceFile = (name: string) => resolve(root, "docs/phase10h/evidence/phase10h_phonon_contract", name);
const output = resolve(root, "docs/phase10h/evidence/phase10h_phonon_contract/frontend_backend_validation_comparison.json");

async function load(name: string): Promise<unknown> {
  return JSON.parse(await readFile(fixture(name), "utf8"));
}

async function loadEvidence(name: string): Promise<any> {
  return JSON.parse(await readFile(evidenceFile(name), "utf8"));
}

const backendInvalid = await loadEvidence("invalid_fixture_results.json");
const backendByCase: Record<string, {valid: boolean; errors: string[]}> = {
  stable_band: (await loadEvidence("stable_band_fixture_result.json")).validation,
  imaginary_band: (await loadEvidence("imaginary_band_fixture_result.json")).validation,
  discontinuous_band: (await loadEvidence("discontinuous_path_result.json")).validation,
  projected_dos: (await loadEvidence("projected_dos_result.json")).validation,
  invalid_branch_count: backendInvalid.branch_count,
  invalid_dos_grid: backendInvalid.dos_grid,
};

const cases = [
  {name: "stable_band", file: "stable_band.json", kind: "band", expected: true},
  {name: "imaginary_band", file: "imaginary_band.json", kind: "band", expected: true},
  {name: "discontinuous_band", file: "discontinuous_band.json", kind: "band", expected: true},
  {name: "projected_dos", file: "projected_dos.json", kind: "dos", expected: true},
  {name: "invalid_branch_count", file: "invalid_branch_count.json", kind: "band", expected: false},
  {name: "invalid_dos_grid", file: "invalid_dos_grid.json", kind: "dos", expected: false},
];

const results = [];
for (const item of cases) {
  const payload = await load(item.file);
  const result = item.kind === "band" ? validatePhononBandReference(payload) : validatePhononDosReference(payload);
  const backend = backendByCase[item.name];
  if (result.valid !== item.expected) throw new Error(`${item.name}: unexpected frontend validation result ${JSON.stringify(result)}`);
  if (backend.valid !== item.expected || backend.valid !== result.valid) throw new Error(`${item.name}: frontend/backend validity mismatch`);
  results.push({name: item.name, expected_valid: item.expected, backend_valid: backend.valid, backend_errors: backend.errors, frontend_valid: result.valid, frontend_errors: result.errors});
}

const stable = await readFile(fixture("stable_band.json"));
const evidence = {
  result: "PASS",
  implementation: "independent TypeScript reference validator",
  canonical_fixture_sha256: createHash("sha256").update(stable).digest("hex"),
  cases: results,
  enum_parity: {
    band_schema: "phase10h.phonon_band.v1",
    dos_schema: "phase10h.phonon_dos.v1",
    frequency_unit: "terahertz",
    imaginary_encoding: "negative_real",
  },
};
await writeFile(output, `${JSON.stringify(evidence, null, 2)}\n`, {encoding: "utf8"});
console.log("PHONON_CONTRACT_CROSS_LANGUAGE_EVIDENCE_PASS");
