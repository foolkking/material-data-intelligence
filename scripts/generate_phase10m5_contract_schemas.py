from __future__ import annotations

import json
from pathlib import Path

from mdi_schemas import (
    RecipeReplayManifest,
    ReportCompositionRequest,
    ReportCompositionSnapshot,
    ReportExportManifest,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "packages" / "schemas" / "json"
SCHEMAS = {
    "report-composition-request-v1.schema.json": ReportCompositionRequest,
    "report-composition-snapshot-v1.schema.json": ReportCompositionSnapshot,
    "recipe-replay-manifest-v1.schema.json": RecipeReplayManifest,
    "report-export-manifest-v1.schema.json": ReportExportManifest,
}


def main() -> None:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for filename, model in SCHEMAS.items():
        payload = model.model_json_schema(mode="validation")
        payload["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        payload["$id"] = f"https://mdi.local/schemas/{filename}"
        target = SCHEMA_DIR / filename
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(target.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
