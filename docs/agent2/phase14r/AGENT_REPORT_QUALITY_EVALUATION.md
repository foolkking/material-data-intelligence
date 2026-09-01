# Agent and Report Quality Evaluation

## Authority and evaluation boundary

R10 combines deterministic correctness, the checked-in scientific Report
rubric and bounded real-user inspection. LLM-as-judge is supplemental only and
was not used for this campaign. Existing provider-composed Reports are useful
test subjects, but deterministic grounding/provenance validation and the
persisted scientific authorities decide PASS.

Machine-readable results are recorded in
`docs/agent2/phase14r/R10_QUALITY_EVALUATION_RESULTS.json`.

## Versioned Agent evaluation corpus

The checked-in corpus
`apps/api/mdi_api/research_agent/evaluation/fixtures/phase14r_quality_v1.json`
uses contract `phase14r.agent-quality-evaluation/1.0` and corpus identity
`phase14r-r10-v1`.

It contains 32 cases:

```text
18 orchestrator decision cases
14 mature-product contract cases
```

The scientific cases cover Structure, CrystalNN, VoronoiNN, coordination
histograms, Structure RDF, theoretical and comparison XRD, trajectory RDF,
MSD, diffusion, Phonon Band/DOS, Electronic Band/DOS, Dataset exploration,
composition space and supplied regression evaluation. The product cases cover
query-only routing, ambiguity/clarification, exact Result reuse, historical
version fidelity, partial execution, unsupported and wrong-assumption
requests, multi-result synthesis, stop during orchestration, queued
cancellation, edit/branch, rerun, re-interpret and retry.

Each case declares the evaluation dimensions that apply:

```text
intent understanding
context selection
clarification quality
capability selection / parameter fidelity
over-analysis / under-analysis
grounding and limitations
scientific usefulness and relevance
conversation/control quality
latency/recovery
historical fidelity
```

The deterministic runner validates legal references, registered requirements,
constraint schemas and expected actions. Product-control cases link to exact
deterministic regression node IDs; a missing or renamed evidence test fails
the corpus evaluation instead of being silently ignored.

Current focused result:

```text
corpus cases = 32
deterministic passed = 32
deterministic failed = 0

linked evidence tests = 27
passed = 27
failed = 0
skipped = 0
```

The historical Phase 2 corpus remains intact:

```text
historical/focused = 6 passed, 4 optional live-provider skips
```

Those four skips are not part of the mandatory R10 count; they remain opt-in
DeepSeek qualification controlled by `MDI_RUN_AGENT2_LIVE=1` and
`DEEPSEEK_KEY`.

## Report quality campaign

The deterministic scorer implements the 20-criterion rubric in
`SCIENTIFIC_REPORT_QUALITY_RUBRIC.md`. It evaluates immutable Report snapshots
against the exact persisted `ScientificResultSnapshot` loaded by the Report's
authoritative foreign key. It verifies section structure, fact/evidence
closure, exact source versions, grounding, limitations, Figure/Table
availability and absence of raw provider/debug payloads. It does not pretend
to measure prose elegance; that remains a bounded human/browser review.

### Current reports

| Family | Report | Result | Exact version(s) | Score | Verdict |
| --- | --- | --- | --- | ---: | --- |
| Structure coordination histogram | `agent2_report_19a0d0c261c28577101de81532464893` | `2382b0eb-b056-42b2-b6a7-d2e8a4ca398c` | `8859cb49-0766-48cd-8a56-e44f5332e0c5` | 100.0% | QUALITY_PASS |
| Structure immutable revision | `agent2_report_revision_7f89612da461b9697d5075d1ce7949b0` | `2382b0eb-b056-42b2-b6a7-d2e8a4ca398c` | `8859cb49-0766-48cd-8a56-e44f5332e0c5` | 100.0% | QUALITY_PASS |
| Electronic Band + DOS | `agent2_report_e7fa88beeb9a92cd8d46e44182ec46f9` | `fa336a66-89f5-47f0-9869-f9240c2e0050` | `087f93c4-2a5b-4c1e-b4e4-916c368801d0`, `7f7f1008-4d67-4592-a501-41d9a7d9a5cc` | 100.0% | QUALITY_PASS |
| Trajectory MSD + diffusion | `agent2_report_e54681009a0e49abe371247d9053ce61` | `26127c48-d736-4983-b035-b68db238f6a7` | `a22745f2-17b6-434f-ba4c-3fe6bd244841` | 100.0% | QUALITY_PASS |
| Composition + regression | `agent2_report_9b6943b7b3a9eaecd594ecf9bde7e806` | `d984bb18-acc6-4d55-90e1-2097b0305a69` | `cf2aeeea-53ad-452a-a4ef-7b61555004e5` | 100.0% | QUALITY_PASS (`Figure=N/A`, authoritative Result has no Figure) |
| Legacy XRD comparison | `agent2_report_1b745b90c5408fbb0dce4ca2679f9daa` | `8c996f41-d78f-4dfc-a9b9-ea1c2ec0d5c6` | `651b5310-d7d6-4894-883d-cc43d7953823`, `86f54119-5404-4ade-835d-44984b84b02c` | 89.5% | LEGACY baseline, not QUALITY_PASS |

The legacy XRD report is intentionally retained as a truthful negative
baseline: it lacks the scientific-discussion section (criterion 11 = 0), with
partial synthesis/coherence scores. The scorer therefore rejects it even
though its schema and grounding are valid. This demonstrates:

```text
REPORT_VALID != GOOD_SCIENTIFIC_REPORT
```

### Same-Result comparison

The Structure base Report and immutable revision use the same exact Result:

```text
Result = 2382b0eb-b056-42b2-b6a7-d2e8a4ca398c

base Report =
agent2_report_19a0d0c261c28577101de81532464893

revision Report =
agent2_report_revision_7f89612da461b9697d5075d1ce7949b0
```

Both score 100%. This is expected: the revision improves user-facing
organization/title metadata, not scientific content. Exact Result, Turn,
source version, Findings, Figures/Tables and Evidence remain unchanged.
Evaluation is read-only:

```text
Jobs              301 → 301  delta 0
ToolCalls          395 → 395  delta 0
Artifacts         1565 → 1565 delta 0
ScientificResults  203 → 203  delta 0
```

### Bounded human/browser review

The existing authenticated same-stack report campaign opened Structure,
Dataset, Electronic, Phonon, Diffusion, Composition and RDF Reports. The
current reviewed Reports:

- display the expected scientific finding hierarchy rather than raw JSON;
- preserve exact source-version tokens and evidence links;
- expose Figures/Tables only when the Result supplies them;
- present limitations in the normal scientific workbench vocabulary;
- do not expose raw capability IDs or internal provider payloads;
- retain mobile readability for the exercised `390x844` routes.

This review supplements the deterministic scorer. It is not a hidden
LLM-as-judge verdict.

## Current R10 verdict

```text
RESEARCH_AGENT_EVALUATION_CORPUS = PASS
SCIENTIFIC_CONVERSATION_CONTRACT_EVALUATION = PASS
SCIENTIFIC_REPORT_QUALITY_EVALUATION = PASS
LLM_AS_JUDGE_SOLE_AUTHORITY = NO
NEW_PROVIDER_CALLS_FOR_R10 = 0
SCIENTIFIC_RECOMPUTATION_FOR_REPORT_EVALUATION = NO
```

Remaining Phase 14-R gates outside R10 are not changed by this document.
