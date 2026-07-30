# Phase 10L-3 Bounded Multi-Tool Architecture

Status: implementation contract; verification and exact-SHA closure remain pending.

## Purpose

Phase 10L-3 adds one bounded dependency layer after the Phase 10L-2
capability decision. It does not replace AnalysisIntent, eligibility, exact
parameter binding, PlanValidator, Tool Registry, or Adapter execution.

```text
READY AnalysisIntent 1.0
  -> exact DataProfile 2.0
  -> EligibilityResolution 1.0
  -> Phase 10L-2 capability decision and exact bindings
  -> bounded dependency composer
  -> AnalysisPlan 0.2
  -> dependency validator + existing PlanValidator
  -> persisted plan/job
  -> QueueWorkerRuntime
  -> registered Adapters
  -> typed artifacts, binding resolutions, and lineage
```

## Authority Boundaries

| Concern | Authority |
|---|---|
| Intended science and exact scope | AnalysisIntent 1.0 |
| Available data and semantic identities | exact DataProfile 2.0 |
| Selected tools and ordinary parameters | Phase 10L-2 decision and binder |
| Planner-visible artifact ports | ToolArtifactPortMetadata 1.1 overlay |
| Producer/consumer compatibility | deterministic compatibility matrix |
| Dependency semantics | AnalysisPlan 0.2 `dependencyBindings` |
| Tool and parameter validity | existing PlanValidator |
| Dependency validity | independent dependency validator |
| Execution | QueueWorkerRuntime through registered Adapters |
| Artifact bytes | existing ArtifactStorage abstraction |
| Audit history | immutable plan, binding, execution, resolution, and lineage records |

The composer may use only tools already selected by Phase 10L-2 and exact
compatible port pairs. It does not rescan rejected Registry candidates or
change resource, target, model, or parameter identity.

## Real Dependency Surface

The audited current Registry has one production dependency composition:

```text
phonon.band:canonical-band -> phonon.band_dos:band
phonon.dos:canonical-dos   -> phonon.band_dos:dos
```

All three tools are existing registered Adapters. The consumer already
validates the `phase10h.phonon_band.v1` and `phase10h.phonon_dos.v1` inputs and
their shared scientific identity before producing
`phase10h.phonon_band_dos.v1`. Phase 10L-3 adds orchestration and lineage, not
a new phonon algorithm.

## Bounded Execution

- At most four selected steps, six bindings, graph depth four, and three
  incoming or outgoing bindings per step.
- Execution is serial in deterministic topological order.
- Step-array order has no dependency authority.
- A producer failure blocks only its descendants; independent branches may
  continue.
- Successful artifacts remain persisted when another branch fails.
- Runtime does not call a Planner or LLM, repair a plan, or fall back to the
  original dataset when a required artifact is absent.

## Explicit Non-Goals

This phase is not a generic DAG engine. It adds no loops, conditions,
parallel scheduler, dynamic fan-out, runtime replanning, cross-job artifacts,
remote artifact inputs, arbitrary expressions, plan editor, result
interpretation, Workspace redesign, professional-science capability, or new
execution framework.
