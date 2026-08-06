# Authority Map

| Stage | Authority | Persistence/runtime |
| --- | --- | --- |
| Source/upload | source record + resource hash | existing dataset API/storage |
| DataProfile 2.0 | data semantic authority | data_profiles |
| AnalysisIntent 1.0 | bounded goal authority | analysis_intents |
| EligibilityResolution 1.0 | capability applicability | capability_eligibility_resolutions |
| AnalysisPlan 0.1/0.2 | declared execution | analysis_plans |
| QueueWorkerRuntime | orchestration | jobs/tool_calls/dependency records |
| Adapter | scientific calculation | Tool Registry validated invocation |
| Artifact + lineage | persisted scientific result | PostgreSQL metadata + MinIO payload |
| Interpretation/evidence | grounded narrative | scientific interpretation tables |
| Workspace | reference/navigation/presentation | scientific_workspaces + panels + revisions |
| Report | selected delivery snapshot | existing reports |
| Recipe | non-executable replay declaration | existing visualization_recipes |
