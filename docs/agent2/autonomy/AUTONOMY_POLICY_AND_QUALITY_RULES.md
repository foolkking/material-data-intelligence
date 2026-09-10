# Autonomy Policy and Scientific Quality Rules

## Policy identity

Every bounded autonomous branch carries `agent2.autonomy-policy/1.0` and its
SHA-256 fingerprint. Historical events keep the policy identity that governed
them; later policy changes do not rewrite completed research.

The conservative default caps are:

| Limit | Default |
| --- | ---: |
| research cycles | 4 |
| total Capability executions | 8 |
| dependency-plan steps per cycle | 4 |
| LLM decision calls | 8 |
| replans | 3 |
| context input tokens | 12,000 |
| maximum cost class | MEDIUM |

The AnalysisPlan contract remains the hard execution authority. Policy cannot
advertise a larger dependency plan than the persisted plan schema permits.

## Selection gate

Autonomous selection follows the inspectable sequence:

```text
authorized exact source?
→ Capability eligible?
→ current qualification evidence?
→ qualification level permitted?
→ cost class permitted?
→ materially adds evidence?
→ not a duplicate semantic step?
→ within policy caps?
→ execute
```

Eligibility, qualification and planning remain separate:

- **Eligibility** determines whether the current scientific input satisfies
  deterministic preconditions.
- **Qualification** states what current evidence validates about the
  Capability.
- **Planning** decides whether an eligible, sufficiently qualified Capability
  materially contributes to the user objective.

## Permitted qualification levels

The default policy allows current, fingerprint-matched evidence for:

```text
DOMAIN_VALIDATED
REFERENCE_VALIDATED
CROSS_IMPLEMENTATION_VALIDATED
EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED
```

`STRUCTURAL_ONLY`, missing, stale or otherwise unqualified evidence is rejected
for autonomous selection.

`EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED` is usable only within the
platform-owned scope recorded by Workstream D. Its limitations remain attached
to the assessment and downstream synthesis; the Agent must not represent it as
independent validation of an external solver or library.

Qualification is current only when all of these agree:

```text
Capability version
scientific contract fingerprint
quality evidence fingerprint
manifest qualification summary
```

## Parameter authority

Autonomous planning may use parameters only when they are available from
authoritative context or durable Results. It must not invent scientific object
versions, units, timestep, target columns, model identity, wavelength or fit
windows.

The trajectory reference chain demonstrates this rule:

```text
MSD Result facts:
  trajectory.msd_first_lag_time
  trajectory.msd_last_lag_time
  trajectory.msd_lag_count

→ validated diffusion fit interval
```

Missing or invalid boundaries produce `NEEDS_CLARIFICATION` or
`STOP_WITH_LIMITATIONS`, never a guessed default interval.

## Stop rules

Autonomy stops deterministically when:

- the objective is sufficiently addressed;
- another analysis would repeat the same semantic step;
- no appropriately qualified Capability can proceed;
- authoritative parameters are missing;
- evidence is partial or conflicting and cannot be safely advanced;
- the requested inference is scientifically unsupported;
- a cycle, execution, LLM or cost budget is exhausted;
- the user cancels.

Executing more Tools is not a success criterion. The preferred path is the
minimum sufficient scientific work.

## Recovery and stale-owner rules

Autonomy uses Workstream A lifecycle ownership. Persisted assessment and child
Turn signatures make duplicate delivery idempotent. A stale process cannot
replace a newer durable assessment, child identity, Job or Result. Publication
recovery resubmits existing durable work.

## Evaluation contract

`scripts/autonomy_evaluation.py --check` evaluates bounded golden cases and
generates:

`docs/agent2/autonomy/generated/autonomy_evaluation.json`

Each case records:

```text
goal
expected outcomes
actual outcome
selected Capability
qualification snapshot
reason codes
limitations
violations
```

The current corpus checks minimum-sufficient work, Result-driven continuation,
quality-aware selection, duplicate/loop prevention, unsupported-claim stops
and partial-evidence stops. It is a bounded regression/evaluation corpus, not a
production statistical benchmark.

## Safety boundary

Autonomy cannot:

- construct unregistered Tools or Adapters;
- execute arbitrary Python, shell, filesystem or network operations;
- bypass project/source authorization;
- bypass Tool Registry, Adapter Registry, Artifact validation or grounding;
- replace exact ScientificObjectVersion or ScientificResult identity;
- persist hidden reasoning;
- run without enforceable stop caps.

