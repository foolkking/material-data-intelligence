import { describe, expect, it } from "vitest";
import type { Artifact, GroundedScientificInterpretation, ScientificEvidenceItem } from "./planner-api";
import { compileReportPresentation, compileScientificPresentation, isSafePresentationBlock } from "./scientific-presentation";
import type { ScientificReportView } from "./scientific-report-api";

const source = { objectId: "structure-a", versionId: "version-v1", objectType: "Structure", displayName: "NaCl" };
const evidence: ScientificEvidenceItem = {
  schemaVersion: "1.0",
  evidenceItemId: "fact-band-gap",
  semanticRole: "band_gap",
  evidenceKind: "SCALAR",
  subjectId: "mat-2",
  displayValue: "5.6",
  unit: "eV",
  sourceArtifactId: "dataset-table",
  sourceArtifactChecksum: "sha256:dataset",
  artifactContract: "dataset.table",
  artifactContractVersion: "1.0",
  sourceToolId: "data.materials_explorer",
  sourceToolVersion: "1.0",
  fieldLocator: { fieldId: "band_gap", entityId: "mat-2" },
  warnings: [],
  limitations: [],
};

const interpretation = {
  interpretationId: "interpretation-1",
  claims: [{
    claimId: "claim-1",
    claimType: "OBSERVATION",
    subjectEvidenceIds: ["fact-band-gap"],
    supportingEvidenceIds: [],
    limitingEvidenceIds: [],
    contradictingEvidenceIds: [],
    renderedText: "样本 mat-2 的带隙为 5.6 eV。",
    confidenceClass: "DIRECT",
    groundingStatus: "GROUNDED",
  }],
  globalWarnings: [],
  globalLimitations: ["结论仅适用于所选样本。"],
} as unknown as GroundedScientificInterpretation;

