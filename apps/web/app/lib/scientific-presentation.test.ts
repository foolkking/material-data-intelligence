import { describe, expect, it } from "vitest";
import type { Artifact, GroundedScientificInterpretation, ScientificEvidenceItem } from "./planner-api";
import { compileReportPresentation, compileScientificPresentation, formatPresentationMetricValue, formatScientificNarrativeNumbers, isSafePresentationBlock, presentationLimitationText, presentationMetricTitle, presentationScientificText } from "./scientific-presentation";
import type { ScientificReportView } from "./scientific-report-api";
import { scientificNarrativeText } from "./scientific-narrative-text";
import { presentationMetricUnit } from "./scientific-presentation";

it("displays trajectory quantities without changing their saved values or identifiers", () => {
  expect(presentationMetricTitle("trajectory.diffusion_fit_duration")).toBe("拟合窗口时长");
  expect(presentationMetricUnit("picosecond")).toBe("ps");
  expect(presentationMetricUnit("angstrom^2/picosecond")).toBe("Å²/ps");
  expect(presentationMetricUnit("unknown/unit")).toBe("unknown/unit");
  expect(scientificNarrativeText("INSUFFICIENT_DURATION")).toBe("拟合窗口时长不足");
  expect(scientificNarrativeText("`INSUFFICIENT_DURATION`；/result/INSUFFICIENT_DURATION")).toBe("`INSUFFICIENT_DURATION`；/result/INSUFFICIENT_DURATION");
});

const source = { objectId: "structure-a", versionId: "version-v1", objectType: "Structure", displayName: "NaCl" };

