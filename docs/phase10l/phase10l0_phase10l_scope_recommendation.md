# Phase 10L-0 Scope Recommendation

Status: recommendation for reviewer decision. This document does not authorize
implementation and does not modify the canonical roadmap.

## 10L-1 Analysis Intent

Recommendation: **REQUIRED**.

The current request is a raw prompt plus dataset/profile/Registry IDs. A small,
strict Analysis Intent should separate the user's scientific objective from an
executable plan. It should remain bounded and avoid a general conversation or
workflow language.

Reviewer should decide the minimum fields for goal category, resource scope,
requested outputs, constraints, and unresolved choices. Existing raw prompt
and IDs should be retained as provenance.

## 10L-2 Capability-Aware Planner

The essential gaps are:

1. A machine-readable eligibility bridge from Profile readiness and semantic
   groups to Registry tools.
2. Planner-facing semantic requirements and collision/ranking metadata without
   weakening the execution Registry.
3. Consistent resource/object and parameter binding across domains.
4. Explicit unsupported/ambiguous outcomes instead of an unrelated generic
   fallback.
5. Bounded plan complexity and prompt/provider configuration caps.
6. Better live-LLM context than the current shallow Profile text, while keeping
   data and artifact contents bounded and untrusted.

The implementation should reuse the current Registry, Profile 2.0, provider
protocol, and strict PlanValidator. It should not add an Agent framework.

## 10L-3 Bounded Multi-Tool Analysis

Current case: **A - multi-step execution exists, but only as sequential
independent steps**.

The next phase should not replace QueueWorkerRuntime with a generic DAG engine.
It needs the smallest approved dependency and artifact-binding model required
for bounded materials analyses. Reviewer must choose ordered sequence versus a
restricted dependency graph. Required hardening includes max steps, cycle or
forward-reference rejection if dependencies are added, failure/partial-result
policy, cancellation, idempotent replay, and typed artifact compatibility.

## 10L-4 Scientific Result Interpretation

Recommendation: extend existing deterministic summaries and recipes. Add a
bounded structured context containing computed metrics, warnings, limitations,
tool provenance, and explicit unavailable facts. The LLM may explain and
recommend, but cannot invent calculations or consume arbitrary raw artifacts.
No implementation exists today.

## 10L-5 Natural-Language Evidence

Final evidence should cover at least:

| Case | Required flow |
|---|---|
| Dataset composition/anomaly analysis | Profile -> eligible product(s) -> bounded findings |
| Structure reasonableness | Profile -> available structure analyses -> limitation-aware result |
| Materials model evaluation | Semantic ML group -> evaluation -> chemistry/sample findings |
| Phonon calculation inspection | Available phonon resources -> approved tools -> warnings |
| Charge-density inspection | Volumetric resource -> canonical artifact -> grounded interpretation |

Each case should prove intent, Profile authority, validated plan, Registry
execution, artifacts, interpretation boundaries, browser behavior, no real LLM
in default CI, service-backed execution, and exact-head CI.

## Scope Constraints

Keep frozen:

* LLMs never execute arbitrary Python, shell, filesystem, or network actions.
* PlanValidator remains before persistence/execution.
* Tool Registry and registered Adapters remain the execution boundary.
* DataProfile remains deterministic data truth.
* Scientific calculations remain deterministic backend work.
* No generic workflow engine, multi-agent system, RAG, or memory system is
  required for Phase 10L initial completion.
