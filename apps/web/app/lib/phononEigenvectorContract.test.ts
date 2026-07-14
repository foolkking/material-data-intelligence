import { readFileSync } from "node:fs";
import path from "node:path";

import { describe, expect, it } from "vitest";

import { validatePhononEigenvector, validatePhononEigenvectorBundle, validatePhononModeRef } from "./phononEigenvectorContract";

const fixture = JSON.parse(readFileSync(path.resolve(process.cwd(), "../../docs/phase10h/fixtures/phonon_eigenvector_v1/valid_bundle.json"), "utf8"));

describe("phonon eigenvector contract", () => {
  it("independently validates the Python-generated contract bundle", () => {
    expect(validatePhononModeRef(fixture.mode)).toMatchObject({valid: true});
    expect(validatePhononEigenvector(fixture.eigenvector)).toMatchObject({valid: true, atomCount: 2});
    expect(validatePhononEigenvectorBundle(fixture)).toMatchObject({valid: true, atomCount: 2, modeCount: 2});
  });

  it("rejects complex shape, norm, phase, mass, and order drift", () => {
    const cases = [
      (value: any) => { value.eigenvector.eigenvectors[0].real = [1, 0]; },
      (value: any) => { value.eigenvector.eigenvectors[0].real[0] = 2; },
      (value: any) => { value.eigenvector.eigenvectors[0].imag[0] = 0.5; },
      (value: any) => { value.eigenvector.atomic_masses.values[0] = 0; },
      (value: any) => { value.set.modes.reverse(); },
    ];
    for (const mutate of cases) { const value = structuredClone(fixture); mutate(value); expect(validatePhononEigenvectorBundle(value).valid).toBe(false); }
  });

  it("rejects stale mode binding and unsafe metadata", () => {
    const stale = structuredClone(fixture); stale.mode.band_artifact.sha256 = "f".repeat(64); stale.eigenvector.mode = stale.mode;
    expect(validatePhononEigenvectorBundle(stale).valid).toBe(false);
    const unsafe = structuredClone(fixture); unsafe.eigenvector.provenance.url = "https://example.invalid/vector";
    expect(validatePhononEigenvectorBundle(unsafe).errors).toContain("PHONON_EIGENVECTOR_EXTERNAL_REFERENCE_FORBIDDEN");
  });

  it("rejects unknown executable fields and oversized mode sets", () => {
    const callback = structuredClone(fixture); callback.eigenvector.callback = "alert(1)";
    expect(validatePhononEigenvector(callback.eigenvector).valid).toBe(false);
    const over = structuredClone(fixture); over.set.mode_count = 4097; over.set.modes = Array.from({length: 4097}, () => fixture.eigenvector);
    expect(validatePhononEigenvectorBundle(over).errors).toContain("PHONON_EIGENVECTOR_SET_INVALID");
  });
});