it("keeps same-named figures separately addressable across ordering changes", () => {
  const artifacts = [1, 2].map(i => ({ id: `call-${"x".repeat(90)}-${i}`, jobId: "job", type: "plotly_json", name: "figure.json" }));
  const compile = (items: Artifact[]) => compileScientificPresentation({ resultId: "result", artifacts: items }).blocks.filter(block => block.type === "figure");
  const first = compile(artifacts), reversed = compile([...artifacts].reverse());
  expect(new Set(first.map(block => block.id)).size).toBe(2);
  expect(first.map(block => block.id)).toEqual(reversed.map(block => block.id).reverse());
  expect(first.every(isSafePresentationBlock)).toBe(true);
});
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
  it("translates narrative terms without expanding scientific claims or altering precision and provenance", () => {
    const prose = "统计量由保存的网格值计算得出（statistics_authority = computed_from_payload）。积分语义为 electron_count，数值 3.1000000000000005 electron。量类型为 orbital_density，归一化语义为 source_native，端点策略为 excluded；不是拓扑分析。";
    const readable = scientificNarrativeText(prose);
    expect(readable).toBe("统计量由保存的网格值计算得出。积分表示电子数，数值 3.1000000000000005 electron。物理量为轨道密度，归一化沿用源数据，网格不包含终点；不是拓扑分析。");
    expect(scientificNarrativeText(readable)).toBe(readable);
    expect(scientificNarrativeText("轨道密度（orbital_density）；未被赋予物理意义（not_physically_interpreted），不能解释为电子数。")).toBe("轨道密度；未被赋予物理意义，不能解释为电子数。");
    expect(presentationScientificText("积分语义为 electron_count，数值 18 electron；不是拓扑分析。")).toBe("积分表示电子数，数值 18 electron；不是拓扑分析。");
    expect(presentationScientificText("结果投影仪不推断 RDF 曲线中的峰位或配位壳层。")).toBe("不据 RDF 曲线推断峰位或配位壳层。");
    expect(presentationScientificText("本次 RDF 已保存 3 个峰位，但未推断配位壳层。")).toBe("本次 RDF 已保存 3 个峰位，但未推断配位壳层。");
    const identifiers = String.raw`electron_count.json result:electron_count unknown_semantics https://example.org/?kind=electron_count ../source_native C:\data\orbital_density source_declared/field exact source versions.csv invalidated Interpretation`;
    expect(scientificNarrativeText(identifiers)).toBe(identifiers);
    expect(scientificNarrativeText("`electron_count`；`statistics_authority = computed_from_payload`；excluded；included；1.25000000000001e-9 electron/Å³")).toBe("`electron_count`；`statistics_authority = computed_from_payload`；excluded；included；1.25000000000001e-9 electron/Å³");
  });

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

  it("projects the persisted Agent2 interpretation contract into bounded summary, findings, and limitations", () => {
    const presentation = compileScientificPresentation({
      resultId: "result-phonon",
      interpretationId: "interpretation-phonon",
      sourceObjectRefs: [source],
      persistedInterpretation: {
        contract_version: "1.0",
        title: "声子能带与态密度分析结果",
        answer_lead: "声子能带包含 6 条分支，频率范围为 0.0 至 5.0 THz。",
        primary_findings: [{
          finding_id: "finding-band",
          statement: "声子能带包含 6 条分支。",
          importance: "HIGH",
          confidence: "HIGH",
          fact_refs: ["fact-branch-count"],
          evidence_refs: ["evidence-band"],
          result_item_refs: ["result-item-band"],
        }],
        supporting_findings: [{
          finding_id: "finding-dos",
          statement: "声子态密度积分为 6 个模式。",
          importance: "MEDIUM",
          confidence: "MEDIUM",
          fact_refs: ["fact-dos-integral"],
          evidence_refs: ["evidence-dos"],
          result_item_refs: ["result-item-dos"],
        }],
        limitations: ["The current band Artifact does not provide eigenvectors or animation authority."],
        primary_result_refs: ["result-item-band"],
        supporting_result_refs: ["result-item-dos"],
        follow_up_suggestions: [],
      },
      validatedNarrative: "不应渲染的旧整段消息。\n- 重复发现\n限制：重复限制",
    });

    expect(presentation.blocks.filter((block) => block.type === "narrative")).toEqual([
      expect.objectContaining({
        text: "声子能带包含 6 条分支。",
      }),
    ]);
    expect(presentation.blocks.filter((block) => block.type === "finding")).toEqual([
      expect.objectContaining({
        text: "声子能带包含 6 条分支。",
        confidence: "DIRECT",
        factIds: ["fact-branch-count"],
        evidenceIds: ["evidence-band"],
        source: expect.objectContaining({ factId: "fact-branch-count", evidenceId: "evidence-band" }),
      }),
      expect.objectContaining({
        text: "声子态密度积分为 6 个模式。",
        confidence: "QUALIFIED",
      }),
    ]);
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "limitation",
      text: "The current band Artifact does not provide eigenvectors or animation authority.",
    }));
    expect(presentationLimitationText("The current band Artifact does not provide eigenvectors or animation authority.")).toBe(
      "当前声子能带 Artifact 不包含特征向量，因此不提供模式动画依据。",
    );
  });

  it("keeps internal provenance identities out of scientific prose while preserving bounded source refs", () => {
    expect(
      presentationScientificText(
        "Band 图（figure.demo）提供带隙事实 fact.demo，值为 0.6 eV。该事实来自证据 evidence.demo（step_1-table_json）。该事实来自证据 evidence.demo。但 limitation.demo 明确说明：仅来自供应数据。",
      ),
    ).toBe(
      "Band 图提供带隙事实，值为 0.6 eV。该数值已绑定本次分析证据。同时，权威限制说明：仅来自供应数据。",
    );
    expect(presentationMetricTitle("electronic.band_gap")).toBe("电子带隙（供应数据）");
    expect(presentationMetricTitle("electronic.kpoint_count")).toBe("k 点数");
    expect(presentationMetricTitle("ml.high_error_sample_id")).toBe("最大误差样本");
  });

  it("formats long scientific values for display without mutating the authoritative contract value", () => {
    expect(formatScientificNarrativeNumbers("参考版本 1.0.0；版本 1.0；version: 2.0；1.2.3-beta；192.168.0.1")).toBe(
      "参考版本 1.0.0；版本 1.0；version: 2.0；1.2.3-beta；192.168.0.1",
    );
    expect(formatScientificNarrativeNumbers("Value 0.20000000000000004. Uncertainty 1.23456789e-12.")).toBe(
      "Value 0.2. Uncertainty 1.2346e-12.",
    );
    expect(formatPresentationMetricValue("0.20000000000000004")).toBe("0.2");
    expect(formatPresentationMetricValue("0.21602468994692867")).toBe("0.2160247");
    expect(formatPresentationMetricValue("-1.4802973661668753e-16")).toBe("-1.4803e-16");
    expect(formatPresentationMetricValue("sample-fe2o3")).toBe("sample-fe2o3");
    expect(formatScientificNarrativeNumbers("MAE 为 0.20000000000000004，RMSE 为 0.21602468994692867。")).toBe(
      "MAE 为 0.2，RMSE 为 0.2160247。",
    );
    expect(formatScientificNarrativeNumbers("MAE为0.20000000000000004，残差为0.2999999999999998。")).toBe(
      "MAE为0.2，残差为0.3。",
    );
    expect(formatScientificNarrativeNumbers("sample-fe2o3 的值为 2.2。")).toBe(
      "sample-fe2o3 的值为 2.2。",
    );
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

  it("binds each multi-source Artifact to its authoritative result-item version", () => {
    const bandSource = {
      objectId: "phonon-band",
      versionId: "band-v1",
      objectType: "phonon.band",
      displayName: "Phonon band",
    };
    const dosSource = {
      objectId: "phonon-dos",
      versionId: "dos-v1",
      objectType: "phonon.dos",
      displayName: "Phonon DOS",
    };
    const presentation = compileScientificPresentation({
      resultId: "result-phonon",
      artifacts: [
        {
          id: "artifact-band",
          jobId: "job-phonon",
          type: "plotly_json",
          name: "phonon_band.json",
        } as Artifact,
        {
          id: "artifact-dos",
          jobId: "job-phonon",
          type: "plotly_json",
          name: "phonon_dos.json",
        } as Artifact,
      ],
      sourceObjectRefs: [bandSource, dosSource],
      artifactSourceRefs: {
        "artifact-band": [bandSource],
        "artifact-dos": [dosSource],
      },
    });

    expect(
      presentation.blocks.find(
        (block) =>
          block.type === "figure" && block.artifactId === "artifact-band",
      )?.source,
    ).toEqual(
      expect.objectContaining({
        objectId: "phonon-band",
        versionId: "band-v1",
      }),
    );
    expect(
      presentation.blocks.find(
        (block) =>
          block.type === "figure" && block.artifactId === "artifact-dos",
      )?.source,
    ).toEqual(
      expect.objectContaining({
        objectId: "phonon-dos",
        versionId: "dos-v1",
      }),
    );
    expect(
      presentation.blocks.filter(
        (block) => block.type === "viewer_reference",
      ),
    ).toHaveLength(2);
  });

  it("does not guess an exact Artifact version for ambiguous legacy sources", () => {
    const presentation = compileScientificPresentation({
      resultId: "result-legacy",
      artifacts: [
        {
          id: "artifact-legacy",
          jobId: "job-legacy",
          type: "table_json",
          name: "legacy.json",
        } as Artifact,
      ],
      sourceObjectRefs: [
        source,
        {
          objectId: "structure-b",
          versionId: "version-v2",
          objectType: "Structure",
        },
      ],
    });

    const artifact = presentation.blocks.find(
      (block) =>
        block.type === "table" && block.artifactId === "artifact-legacy",
    );
    expect(artifact?.source.artifactId).toBe("artifact-legacy");
    expect(artifact?.source.objectId).toBeUndefined();
    expect(artifact?.source.versionId).toBeUndefined();
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

  it("preserves the persisted outer interpretation identity for evidence inspection", () => {
    const presentation = compileScientificPresentation({
      resultId: "result-1",
      interpretationId: "interpretation-1",
      evidence: [{
        schemaVersion: "1.0",
        evidenceItemId: "evidence-1",
        semanticRole: "band_gap",
        evidenceKind: "SCALAR",
        subjectId: "mat-2",
        displayValue: "2.5",
        unit: "eV",
        sourceArtifactId: "artifact-1",
        sourceArtifactChecksum: "a".repeat(64),
        artifactContract: "dataset.table",
        artifactContractVersion: "1.0",
        sourceToolId: "data.materials_explorer",
        sourceToolVersion: "1.0",
        fieldLocator: { fieldId: "band_gap", entityId: "mat-2" },
        warnings: [],
        limitations: [],
      }],
    });
    expect(presentation.blocks.find((block) => block.type === "evidence_reference")?.source.interpretationId).toBe("interpretation-1");
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

  it("fails closed for unknown runtime block types", () => {
    expect(isSafePresentationBlock({
      id: "unknown",
      type: "remote_component",
      label: "ignored",
    })).toBe(false);
  });

  it("rejects executable UI fields hidden inside otherwise supported blocks", () => {
    const base = {
      id: "safe-narrative",
      type: "narrative",
      text: "Grounded scientific summary.",
      source: { resultId: "result-1" },
    };
    expect(isSafePresentationBlock({
      ...base,
      component: "RemoteScientificWidget",
    })).toBe(false);
    expect(isSafePresentationBlock({
      ...base,
      modulePath: "https://plugins.invalid/widget.js",
    })).toBe(false);
    expect(isSafePresentationBlock({
      ...base,
      html: "<img src=x onerror=alert(1)>",
    })).toBe(false);
    expect(isSafePresentationBlock({
      ...base,
      source: {
        resultId: "result-1",
        url: "https://plugins.invalid/result",
      },
    })).toBe(false);
  });

  it("rejects remote or executable identities before building artifact routes", () => {
    expect(isSafePresentationBlock({
      id: "unsafe-figure",
      type: "figure",
      title: "Persisted figure",
      artifactId: "https://plugins.invalid/figure.json",
      source: { artifactId: "https://plugins.invalid/figure.json", jobId: "job-1" },
    })).toBe(false);
    expect(isSafePresentationBlock({
      id: "unsafe-viewer",
      type: "viewer_reference",
      title: "Viewer",
      label: "Open source",
      source: { objectId: "javascript:alert(1)", versionId: "version-1" },
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
    expect(presentation.blocks).toContainEqual(expect.objectContaining({ type: "finding", factIds: ["fact-1"], evidenceIds: ["evidence-1"] }));
    expect(presentation.blocks).toContainEqual(expect.objectContaining({
      type: "evidence_reference",
      source: expect.objectContaining({ interpretationId: "interpretation-1" }),
    }));
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

  it("labels repeated figures and metrics by their exact material rather than array position", () => {
    const sources = ["Si", "Cu", "NaCl"].map((name) => ({ objectId: name, versionId: `${name}-v1`, displayName: `${name}.cif` }));
    const artifactSources = [sources[2], sources[0], sources[1]];
    const presentation = compileScientificPresentation({
      sourceObjectRefs: sources,
      artifactSourceRefs: Object.fromEntries(artifactSources.map((source, i) => [`a${i}`, [source]])),
      artifacts: artifactSources.map((_, i) => ({ id: `a${i}`, jobId: "job", type: "plotly_json", name: "rdf_plot.json" } as Artifact)),
      facts: artifactSources.map((_, i) => ({ factId: `f${i}`, predicate: "rdf.number_density", subjectRef: `a${i}`, value: i + 0.1, unit: "angstrom^-3", source: { artifactId: `a${i}` } })),
    });
    expect(presentation.blocks.flatMap((block) => block.type === "figure" ? [block.title] : [])).toEqual([
      "NaCl.cif · 径向分布函数（RDF）", "Si.cif · 径向分布函数（RDF）", "Cu.cif · 径向分布函数（RDF）",
    ]);
    expect(presentation.blocks.filter((block) => block.type === "metric").map((block) => [block.title, block.source.versionId])).toEqual([
      ["NaCl.cif · 数密度", "NaCl-v1"], ["Si.cif · 数密度", "Si-v1"], ["Cu.cif · 数密度", "Cu-v1"],
    ]);
  });

  it("validates bounded fact references independently of provenance references", () => {
    const finding = { id: "finding", type: "finding", title: "发现", text: "结论", confidence: "DIRECT", source: {}, evidenceIds: ["evidence"], factIds: ["fact"] };
    expect(isSafePresentationBlock(finding)).toBe(true);
    expect(isSafePresentationBlock({ ...finding, factIds: undefined })).toBe(true);
    expect(isSafePresentationBlock({ ...finding, factIds: "fact" })).toBe(false);
    expect(isSafePresentationBlock({ ...finding, factIds: ["<script>run()</script>"] })).toBe(false);
    expect(isSafePresentationBlock({ ...finding, factIds: Array.from({ length: 13 }, (_, i) => `fact-${i}`) })).toBe(false);
  });

  it("binds report figures to their declared exact source type", () => {
    const band = { objectId: "band-object", versionId: "band-version", objectType: "electronic.band_structure", displayName: "Band" };
    const dos = { objectId: "dos-object", versionId: "dos-version", objectType: "electronic.dos", displayName: "DOS" };
    const presentation = compileReportPresentation({
      report_id: "report-electronic",
      snapshot_id: "snapshot-electronic",
      project_id: "project-1",
      research_turn_id: "turn-electronic",
      scientific_result_snapshot_id: "result-electronic",
      scientific_interpretation_id: "interpretation-electronic",
      title: "Electronic",
      relevance_at_generation: "CURRENT",
      current_effective_relevance: "CURRENT",
      grounding_status: "VALID",
      scientific_context: "exact",
      finding_count: 0,
      figure_count: 2,
      source_fingerprint: "fingerprint",
      created_at: "2026-08-31T00:00:00Z",
      viewer_sources: [dos, band].map((item, index) => ({
        source_ref: `source-${index + 1}`,
        object_id: item.objectId,
        version_id: item.versionId,
        object_type: item.objectType,
        display_name: item.displayName,
        is_current_version: true,
      })),
      figure_sources: [
        { figure_ref: "figure-band", artifact_ids: ["artifact-band"], job_id: "job-electronic", object_id: band.objectId, version_id: band.versionId, object_type: band.objectType },
        { figure_ref: "figure-dos", artifact_ids: ["artifact-dos"], job_id: "job-electronic", object_id: dos.objectId, version_id: dos.versionId, object_type: dos.objectType },
      ],
      report: {
        contract_version: "2.0",
        title: "Electronic",
        research_question: "比较电子数据",
        summary: "已验证结果。",
        discussion: null,
        conclusion: null,
        next_steps: null,
        main_findings: [],
        primary_figures: [
          { figure_ref: "figure-band", caption: "电子能带", fact_refs: [], evidence_refs: [] },
          { figure_ref: "figure-dos", caption: "电子态密度", fact_refs: [], evidence_refs: [] },
        ],
        supporting_results: [],
        method_summary: "方法",
        limitations: [],
        data_sources: ["source-1", "source-2"],
        evidence_refs: [],
        reproducibility_summary: "可复现",
        omitted_supporting_items: [],
      },
    });
    const figures = presentation.blocks.filter((block) => block.type === "figure");
    expect(figures).toHaveLength(2);
    expect(figures.every(isSafePresentationBlock)).toBe(true);
    expect(figures[0]?.source).toEqual(expect.objectContaining({ objectId: "band-object", versionId: "band-version" }));
    expect(figures[1]?.source).toEqual(expect.objectContaining({ objectId: "dos-object", versionId: "dos-version" }));
  });
});
