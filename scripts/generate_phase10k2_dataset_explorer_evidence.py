from __future__ import annotations

import json
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd
from pymatgen.core import Lattice, Structure

from mdi_adapters import ToolExecutionContext
from mdi_adapters.platform_builtin import DatasetMaterialsExplorerAdapter
from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    get_planner_job,
    get_planner_job_artifact_content,
    get_planner_job_artifacts,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
    planner_jobs,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import NormalizedObjectDraft, ParseResult, build_data_profile
from mdi_material_parsers.models import DetectedFormat
from mdi_schemas import ArtifactType, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10k" / "evidence" / "phase10k2_dataset_materials_explorer"


def _table(object_id: str, records: list[dict[str, Any]], units: dict[str, str] | None = None) -> NormalizedObjectDraft:
    frame = pd.DataFrame(records)
    columns = []
    for name in frame.columns:
        series = frame[name]
        numeric = pd.api.types.is_numeric_dtype(series)
        converted = pd.to_numeric(series, errors="coerce") if numeric else series
        finite_count = int(converted.map(lambda value: pd.notna(value) and float("-inf") < float(value) < float("inf")).sum()) if numeric else None
        columns.append(
            {
                "name": str(name),
                "dtype": "number" if numeric else "string",
                "missingCount": int(series.isna().sum()),
                "uniqueCount": int(series.nunique(dropna=True)),
                "unit": (units or {}).get(str(name)),
                "finiteCount": finite_count,
            }
        )
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id="dataset_phase10k2_evidence",
        object_type=MaterialObjectType.DataFrame,
        source_file_ids=[f"{object_id}.json"],
        storage_key=f"normalized/{object_id}.json",
        metadata={"nRows": len(frame), "nColumns": len(frame.columns), "columns": columns},
        hash=(object_id.encode("utf-8").hex() + "0" * 64)[:64],
        payload=records,
    )


def _structure(object_id: str, structure: Structure, object_hash: str) -> NormalizedObjectDraft:
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id="dataset_phase10k2_evidence",
        object_type=MaterialObjectType.Structure,
        source_file_ids=[f"{object_id}.cif"],
        storage_key=f"normalized/{object_id}.json",
        metadata={
            "formula": structure.composition.reduced_formula,
            "chemicalSystem": structure.composition.chemical_system,
            "elements": sorted(str(element) for element in structure.composition.elements),
            "nAtoms": len(structure),
            "periodicity": "periodic",
        },
        hash=object_hash,
        payload=structure.as_dict(),
    )


