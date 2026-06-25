from __future__ import annotations

import mdi_schemas


CORE_SCHEMA_EXPORTS = {
    "ArtifactType",
    "DisplayTarget",
    "ToolCategory",
    "ToolDomain",
    "ImplementationSource",
    "MaterialObjectType",
    "JobStatus",
    "JobEventStatus",
    "RegisteredTool",
    "ToolInputSchema",
    "ToolInputOption",
    "ToolOutputSchema",
    "ToolExecutionRequest",
    "ToolCall",
    "Artifact",
    "AnalysisPlan",
    "AnalysisStep",
    "DataProfile",
    "VisualizationRecipe",
}


def test_python_schema_package_exports_core_types():
    assert CORE_SCHEMA_EXPORTS <= set(mdi_schemas.__all__)
    for export_name in CORE_SCHEMA_EXPORTS:
        assert hasattr(mdi_schemas, export_name)


def test_typescript_schema_entry_exports_core_types(repo_root):
    source = (repo_root / "packages" / "schemas" / "src" / "index.ts").read_text(encoding="utf-8")

    for export_name in CORE_SCHEMA_EXPORTS:
        assert f"export type {export_name}" in source or f"export const {export_name[0].lower()}{export_name[1:]}" in source

