import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { validatePhononBandDosBundle } from "./phononBandDosContract";

const root = resolve(__dirname, "../../../..");
const evidence = resolve(root, "docs/phase10h/evidence/phase10h3_combined_band_dos/artifacts");

function json(name: string) { return JSON.parse(readFileSync(resolve(evidence, name), "utf8")); }
function bundle() {
  return {
    combined: json("phonon_band_dos.json"),
    summary: json("phonon_band_dos_summary.json"),
    report: json("phonon_band_dos_compatibility_report.json"),
    plot: json("phonon_band_dos_plot.json"),
    table: json("phonon_band_dos_table.json"),
    manifest: json("phonon_band_dos_manifest.json"),
  };
}

describe("phononBandDosContract", () => {
  it("validates the real backend-generated combined artifact bundle", () => {
    expect(validatePhononBandDosBundle(bundle())).toEqual({valid: true, errors: []});
  });

  it("rejects source-reference and manifest hash drift", () => {
    const value = bundle();
    value.plot.source_refs.band.sha256 = "0".repeat(64);
    expect(validatePhononBandDosBundle(value).errors).toContain("PHONON_BAND_DOS_SOURCE_REFERENCE_MISMATCH");
    const mismatch = bundle();
    mismatch.manifest.artifacts[2].sha256 = "0".repeat(64);
    expect(validatePhononBandDosBundle(mismatch).errors).toContain("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID");
  });

  it("rejects executable, URL, and arbitrary compatibility metadata", () => {
    const executable = bundle();
    executable.combined.module = "https://example.invalid/phonon.js";
    const result = validatePhononBandDosBundle(executable);
    expect(result.errors).toContain("PHONON_BAND_DOS_EXTERNAL_REFERENCE_FORBIDDEN");
    const arbitrary = bundle();
    arbitrary.report.checks[0].result_code = "javascript:alert(1)";
    expect(validatePhononBandDosBundle(arbitrary).errors).toContain("PHONON_BAND_DOS_COMPATIBILITY_REPORT_INVALID");
  });

  it("rejects plot budget and shared-axis contract drift", () => {
    const value = bundle();
    value.plot.display.numeric_values = 1_000_001;
    value.plot.shared_frequency_axis.unit = "millielectronvolt";
    expect(validatePhononBandDosBundle(value).errors).toContain("PHONON_BAND_DOS_PLOT_INVALID");
  });
});