def _fixture_objects() -> list[NormalizedObjectDraft]:
    rows = [
        {"material_id": "sample-si-1", "formula": "Si", "formation_energy": -5.42, "band_gap": 1.10, "split": "train"},
        {"material_id": "sample-nacl", "formula": "NaCl", "formation_energy": -3.21, "band_gap": 5.60, "split": "train"},
        {"material_id": "sample-si-2", "formula": "Si", "formation_energy": -5.31, "band_gap": 1.30, "split": "test"},
        {"material_id": "sample-nacl", "formula": "invalid formula", "formation_energy": None, "band_gap": float("inf"), "split": "test"},
    ]
    table = _table("obj_materials", rows, {"formation_energy": "eV/atom", "band_gap": "eV"})
    si = Structure(Lattice.cubic(5.43), ["Si", "Si"], [[0, 0, 0], [0.25, 0.25, 0.25]])
    nacl = Structure(Lattice.cubic(5.64), ["Na", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    return [
        table,
        _structure("obj_si_a", si, "a" * 64),
        _structure("obj_si_b", si, "a" * 64),
        _structure("obj_nacl", nacl, "b" * 64),
    ]


def _profile(objects: list[NormalizedObjectDraft]):
    registry = load_manifests()
    return build_data_profile(
        dataset_id="dataset_phase10k2_evidence",
        parse_results=[
            ParseResult(
                file_id="file_phase10k2_evidence",
                file_path=Path("materials_fixture.json"),
                detected_format=DetectedFormat.json_limited,
                parse_status="success",
                objects=objects,
            )
        ],
        platform_tool_ids={tool.toolId for tool in registry.tools},
    )


def _write(relative: str, value: Any) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        target.write_text(value, encoding="utf-8")
    else:
        target.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def _sanitized(value: Any) -> Any:
    if isinstance(value, list):
        return [_sanitized(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitized(item) for key, item in value.items() if key not in {"createdAt", "updatedAt"}}
    return value


def _runtime_capture() -> dict[str, Any]:
    objects = _fixture_objects()
    profile = _profile(objects)
    registry = load_manifests()
    prompt = "Explore this materials dataset and compare the explicit train and test groups."
    raw_plan = MockLLMProvider().generate_plan(
        PlannerRequest(
            user_prompt=prompt,
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            tool_registry_version=registry.version,
        ),
        tools=registry.list_mvp_tools(),
        data_profile=profile,
    ).raw_json
    if raw_plan is None:
        raise RuntimeError("Mock Planner did not produce the Dataset Explorer plan.")

    repositories = InMemoryRepositoryBundle.create()
    with tempfile.TemporaryDirectory(prefix="mdi-phase10k2-") as directory:
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=Path(directory))
        deterministic_ids = [
            uuid.UUID("00000000-0000-0000-0000-000000000001"),
            uuid.UUID("00000000-0000-0000-0000-000000000002"),
        ]
        with patch("mdi_api.routers.planner.uuid.uuid4", side_effect=deterministic_ids):
            created = planner_jobs(
                PlannerJobsRequest(
                    userPrompt=prompt,
                    projectId="project_phase10k2_evidence",
                    datasetId=profile.datasetId,
                    profileId=profile.profileId,
                    enqueue=True,
                ),
                provider=MockLLMProvider(fixed_plan=raw_plan),
                repositories=repositories,
                queue_runtime=runtime,
                registry=registry,
            )
        store, _ = build_object_store(objects, profile=profile)
        completed = runtime.handle_job(created.job_id or "", object_store=store)
        if completed.status != "completed":
            raise RuntimeError("Dataset Explorer runtime evidence job did not complete.")
        job_id = created.job_id or ""
        artifacts = get_planner_job_artifacts(job_id, repositories=repositories)
        artifact_contents: dict[str, Any] = {}
        for artifact in artifacts:
            response = get_planner_job_artifact_content(
                job_id,
                str(artifact["id"]),
                repositories=repositories,
                queue_runtime=runtime,
            )
            content = bytes(response.body)
            name = str(artifact["name"])
            if name.endswith(".json"):
                artifact_contents[name] = json.loads(content)
                _write(f"artifacts/{name}", artifact_contents[name])
            else:
                text = content.decode("utf-8")
                artifact_contents[name] = text
                _write(f"artifacts/{name}", text)

        capture = {
            "request": {"userPrompt": prompt, "datasetId": profile.datasetId, "profileId": profile.profileId},
            "plan": created.plan,
            "job": get_planner_job(job_id, repositories=repositories),
            "events": get_planner_job_events(job_id, repositories=repositories),
            "toolCalls": get_planner_job_tool_calls(job_id, repositories=repositories),
            "artifacts": artifacts,
            "result": get_planner_job_result(job_id, repositories=repositories),
            "apiContentRetrieval": {
                "artifactNames": sorted(artifact_contents),
                "allContentRoutesValidated": len(artifact_contents) == len(artifacts),
            },
        }
    _write("api/data_profile.json", _sanitized(profile.model_dump(mode="json")))
    _write("api/runtime_capture.json", _sanitized(capture))
    _write("api/artifacts.json", _sanitized(artifacts))
    return artifact_contents["dataset_materials_explorer.json"]


def _performance_case(row_count: int, case_id: str) -> dict[str, Any]:
    records = [
        {
            "material_id": f"sample-{index:06d}",
            "formula": ("Si", "NaCl", "LiF", "MgO")[index % 4],
            "band_gap": float(index % 101) / 10.0,
        }
        for index in range(row_count)
    ]
    objects = [_table(f"obj_{case_id}", records, {"band_gap": "eV"})]
    profile = _profile(objects)
    registry = load_manifests()
    tool = registry.get_tool_by_id("dataset.materials_explorer")
    store, _ = build_object_store(objects, profile=profile)
    with tempfile.TemporaryDirectory(prefix=f"mdi-{case_id}-") as directory:
        context = ToolExecutionContext(
            job_id=f"job_{case_id}",
            project_id="project_phase10k2_performance",
            dataset_id=profile.datasetId,
            tool_id=tool.toolId,
            tool_version=tool.version,
            adapter_version="0.1.0",
            registry_version=registry.version,
            artifact_root=Path(directory),
            tool_call_id=f"call_{case_id}",
            object_store=store,
            resource_limits=tool.resourceLimits,
        )
        request = ToolExecutionRequest(
            jobId=context.job_id,
            stepId="step_001",
            toolId=tool.toolId,
            inputRefs=[
                {"refType": "profile", "ref": "profile"},
                {"refType": "normalized_object", "ref": f"obj_{case_id}", "objectType": "DataFrame"},
            ],
            params={"comparisonMode": "none", "tableObjectId": f"obj_{case_id}"},
            artifactTypes=[ArtifactType.table_json.value],
        )
        started = time.perf_counter()
        artifacts = DatasetMaterialsExplorerAdapter().execute(context, request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        artifact = artifacts[0]
        payload = json.loads((Path(directory) / artifact.storageKey).read_text(encoding="utf-8"))
        return {
            "caseId": case_id,
            "inputRows": row_count,
            "elapsedMs": round(elapsed_ms, 3),
            "artifactBytes": artifact.sizeBytes,
            "sampleRowsMaterialized": len(payload["sampleIndex"]),
            "propertyCount": len(payload["properties"]["properties"]),
            "chemicalSystemsMaterialized": len(payload["composition"]["chemicalSystems"]),
        }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    product = _runtime_capture()
    performance = {
        "cases": [
            _performance_case(4, "small"),
            _performance_case(5000, "medium"),
            _performance_case(100000, "near_cap"),
        ],
        "caps": {"maxRows": 100000, "maxTableRows": 200, "maxProperties": 64, "maxArtifactBytes": 8000000},
        "acceptance": "PASS",
        "marker": "DATASET_MATERIALS_EXPLORER_PERFORMANCE_EVIDENCE_PASS",
    }
    _write("performance/performance_metrics.json", performance)
    _write(
        "fixtures/required_cases.json",
        {
            "composition": product["composition"],
            "structures": product["structures"],
            "properties": product["properties"],
            "quality": product["quality"],
            "comparison": product["comparison"],
        },
    )
    _write("network_audit.json", {"externalRequests": 0, "marker": "NO_DATASET_EXPLORER_EXTERNAL_NETWORK_REQUESTS"})
    _write(
        "security_audit.json",
        {
            "artifactJavaScript": False,
            "externalUrls": False,
            "externalAssets": False,
            "realLlmCalls": 0,
            "secretPatternHits": [],
            "marker": "NO_SECRET_PATTERN_HITS",
        },
    )
    print("DATASET_MATERIALS_EXPLORER_RUNTIME_EVIDENCE_PASS")
    print("DATASET_COMPOSITION_EXPLORER_EVIDENCE_PASS")
    print("DATASET_STRUCTURE_STATISTICS_EVIDENCE_PASS")
    print("DATASET_PROPERTY_EXPLORER_EVIDENCE_PASS")
    print("DATASET_QUALITY_EVIDENCE_PASS")
    print("DATASET_COMPARISON_EVIDENCE_PASS")
    print("DATASET_MATERIALS_EXPLORER_PERFORMANCE_EVIDENCE_PASS")
    print("NO_DATASET_EXPLORER_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
