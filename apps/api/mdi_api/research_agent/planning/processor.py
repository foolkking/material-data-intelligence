from __future__ import annotations

from datetime import datetime, timezone
import asyncio
import logging
import math
from typing import Any
from uuid import UUID, uuid4

from mdi_llm.providers import LLMProviderError
from mdi_schemas import PlannerBindingSource

from mdi_api.agent2_errors import CapabilityBindingFailed, CapabilityPlanInvalid
from mdi_api.application.research.ports import ResearchRepositoryFactoryPort
from mdi_api.research_agent.capabilities.fingerprint import capability_plan_fingerprint
from mdi_api.research_agent.capabilities.quality_evidence import scientific_contract_fingerprint
from mdi_api.research_agent.capabilities.preconditions import build_default_precondition_registry
from mdi_api.research_agent.capabilities.resolver import CapabilityResolutionService
from mdi_api.research_agent.capabilities.schemas import (
    CapabilityEligibility, CapabilityPlannerInput, PlannerCapabilityView,
    PlannerInputSlotView, PlannerOutputSlotView, PlannerRequirementView,
    PlannerResultRef, PlannerSourceRef,
)
from mdi_api.research_agent.orchestration.schemas import ResearchTurnDecision
from mdi_api.research_agent.planning.binder import CapabilityBinder
from mdi_api.research_agent.planning.planner import (
    PROMPT_VERSION as PLANNER_PROMPT_VERSION,
    ScientificCapabilityPlanner,
)
from mdi_api.research_agent.schemas import ResearchAction, ResearchTurnEventType, ResearchTurnStatus
from mdi_api.research_agent.context.manifest import build_operation_manifest
from mdi_api.research_agent.context.policy import ContextOperation
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.domain.scientific_results.contracts import ScientificResultBundle
from mdi_tool_registry import build_tool_planner_metadata, load_manifests

logger = logging.getLogger(__name__)


