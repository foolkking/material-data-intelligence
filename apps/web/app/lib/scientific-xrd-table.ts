type JsonRecord = Record<string, unknown>;
const asRecord = (value: unknown): JsonRecord | null => value && typeof value === "object" && !Array.isArray(value) ? value as JsonRecord : null;

/** Read saved peak rows without sorting, rounding, calculating or inferring missing values. */
export function savedXrdTableRows(payload: unknown): JsonRecord[] | null {
  const record = asRecord(payload);
  if (record?.schema_version !== "phase10e4.xrd_pattern.v1") return null;
  const pattern = asRecord(record.pattern);
  const peaks = Array.isArray(pattern?.peaks) ? pattern.peaks.map(asRecord).filter((peak): peak is JsonRecord => Boolean(peak)) : [];
  const multipleStructures = new Set(peaks.map(peak => peak.structureId).filter(Boolean)).size > 1;
  return peaks.map(peak => {
    const hkls = Array.isArray(peak.hkls) ? peak.hkls.map(value => {
      const hkl = asRecord(value)?.hkl;
      return Array.isArray(hkl) ? `(${hkl.join(" ")})` : "";
    }).filter(Boolean).join(" · ") : "";
    return {
      ...(multipleStructures ? { structureId: peak.structureId } : {}),
      "2θ (°)": peak.two_theta_deg,
      "相对强度": peak.intensity,
      "晶面 hkl": hkls || "—",
      "晶面间距 (Å)": peak.d_spacing_angstrom,
    };
  });
}
