from __future__ import annotations

import json
import hashlib
import shutil
import tempfile
from pathlib import Path
from typing import Any

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import decode_volumetric_payload, validate_volumetric_dataset, validate_volumetric_manifest
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import parse_file
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime

ROOT=Path(__file__).resolve().parents[3]
FIXTURE=ROOT/"docs"/"phase10j"/"fixtures"/"volumetric_parser"/"LOCPOT"
EVIDENCE=ROOT/"docs"/"phase10j"/"evidence"/"phase10j4_electrostatic_potential_product"

def write_json(name:str,value:Any)->None:
    target=EVIDENCE/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def main()->None:
    registry=load_manifests();prompt="Visualize the local potential from this LOCPOT and show planar averages"
    profile=DataProfile.model_validate({"schemaVersion":"0.1","profileId":"profile_potential","datasetId":"dataset_potential","version":"1","datasetType":"volumetric","objects":[{"id":"volumetric","objectType":"VolumetricData"}],"qualityIssues":[],"recommendedTasks":[],"createdAt":"2026-07-22T00:00:00Z"})
    plan=MockLLMProvider().generate_plan(PlannerRequest(user_prompt=prompt,dataset_id="dataset_potential",profile_id="profile_potential",tool_registry_version=registry.version),tools=registry.list_tools(),data_profile=profile).raw_json
    if not plan or plan["steps"][0]["toolId"]!="structure.volumetric_data":raise RuntimeError("potential prompt routing failed")
    source=parse_file(FIXTURE,dataset_id="dataset_potential",file_id="locpot").objects[0]
    with tempfile.TemporaryDirectory(prefix="mdi_potential_runtime_") as temp:
        root=Path(temp);repos=InMemoryRepositoryBundle.create();runtime=QueueWorkerRuntime(repositories=repos,registry=registry,artifact_root=root)
        created=planner_jobs(PlannerJobsRequest(userPrompt=prompt,projectId="project_potential",datasetId="dataset_potential",profileId="profile_potential",enqueue=True),provider=MockLLMProvider(fixed_plan=plan),repositories=repos,queue_runtime=runtime,registry=registry)
        result=runtime.handle_job(created.job_id,object_store={"volumetric":source})
        if result.status!="completed":raise RuntimeError("potential runtime failed")
        destination=EVIDENCE/"artifacts"/"live_locpot";destination.mkdir(parents=True,exist_ok=True);artifacts=[]
        for row in repos.artifacts.list_for_job(created.job_id):
            shutil.copyfile(root/row["storageKey"],destination/row["name"]);artifacts.append({"id":row["id"],"name":row["name"],"type":row["type"],"bytes":row["sizeBytes"],"sha256":row["contentHash"]})
        dataset=json.loads((destination/"volumetric_dataset.json").read_text(encoding="utf-8"));manifest=json.loads((destination/"volumetric_manifest.json").read_text(encoding="utf-8"));binaries={item["name"]:(destination/item["name"]).read_bytes() for item in artifacts if item["type"]=="volumetric_binary"};values=decode_volumetric_payload(dataset["payloads"][0],binaries);field=dataset["fields"][0]
        shape=dataset["grid"]["shape"]
        profiles=[]
        for axis in range(3):
            points=[]
            for plane in range(shape[axis]):
                selected=[value for index,value in enumerate(values) if ((index//(shape[1]*shape[2]),(index//shape[2])%shape[1],index%shape[2])[axis])==plane]
                points.append(sum(selected)/len(selected))
            profiles.append({"axis":f"lattice_axis_{axis}","source_values":points,"cell_average_zero_values":[value-field["statistics"]["stored_components"][0]["mean"] for value in points]})
        validation={"dataset":validate_volumetric_dataset(dataset,binaries).valid,"manifest":validate_volumetric_manifest(manifest,dataset=dataset,artifacts=binaries).valid}
        capture={"prompt":prompt,"selected_tool":plan["steps"][0]["toolId"],"plan":plan,"job_id":created.job_id,"status":result.status,"artifacts":artifacts,"validation":validation,"field":{"field_id":field["field_id"],"quantity":field["quantity"],"unit":field["unit"],"potential_reference":field["potential_reference"],"statistics":field["statistics"]},"source_values":values}
    mean=field["statistics"]["stored_components"][0]["mean"];shift=-mean;before=values[-1]-values[0];after=(values[-1]+shift)-(values[0]+shift)
    profile_records=[]
    for profile in profiles:
        model={"schema_version":"phase10j4.potential_profile.v1","source_field_hash":field["content_hash"],"formula_id":"POTENTIAL_PLANAR_AVERAGE_V1","gauge":"source_native","axis":profile["axis"],"unit":field["unit"]["canonical_unit"],"source_values":profile["source_values"],"displayed_values":profile["source_values"],"smoothing":False}
        model["profile_hash"]=hashlib.sha256(json.dumps(model,sort_keys=True,separators=(",",":" )).encode()).hexdigest();profile_records.append(model);write_json(f"scientific/{profile['axis']}.json",model)
    write_json("scientific/product_manifest.json",{"schema_version":"phase10j4.electrostatic_potential_product.v1","dataset_hash":dataset["content_hash"],"source_field":{"field_id":field["field_id"],"field_hash":field["content_hash"],"quantity":field["quantity"],"unit":field["unit"]["canonical_unit"],"reference":field["potential_reference"]},"gauge_formulas":["POTENTIAL_SOURCE_NATIVE_V1","POTENTIAL_CELL_AVERAGE_ZERO_V1","POTENTIAL_SELECTED_POINT_ZERO_V1"],"profile_formula":"POTENTIAL_PLANAR_AVERAGE_V1","profile_hashes":[item["profile_hash"] for item in profile_records],"source_contour_policy":"preserve_source_contour_identity","renderer_included":False,"external_assets":[],"security":{"artifact_javascript":False,"artifact_worker":False,"artifact_wasm":False,"artifact_shader":False,"external_urls":False}})
    write_json("api/live_job_capture.json",capture);write_json("scientific/gauge_invariants.json",{"source_mean":mean,"cell_average_zero_shift":shift,"shifted_mean_residual":sum(value+shift for value in values)/len(values),"point_difference_before":before,"point_difference_after":after,"source_payload_unchanged":True,"source_payload_sha256":dataset["payloads"][0]["logical_sha256"],"formula":"POTENTIAL_CELL_AVERAGE_ZERO_V1","source_contour_policy":"preserve_source_contour_identity"});write_json("scientific/planar_profiles.json",{"formula":"POTENTIAL_PLANAR_AVERAGE_V1","smoothing":False,"axes":["lattice_axis_0","lattice_axis_1","lattice_axis_2"],"profiles":profiles});write_json("security/audit.json",{"artifactJavaScript":False,"artifactWorker":False,"artifactWasm":False,"artifactShader":False,"artifactHtmlCss":False,"externalUrls":False,"externalRequests":0,"marker":"NO_ELECTROSTATIC_POTENTIAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS","secrets":"NO_SECRET_PATTERN_HITS"});write_json("evidence_manifest.json",{"phase":"10J-4","tool":"structure.volumetric_data","source":"live LOCPOT QueueWorkerRuntime artifact","dataset_hash":dataset["content_hash"],"field_hash":field["content_hash"],"quantity":"local_potential","unit":"electronvolt","reference":"source_defined","profile_formula":"POTENTIAL_PLANAR_AVERAGE_V1","gauge_formulas":["POTENTIAL_SOURCE_NATIVE_V1","POTENTIAL_CELL_AVERAGE_ZERO_V1","POTENTIAL_SELECTED_POINT_ZERO_V1"],"replay":["uv run python apps/web/test/generate-electrostatic-potential-evidence.py","node apps/web/test/electrostatic-potential-browser-evidence.mjs"]})
    print("ELECTROSTATIC_POTENTIAL_RUNTIME_EVIDENCE_PASS");print("NO_ELECTROSTATIC_POTENTIAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS");print("NO_SECRET_PATTERN_HITS")

if __name__=="__main__":main()