class CapabilityPlanningProcessor:
    def __init__(self, repository_factory: ResearchRepositoryFactoryPort, *, registries: Any | None = None, tool_registry: Any | None = None, llm_client: Any | None = None) -> None:
        self.repository_factory = repository_factory
        self.registries = registries
        self.tool_registry = tool_registry or load_manifests()
        self.llm_client = llm_client

    def process(self, turn_id: UUID) -> dict[str, Any]:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            if turn["status"] != ResearchTurnStatus.READY_TO_PLAN.value:
                return {"status": "NOOP", "turn_id": str(turn_id), "turn_status": turn["status"]}
            claimed = unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=ResearchTurnStatus.READY_TO_PLAN.value, expected_version=int(turn["row_version"]), target_status=ResearchTurnStatus.PLANNING.value)
            self._event(unit, turn_id, ResearchTurnEventType.CAPABILITY_PLANNING_STARTED, {"status": claimed["status"]})
        return self._plan_after_claim(turn_id)

    def _plan_after_claim(self, turn_id: UUID) -> dict[str, Any]:
        registries = self.registries
        if registries is None:
            from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
            registries = DEFAULT_AGENT2_REGISTRIES
        try:
            prepared = self._resolve_and_persist(turn_id, registries)
            if prepared.get("terminal"):
                return prepared["result"]
            planner = ScientificCapabilityPlanner(registry=registries.capabilities, llm_client=self.llm_client)
            planner_input = self._planner_input(
                prepared["decision"], prepared["resolution"], prepared["snapshot"],
                prepared["reusable_results"], registries,
            )
            planner_manifest = build_operation_manifest(
                operation=ContextOperation.PLANNER,
                project_id=str(prepared["turn"]["project_id"]),
                research_session_id=str(prepared["turn"]["research_session_id"]),
                research_turn_id=turn_id,
                context_fingerprint=str(prepared["snapshot"].get("context_fingerprint") or ""),
                items=self._planner_manifest_items(planner_input, prepared["snapshot"]),
                serialized_input=planner_input.model_dump(mode="json"),
                serialized_input_version=planner_input.contract_version,
                invocation_role="scientific_capability_planner",
                prompt_template_version=PLANNER_PROMPT_VERSION,
                input_state="ACTUAL",
            )
            with self.repository_factory.unit_of_work() as unit:
                self._event(unit, turn_id, ResearchTurnEventType.CONTEXT_MANIFEST_RECORDED, {
                    "operation": "PLANNER",
                    "context_manifest": planner_manifest.model_dump(mode="json"),
                })
            plan, planner_mode, provider_result = asyncio.run(planner.plan(
                decision=prepared["decision"], resolution=prepared["resolution"],
                planner_input=planner_input,
                context=prepared["snapshot"],
            ))
            self._enforce_autonomy_plan_budget(
                prepared["turn"], plan
            )
            with self.repository_factory.unit_of_work() as unit:
                turn = unit.agent2.research_turns.get_for_update(turn_id)
                if turn["status"] != ResearchTurnStatus.PLANNING.value:
                    return {"status": "NOOP", "turn_id": str(turn_id), "turn_status": turn["status"]}
                self._reauthorize_snapshot(unit, turn, prepared["snapshot"])
                reusable_results = self._load_reusable_results(unit, turn, prepared["decision"], prepared["snapshot"])
                object_refs = self._snapshot_refs(prepared["snapshot"])
                result_object_refs = {
                    key: value["output_object_refs"][0]
                    for key, value in reusable_results.items()
                    if value.get("usable") and value.get("output_object_refs")
                }
                result_artifact_refs = {
                    key: value["artifact_ids_by_result_type"]
                    for key, value in reusable_results.items()
                    if value.get("usable") and value.get("artifact_ids_by_result_type")
                }
                result_artifact_metadata_refs = {
                    key: value.get("artifact_metadata_by_id") or {}
                    for key, value in reusable_results.items()
                    if value.get("usable") and value.get("artifact_metadata_by_id")
                }
                context = self._plan_context(
                    unit,
                    str(turn["project_id"]),
                    {**object_refs, **result_object_refs},
                )
                context["object_refs"] = object_refs
                context["result_object_refs"] = result_object_refs
                context["result_artifact_refs"] = result_artifact_refs
                context["result_artifact_metadata_refs"] = result_artifact_metadata_refs
                analysis_plan, plan_hash = CapabilityBinder(self.tool_registry).bind(
                    capability_plan=plan,
                    resolution=prepared["resolution"],
                    context=context,
                    registry=registries.capabilities,
                    decision=prepared["decision"],
                )
                plan_fp = capability_plan_fingerprint(plan, registry_fingerprint=prepared["resolution"].registry_fingerprint)
                capability_plan_id = uuid4()
                unit.agent2.research_capability_plans.add({"id": capability_plan_id, "research_turn_id": turn_id, "capability_resolution_id": prepared["resolution_id"], "contract_version": plan.contract_version, "plan_json": plan.model_dump(mode="json"), "input_fingerprint": plan_fp, "planner_mode": planner_mode, "prompt_version": None if provider_result is None else provider_result.prompt_version, "provider": None if provider_result is None else provider_result.provider, "model": None if provider_result is None else provider_result.model, "provider_request_id": None if provider_result is None else provider_result.provider_request_id, "repair_attempted": False if provider_result is None else provider_result.repair_attempted, "validation_status": "VALIDATED"})
                self._event(unit, turn_id, ResearchTurnEventType.CAPABILITY_PLAN_CREATED, {"capability_plan_id": str(capability_plan_id), "planner_mode": planner_mode})
                plan_id = f"plan_{uuid4().hex[:24]}"
                unit.repositories.analysis_plans.save_plan({"id": plan_id, "projectId": str(turn["project_id"]), "datasetId": context["dataset_id"], "profileId": context["profile_id"], "planSource": "agent2_capability_binder", "plannerProvider": None, "analysisPlan": analysis_plan.model_dump(mode="json"), "planHash": plan_hash, "validationStatus": "validated", "createdBy": "user_local"})
                current = unit.agent2.research_turns.get_for_update(turn_id)
                updated = unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=ResearchTurnStatus.PLANNING.value, expected_version=int(current["row_version"]), target_status=ResearchTurnStatus.PLAN_READY.value)
                unit.agent2.research_turns.attach_analysis_plan(turn_id, plan_id)
                self._event(unit, turn_id, ResearchTurnEventType.PLAN_ATTACHED, {"analysis_plan_id": plan_id})
                self._event(unit, turn_id, ResearchTurnEventType.ANALYSIS_PLAN_BOUND, {"analysis_plan_id": plan_id, "status": updated["status"]})
                self._event(unit, turn_id, ResearchTurnEventType.PLAN_READY, {"analysis_plan_id": plan_id, "status": updated["status"]})
                return {"status": updated["status"], "turn_id": str(turn_id), "analysis_plan_id": plan_id}
        except (TimeoutError, asyncio.TimeoutError):
            logger.warning("Agent2 capability planner timed out", extra={"turn_id": str(turn_id)})
            self._fail(turn_id, "CAPABILITY_PLANNER_TIMEOUT", "Capability planner timed out", target=ResearchTurnStatus.FAILED)
            raise
        except LLMProviderError as exc:
            logger.warning("Agent2 capability planner provider unavailable", extra={"turn_id": str(turn_id)})
            self._fail(turn_id, "CAPABILITY_PLANNER_UNAVAILABLE", exc.safe_message, target=ResearchTurnStatus.FAILED)
            raise
        except CapabilityPlanInvalid as exc:
            logger.warning("Agent2 capability plan rejected", extra={"turn_id": str(turn_id), "error_code": exc.code})
            self._fail(turn_id, exc.code, str(exc), target=ResearchTurnStatus.PLAN_REJECTED)
            raise
        except CapabilityBindingFailed as exc:
            logger.exception("Agent2 capability planning failed", extra={"turn_id": str(turn_id)})
            self._fail(turn_id, exc.code, str(exc))
            raise
        except Exception as exc:
            logger.exception("Agent2 capability planning failed unexpectedly", extra={"turn_id": str(turn_id)})
            self._fail(turn_id, "CAPABILITY_DETERMINISTIC_PLANNER_ERROR", str(exc), target=ResearchTurnStatus.FAILED)
            raise

    def _resolve_and_persist(self, turn_id: UUID, registries: Any) -> dict[str, Any]:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            decision_row = unit.agent2.research_turn_decisions.get_for_turn(turn_id)
            snapshot = unit.agent2.research_context_snapshots.get_for_turn(turn_id)
            if decision_row is None or snapshot is None:
                raise CapabilityPlanInvalid("decision or context snapshot missing")
            decision = ResearchTurnDecision.model_validate(decision_row["decision_json"])
            self._reauthorize_snapshot(unit, turn, snapshot)
            reusable_results = self._load_reusable_results(unit, turn, decision, snapshot)
            self._event(unit, turn_id, ResearchTurnEventType.CAPABILITY_RESOLUTION_STARTED, {"status": turn["status"]})
            resolver = CapabilityResolutionService(registries.capabilities, registries.requirements, self.tool_registry, build_default_precondition_registry())
            resolution = resolver.resolve(
                turn=turn,
                decision=decision,
                context_snapshot=snapshot,
                reusable_results=reusable_results,
            )
            resolution = self._enforce_autonomy_resolution(
                unit, turn_id, resolution, registries
            )
            resolution_id = uuid4()
            unit.agent2.research_capability_resolutions.add({"id": resolution_id, "research_turn_id": turn_id, "contract_version": resolution.contract_version, "requirement_snapshot_json": {"objective": resolution.objective, "requirements": [item.model_dump(mode="json") for item in decision.scientific_requirements]}, "resolution_json": resolution.model_dump(mode="json"), "registry_fingerprint": resolution.registry_fingerprint, "resolver_version": resolution.resolver_version})
            if resolution.unsatisfied_required_requirement_ids:
                current = unit.agent2.research_turns.get_for_update(turn_id)
                updated = unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=ResearchTurnStatus.PLANNING.value, expected_version=int(current["row_version"]), target_status=ResearchTurnStatus.UNSUPPORTED.value, completed_at=datetime.now(timezone.utc), error_code="CAPABILITY_REQUIREMENT_UNSATISFIED", error_summary="No executable capability path satisfies the required scientific requirements")
                self._event(unit, turn_id, ResearchTurnEventType.CAPABILITY_UNSUPPORTED, {"status": updated["status"], "requirements": resolution.unsatisfied_required_requirement_ids})
                return {"terminal": True, "result": {"status": updated["status"], "turn_id": str(turn_id)}}
            self._event(unit, turn_id, ResearchTurnEventType.CAPABILITY_RESOLUTION_COMPLETED, {"candidate_count": len(resolution.candidates), "registry_fingerprint": resolution.registry_fingerprint})
            return {
                "terminal": False,
                "turn": {
                    **turn,
                    "_autonomy": self._turn_autonomy(unit, turn_id),
                },
                "decision": decision,
                "snapshot": snapshot,
                "resolution": resolution,
                "resolution_id": resolution_id,
                "reusable_results": reusable_results,
            }

    @staticmethod
    def _planner_input(decision: ResearchTurnDecision, resolution: Any, snapshot: dict[str, Any], reusable_results: dict[str, dict[str, Any]], registries: Any) -> CapabilityPlannerInput:
        refs = CapabilityPlanningProcessor._snapshot_refs(snapshot)
        candidates = []
        ordered_candidates = sorted(resolution.candidates, key=lambda item: (item.planning_priority, item.capability_id, item.capability_version))
        capability_keys = {
            f"{item.capability_id}@{item.capability_version}": f"cap_{index}"
            for index, item in enumerate(ordered_candidates, 1)
        }
        for index, item in enumerate(ordered_candidates, 1):
            if item.eligibility not in {CapabilityEligibility.ELIGIBLE, CapabilityEligibility.CONDITIONAL}:
                continue
            manifest = registries.capabilities.require(item.capability_id, item.capability_version)
            candidates.append(PlannerCapabilityView(
                ref_key=f"cap_{index}", capability_id=item.capability_id, version=item.capability_version,
                eligibility=item.eligibility, satisfies_requirement_ids=item.satisfies_requirement_ids,
                input_slots=[PlannerInputSlotView(
                    name=slot.name,
                    accepted_object_types=list(slot.accepted_object_types),
                    required=slot.required,
                    min_count=slot.min_count,
                    max_count=slot.max_count,
                ) for slot in manifest.input_slots],
                output_slots=[PlannerOutputSlotView(
                    name=slot.name,
                    result_type=slot.result_type,
                    scientific_object_type=slot.scientific_object_type,
                    required=slot.required,
                    cardinality=slot.cardinality,
                ) for slot in manifest.output_slots],
                bound_source_ref_keys=item.bound_source_ref_keys,
                reusable_result_bindings=item.reusable_result_bindings,
                missing_input_slots=item.missing_input_slots,
                possible_producer_ref_keys={
                    slot: [capability_keys[value] for value in values if value in capability_keys]
                    for slot, values in item.possible_producers.items()
                },
                qualification_level=manifest.qualification.level,
                qualification_evidence_version=manifest.qualification.evidence_version,
                qualification_evidence_fingerprint=manifest.qualification.evidence_fingerprint,
                scientific_contract_fingerprint=scientific_contract_fingerprint(
                    manifest
                ),
                validated_domains=list(manifest.qualification.validated_domains),
                known_limitations=list(
                    manifest.qualification.known_limitations[:3]
                ),
            ))
        results = []
        for key, item in sorted(reusable_results.items()):
            results.append(PlannerResultRef(
                ref_key=key,
                result_id=item["snapshot_id"],
                relevance_status=item["relevance_status"],
                output_object_types=sorted({
                    *(ref.object_type for ref in item.get("output_object_refs") or []),
                    *(item.get("result_types") or []),
                }),
            ))
        return CapabilityPlannerInput(
            research_objective=decision.research_objective or resolution.objective,
            requirements=[PlannerRequirementView(requirement_id=item.requirement_id, criticality=item.criticality.value, subject_ref_keys=item.subject_ref_keys, constraints=item.constraints) for item in decision.scientific_requirements],
            candidates=candidates,
            source_bindings=[PlannerSourceRef(ref_key=key, object_type=ref.object_type, display_name=ref.display_name or ref.object_type) for key, ref in refs.items()],
            reusable_results=results,
            explicit_constraints=[item.constraints for item in decision.scientific_requirements if item.constraints],
        )

    @staticmethod
    def _planner_manifest_items(planner_input: CapabilityPlannerInput, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        selected_versions = {
            str(item.get("version_id"))
            for item in (snapshot.get("selection_refs_json") or [])
            if isinstance(item, dict)
        }
        snapshot_refs: dict[str, dict[str, Any]] = {}
        for raw in [*(snapshot.get("selection_refs_json") or []), *(snapshot.get("active_scope_refs_json") or [])]:
            if not isinstance(raw, dict):
                continue
            ref_key = f"obj_{len(snapshot_refs) + 1}"
            snapshot_refs.setdefault(ref_key, raw)
        items: list[dict[str, Any]] = []
        for source in planner_input.source_bindings:
            # ``PlannerSourceRef.ref_key`` is the bounded server-side binding
            # key. Resolve it first so two sources of the same object type can
            # never be silently collapsed onto the first matching row.
            raw = snapshot_refs.get(source.ref_key)
            if raw is None:
                # Compatibility fallback for older planner payloads that did
                # not preserve the binding key. This is intentionally bounded
                # and only used when the authoritative key is unavailable.
                raw = next(
                    (item for item in snapshot_refs.values() if str(item.get("object_type")) == source.object_type),
                    None,
                )
            items.append({
                "item_id": source.ref_key,
                "kind": "SCIENTIFIC_SELECTION" if raw and str(raw.get("version_id")) in selected_versions else "SCIENTIFIC_OBJECT",
                "authority_class": "SCIENTIFIC_DATA",
                "source_identity": f"{raw.get('object_id')}:{raw.get('version_id')}" if raw else source.ref_key,
                "opaque_ref": source.ref_key,
                "object_id": raw.get("object_id") if raw else None,
                "version_id": raw.get("version_id") if raw else None,
                "content": source.model_dump(mode="json"),
                "inclusion_reason": "exact source binding for capability planning",
                "selection_mode": "UI_SELECTION" if raw and str(raw.get("version_id")) in selected_versions else "CURRENT",
            })
        for candidate in planner_input.candidates:
            items.append({
                "item_id": candidate.ref_key,
                "kind": "CAPABILITY_CANDIDATE",
                "authority_class": "SYSTEM_RUNTIME_STATE",
                "source_identity": f"{candidate.capability_id}@{candidate.version}",
                "opaque_ref": candidate.ref_key,
                "content": candidate.model_dump(mode="json"),
                "inclusion_reason": "eligible registered capability candidate",
                "selection_mode": "RETRIEVED",
            })
        for result in planner_input.reusable_results:
            items.append({
                "item_id": result.ref_key,
                "kind": "SCIENTIFIC_RESULT",
                "authority_class": "SCIENTIFIC_RESULT",
                "source_identity": str(result.result_id),
                "opaque_ref": result.ref_key,
                "result_ref": str(result.result_id),
                "content": result.model_dump(mode="json"),
                "inclusion_reason": "authorized exact-result reuse candidate",
                "selection_mode": "CONTINUATION",
            })
        for index, constraint in enumerate(planner_input.explicit_constraints, start=1):
            items.append({
                "item_id": f"constraint_{index}",
                "kind": "USER_CONSTRAINT",
                "authority_class": "USER_CONSTRAINT",
                "source_identity": f"{planner_input.contract_version}:constraint:{index}",
                "opaque_ref": f"constraint_{index}",
                "content": constraint,
                "inclusion_reason": "explicit scientific constraint",
                "selection_mode": "EXPLICIT",
            })
        return items

    def _plan_context(
        self,
        unit: Any,
        project_id: str,
        refs: dict[str, ScientificObjectRef],
    ) -> dict[str, Any]:
        source_dataset_ids: set[str] = set()
        registered_fact_keys = {
            fact_key
            for tool in self.tool_registry.list_planner_visible_tools()
            for binding in build_tool_planner_metadata(tool).parameterBindings
            if binding.source is PlannerBindingSource.resource_fact
            for fact_key in binding.factKeys
        }
        resource_facts: dict[str, dict[str, Any]] = {}
        for ref_key, ref in refs.items():
            version = unit.agent2.scientific_objects.get_version(ref.version_id)
            for source in version.get("source_resource_refs_json") or []:
                if source.get("project_id") not in {None, project_id}:
                    raise CapabilityBindingFailed("source resource belongs to another project")
                if source.get("dataset_id"):
                    source_dataset_ids.add(str(source["dataset_id"]))
            canonical_metadata = dict(version.get("canonical_metadata_json") or {})
            source_resource_id = str(
                canonical_metadata.get("source_resource_id")
                or next(
                    (
                        source.get("resource_id")
                        for source in version.get("source_resource_refs_json") or []
                        if source.get("resource_id")
                    ),
                    "",
                )
            )
            bounded_facts = {
                key: canonical_metadata[key]
                for key in sorted(registered_fact_keys)
                if key in canonical_metadata
                and self._is_bounded_resource_fact(canonical_metadata[key])
            }
            resource_facts[ref_key] = {
                "object_id": str(ref.object_id),
                "version_id": str(ref.version_id),
                "object_type": ref.object_type,
                "resource_id": source_resource_id or None,
                "facts": bounded_facts,
            }
        datasets = unit.repositories.datasets.list_for_project(project_id)
        allowed = {str(item.get("id") or item.get("datasetId")) for item in datasets}
        if source_dataset_ids and not source_dataset_ids.issubset(allowed):
            raise CapabilityBindingFailed("scientific source dataset is not authorized")
        if len(source_dataset_ids) > 1:
            raise CapabilityBindingFailed("AnalysisPlan 0.2 requires one exact root dataset")
        if source_dataset_ids:
            dataset_id = next(iter(source_dataset_ids))
        elif datasets:
            dataset_id = str(datasets[0]["id"] if "id" in datasets[0] else datasets[0].get("datasetId"))
        else:
            raise CapabilityBindingFailed("an executable AnalysisPlan requires a project dataset")
        profiles = unit.repositories.data_profiles.list_for_dataset(dataset_id)
        if not profiles:
            raise CapabilityBindingFailed("an executable AnalysisPlan requires a persisted DataProfile")
        profile_record = profiles[0]
        profile_id = str(
            profile_record.get("profileId")
            or profile_record.get("id")
        )
        return {
            "dataset_id": dataset_id,
            "profile_id": profile_id,
            "profile": profile_record,
            "resource_facts": resource_facts,
        }

    @staticmethod
    def _is_bounded_resource_fact(value: Any) -> bool:
        if value is None or isinstance(value, bool):
            return value is not None
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            return math.isfinite(value)
        if isinstance(value, str):
            return len(value) <= 256
        return False

    @staticmethod
    def _snapshot_refs(snapshot: dict[str, Any]) -> dict[str, Any]:
        from mdi_api.scientific_objects.schemas import ScientificObjectRef
        result = {}
        for raw in [*(snapshot.get("selection_refs_json") or []), *(snapshot.get("active_scope_refs_json") or [])]:
            ref = ScientificObjectRef.model_validate(raw)
            result.setdefault(f"obj_{len(result) + 1}", ref)
        return result

    @staticmethod
    def _reauthorize_snapshot(unit: Any, turn: dict[str, Any], snapshot: dict[str, Any]) -> None:
        project_id = str(turn["project_id"])
        for ref in CapabilityPlanningProcessor._snapshot_refs(snapshot).values():
            logical = unit.agent2.scientific_objects.get_object(ref.object_id)
            version = unit.agent2.scientific_objects.get_version(ref.version_id)
            if str(logical["project_id"]) != project_id or version["scientific_object_id"] != ref.object_id or str(version["object_type"]) != ref.object_type or str(version["availability_status"]) not in {"AVAILABLE", "PARTIALLY_AVAILABLE"}:
                raise CapabilityBindingFailed("scientific source reference is unauthorized or unavailable")

    @staticmethod
    def _load_reusable_results(unit: Any, turn: dict[str, Any], decision: ResearchTurnDecision, snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
        requested = set(decision.reusable_result_ref_keys)
        received = next(
            (
                event
                for event in unit.agent2.research_turn_events.list_for_turn(turn["id"])
                if event["event_type"] == ResearchTurnEventType.TURN_RECEIVED.value
            ),
            None,
        )
        autonomy = ((received or {}).get("payload_json") or {}).get("autonomy") or {}
        autonomous_reuse = (
            autonomy.get("mode") == "BOUNDED_AUTONOMOUS"
            and bool(autonomy.get("assessment_signature"))
        )
        # A normal CONTINUE_ANALYSIS request means rerun/recompute, including
        # when the user changes parameters.  A persisted autonomous child is
        # different: its constraints parameterize the *new downstream*
        # capability selected from a durable Result (for example an MSD fit
        # window for diffusion).  Treating those constraints as a request to
        # recompute the parent evidence removes the only valid input binding
        # and defeats reuse-before-recompute.
        recompute = not autonomous_reuse and (
            decision.action == ResearchAction.CONTINUE_ANALYSIS
            or any(
                item.constraints
                for item in decision.scientific_requirements
            )
        )
        result: dict[str, dict[str, Any]] = {}
        project_id = str(turn["project_id"])
        for item in snapshot.get("referenced_result_refs_json") or []:
            key = item.get("candidate_key")
            snapshot_id = item.get("result_id")
            if not key or not snapshot_id or key not in requested:
                continue
            row = unit.agent2.scientific_result_snapshots.get(UUID(str(snapshot_id)))
            if str(row["project_id"]) != project_id:
                raise CapabilityBindingFailed("previous Result belongs to another project")
            bundle = ScientificResultBundle.model_validate(row["bundle_json"])
            output_refs = list(bundle.output_object_refs)
            artifact_ids_by_result_type: dict[str, list[str]] = {}
            artifact_metadata_by_id: dict[str, dict[str, Any]] = {}
            for result_item in bundle.result_items:
                if result_item.artifact_ids:
                    artifact_ids_by_result_type.setdefault(
                        result_item.result_type, []
                    ).extend(result_item.artifact_ids)
            for result_type, artifact_ids in artifact_ids_by_result_type.items():
                artifact_ids_by_result_type[result_type] = sorted(set(artifact_ids))
                for artifact_id in artifact_ids_by_result_type[result_type]:
                    artifact = unit.repositories.artifacts.get(artifact_id)
                    artifact_metadata_by_id[str(artifact_id)] = {
                        "type": artifact.get("type"),
                        "content_type": artifact.get("contentType")
                        or artifact.get("content_type"),
                        "metadata": artifact.get("metadata_json")
                        or artifact.get("metadataJson")
                        or {},
                    }
                    if (
                        str(artifact.get("projectId") or "") != project_id
                        or (
                            row.get("job_id")
                            and str(artifact.get("jobId") or "")
                            != str(row["job_id"])
                        )
                    ):
                        raise CapabilityBindingFailed(
                            "previous Result Artifact is unauthorized"
                        )
            for ref in output_refs:
                logical = unit.agent2.scientific_objects.get_object(ref.object_id)
                version = unit.agent2.scientific_objects.get_version(ref.version_id)
                if (
                    str(ref.project_id) != project_id
                    or str(logical["project_id"]) != project_id
                    or version["scientific_object_id"] != ref.object_id
                    or str(version["object_type"]) != ref.object_type
                    or str(version["availability_status"]) not in {"AVAILABLE", "PARTIALLY_AVAILABLE"}
                ):
                    raise CapabilityBindingFailed("previous Result output is unauthorized or unavailable")
            relevance = str(row["relevance_status"])
            result[key] = {
                "snapshot_id": row["id"],
                "relevance_status": relevance,
                "output_object_refs": output_refs,
                "result_types": sorted(artifact_ids_by_result_type),
                "artifact_ids_by_result_type": artifact_ids_by_result_type,
                "artifact_metadata_by_id": artifact_metadata_by_id,
                "usable": (
                    relevance == "CURRENT"
                    and bool(output_refs or artifact_ids_by_result_type)
                    and not recompute
                ),
            }
        return result

    @staticmethod
    def _enforce_autonomy_resolution(
        unit: Any, turn_id: UUID, resolution: Any, registries: Any
    ) -> Any:
        received = next(
            (
                event
                for event in unit.agent2.research_turn_events.list_for_turn(turn_id)
                if event["event_type"] == ResearchTurnEventType.TURN_RECEIVED.value
            ),
            None,
        )
        autonomy = ((received or {}).get("payload_json") or {}).get("autonomy") or {}
        if (
            autonomy.get("mode") != "BOUNDED_AUTONOMOUS"
            or not autonomy.get("assessment_signature")
        ):
            return resolution
        from mdi_api.research_agent.autonomy.policy import CapabilityAutonomyPolicy
        from mdi_api.research_agent.autonomy.schemas import AutonomyPolicy

        capability_id = str(autonomy.get("selected_capability_id") or "")
        version = str(autonomy.get("selected_capability_version") or "1.0")
        manifest = registries.capabilities.require(capability_id, version)
        policy = AutonomyPolicy.model_validate(autonomy.get("policy") or {})
        current = CapabilityAutonomyPolicy(policy).qualification_snapshot(manifest)
        recorded = autonomy.get("qualification") or {}
        if (
            not current.allowed_for_autonomy
            or recorded.get("evidence_fingerprint") != current.evidence_fingerprint
            or recorded.get("scientific_contract_fingerprint")
            != current.scientific_contract_fingerprint
        ):
            raise CapabilityPlanInvalid(
                "Autonomous capability qualification is stale or insufficient",
                code="AUTONOMY_QUALIFICATION_INVALID",
            )
        selected = [
            item
            for item in resolution.candidates
            if item.capability_id == capability_id
            and item.capability_version == version
        ]
        if not selected:
            raise CapabilityPlanInvalid(
                "Persisted autonomous capability is no longer eligible",
                code="AUTONOMY_CAPABILITY_INELIGIBLE",
            )
        return resolution.model_copy(update={"candidates": selected})

    @staticmethod
    def _enforce_autonomy_plan_budget(turn: dict[str, Any], plan: Any) -> None:
        autonomy = dict(turn.get("_autonomy") or {})
        if not autonomy:
            return
        policy = autonomy.get("policy") or {}
        limit = int(policy.get("max_dependency_steps_per_cycle") or 4)
        if len(plan.steps) > limit:
            raise CapabilityPlanInvalid(
                "Autonomous capability plan exceeds its persisted step budget",
                code="AUTONOMY_DEPENDENCY_STEP_LIMIT_REACHED",
            )

    @staticmethod
    def _turn_autonomy(unit: Any, turn_id: UUID) -> dict[str, Any]:
        received = next(
            (
                event
                for event in unit.agent2.research_turn_events.list_for_turn(turn_id)
                if event["event_type"] == ResearchTurnEventType.TURN_RECEIVED.value
            ),
            None,
        )
        return dict(
            ((received or {}).get("payload_json") or {}).get("autonomy") or {}
        )

    def _fail(self, turn_id: UUID, code: str, summary: str, *, target: ResearchTurnStatus = ResearchTurnStatus.PLAN_REJECTED) -> None:
        with self.repository_factory.unit_of_work() as unit:
            turn = unit.agent2.research_turns.get_for_update(turn_id)
            if turn["status"] != ResearchTurnStatus.PLANNING.value:
                return
            updated = unit.agent2.research_turns.compare_and_set_status(turn_id, expected_status=ResearchTurnStatus.PLANNING.value, expected_version=int(turn["row_version"]), target_status=target.value, completed_at=datetime.now(timezone.utc), error_code=code, error_summary=summary[:1000])
            event_type = ResearchTurnEventType.TURN_FAILED if target == ResearchTurnStatus.FAILED else ResearchTurnEventType.CAPABILITY_PLAN_REJECTED
            self._event(unit, turn_id, event_type, {"status": updated["status"], "error_code": code})

    @staticmethod
    def _event(unit: Any, turn_id: UUID, event_type: ResearchTurnEventType, payload: dict[str, Any]) -> None:
        unit.agent2.research_turn_events.append_turn_event({"id": uuid4(), "turn_id": turn_id, "sequence_no": unit.agent2.research_turn_events.next_sequence_no(turn_id), "event_type": event_type.value, "payload_json": payload, "created_at": datetime.now(timezone.utc)})