describe("scientific presentation compiler", () => {
  it("preserves authoritative numeric values, units, evidence, and exact sources", () => {
    const presentation = compileScientificPresentation({
      interpretation,
      evidence: [evidence],
      artifacts: [{ id: "dataset-table", type: "table_json", name: "materials_table.json" } as Artifact],
      resultId: "result-1",
      sourceObjectRefs: [source],
    });

    expect(presentation.exactSourceRefs).toEqual([source]);
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "metric",
      value: "5.6",
      unit: "eV",
      source: expect.objectContaining({ evidenceId: "fact-band-gap", versionId: "version-v1" }),
    }));
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "finding",
      evidenceIds: ["fact-band-gap"],
    }));
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "evidence_reference",
      source: expect.objectContaining({ interpretationId: "interpretation-1", evidenceId: "fact-band-gap" }),
    }));
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "table",
      artifactId: "dataset-table",
      source: expect.objectContaining({ versionId: "version-v1" }),
    }));
  });

  it("retains bounded artifact provenance for real content links", () => {
    const presentation = compileScientificPresentation({
      resultId: "result-1",
      artifacts: [{ id: "artifact-1", jobId: "job-1", type: "table_json", name: "table.json" } as Artifact],
      sourceObjectRefs: [source],
    });
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "table",
      source: expect.objectContaining({ artifactId: "artifact-1", jobId: "job-1" }),
    }));
  });

  it("does not promote ungrounded claims into a finding", () => {
    const unsafeInterpretation = {
      ...interpretation,
      claims: [{ ...interpretation.claims[0], claimId: "unsupported", renderedText: "未被证据支持的 99 eV 声明。", groundingStatus: "REJECTED" }],
    } as GroundedScientificInterpretation;
    const presentation = compileScientificPresentation({ interpretation: unsafeInterpretation, evidence: [evidence] });
    expect(presentation.blocks.some((block) => block.type === "finding")).toBe(false);
  });

  it("maps exact ScientificResult facts without recalculating their values or units", () => {
    const presentation = compileScientificPresentation({
      resultId: "result-1",
      facts: [{
        factId: "dataset.band_gap.mat-2",
        predicate: "dataset.band_gap",
        subjectRef: "mat-2",
        value: 5.6,
        unit: "eV",
        source: { artifactId: "dataset-table", scientificObjectRef: { objectId: "dataset-a", versionId: "dataset-v1" } },
      }],
    });
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "metric",
      value: "5.6",
      unit: "eV",
      source: expect.objectContaining({ factId: "dataset.band_gap.mat-2", versionId: "dataset-v1" }),
    }));
  });

  it("prioritizes the immutable selected Dataset sample over an unrelated first table row", () => {
    const presentation = compileScientificPresentation({
      facts: [
        {
          factId: "dataset.sample.mat-1",
          predicate: "dataset.sample.band_gap",
          subjectRef: "dataset-version:mat-1",
          value: 1.1,
          unit: "eV",
        },
        {
          factId: "dataset.sample.mat-2",
          predicate: "dataset.sample.band_gap",
          subjectRef: "dataset-version:mat-2",
          value: 5.6,
          unit: "eV",
        },
      ],
      scientificSelections: [{
        selectionType: "DATASET_SAMPLE",
        semanticLocator: { sample_ref: "mat-2" },
      }],
    });
    const factMetrics = presentation.blocks.filter((block) => block.type === "metric" && block.source.factId);
    expect(factMetrics[0]).toEqual(expect.objectContaining({
      value: "5.6",
      source: expect.objectContaining({ factId: "dataset.sample.mat-2" }),
    }));
    expect(factMetrics[1]).toEqual(expect.objectContaining({
      value: "1.1",
      source: expect.objectContaining({ factId: "dataset.sample.mat-1" }),
    }));
  });

  it("keeps historical presentation exact rather than substituting current sources", () => {
    const presentation = compileScientificPresentation({
      interpretation,
      sourceObjectRefs: [source],
      relevance: "STALE",
    });
    expect(presentation.historicalNotice).toContain("不会替换");
    expect(presentation.exactSourceRefs[0].versionId).toBe("version-v1");
  });

  it("rejects executable presentation labels", () => {
    expect(isSafePresentationBlock({
      id: "unsafe",
      type: "narrative",
      text: "<script>alert(1)</script>",
      source: {},
    })).toBe(false);
  });

  it("maps immutable report fields without inventing facts", () => {
    const view = {
      report_id: "report-1",
      snapshot_id: "snapshot-1",
      project_id: "project-1",
      research_turn_id: "turn-1",
      scientific_result_snapshot_id: "result-1",
      scientific_interpretation_id: "interpretation-1",
      title: "NaCl report",
      relevance_at_generation: "CURRENT",
      current_effective_relevance: "STALE",
      grounding_status: "VALID",
      scientific_context: "exact source",
      finding_count: 1,
      figure_count: 1,
      source_fingerprint: "fingerprint",
      created_at: "2026-08-26T00:00:00Z",
      viewer_sources: [{ source_ref: "source-1", object_id: "structure-a", version_id: "version-v1", object_type: "Structure", display_name: "NaCl", is_current_version: false }],
      report: {
        contract_version: "1.0",
        title: "NaCl report",
        research_question: "What is the structure?",
        summary: "Grounded snapshot.",
        main_findings: [{ statement: "Coordinations were computed.", finding_refs: ["finding-1"], fact_refs: ["fact-1"], evidence_refs: ["evidence-1"] }],
        primary_figures: [{ figure_ref: "artifact-1", caption: "Structure figure", fact_refs: [], evidence_refs: ["evidence-1"] }],
        supporting_results: [],
        method_summary: "Method.",
        limitations: [{ statement: "Snapshot scope.", source_refs: ["source-1"] }],
        data_sources: ["source-1"],
        evidence_refs: ["evidence-1"],
        reproducibility_summary: "Reproducible.",
        omitted_supporting_items: [],
      },
    } satisfies ScientificReportView;
    const presentation = compileReportPresentation(view);
    expect(presentation.historicalNotice).toContain("不会静默替换");
    expect(presentation.exactSourceRefs[0].versionId).toBe("version-v1");
    expect(presentation.blocks).toContainEqual(expect.objectContaining({ type: "finding", evidenceIds: expect.arrayContaining(["evidence-1"]) }));
  });

  it("retains ToolCall provenance when projecting a Result fact", () => {
    const presentation = compileScientificPresentation({
      resultId: "result-tool",
      facts: [{
        factId: "coordination.count",
        predicate: "coordination.count",
        subjectRef: "structure-a",
        value: 4,
        unit: "count",
        source: { toolCallId: "tool-call-crystalnn" },
      }],
      sourceObjectRefs: [source],
    });
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "metric",
      source: expect.objectContaining({ toolCallId: "tool-call-crystalnn" }),
    }));
  });
});
