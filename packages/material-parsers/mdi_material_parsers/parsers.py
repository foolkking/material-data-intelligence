from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from ase import Atoms
from ase.io import read as ase_read
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor

from mdi_artifact_core import content_hash, stable_json_dumps
from mdi_schemas import MaterialObjectType

from .detector import detect_format
from .models import DetectedFormat, NormalizedObjectDraft, ParseResult


def parse_file(path: str | Path, *, dataset_id: str, file_id: str | None = None) -> ParseResult:
    file_path = Path(path)
    detected_format = detect_format(file_path)
    resolved_file_id = file_id or _file_id(file_path)
    try:
        if detected_format in {DetectedFormat.cif, DetectedFormat.poscar}:
            structure = Structure.from_file(file_path)
            return ParseResult(
                file_id=resolved_file_id,
                file_path=file_path,
                detected_format=detected_format,
                parse_status="success",
                objects=[_structure_object(structure, dataset_id, resolved_file_id, detected_format.value)],
            )
        if detected_format == DetectedFormat.csv:
            dataframe = _coerce_numeric_like_columns(pd.read_csv(file_path))
            return ParseResult(
                file_id=resolved_file_id,
                file_path=file_path,
                detected_format=detected_format,
                parse_status="success",
                objects=[_dataframe_object(dataframe, dataset_id, resolved_file_id, detected_format.value)],
            )
        if detected_format == DetectedFormat.json_limited:
            return _parse_json_limited(file_path, dataset_id=dataset_id, file_id=resolved_file_id)
        if detected_format in {DetectedFormat.xyz, DetectedFormat.extxyz}:
            return _parse_xyz(file_path, dataset_id=dataset_id, file_id=resolved_file_id, detected_format=detected_format)
        if detected_format == DetectedFormat.archive:
            return _parse_zip_archive(file_path, dataset_id=dataset_id, file_id=resolved_file_id)
        return ParseResult(
            file_id=resolved_file_id,
            file_path=file_path,
            detected_format=detected_format,
            parse_status="unsupported",
            error_code="FORMAT_UNSUPPORTED",
            error_message=f"No MVP parser is implemented for {detected_format.value}.",
        )
    except Exception as exc:
        return ParseResult(
            file_id=resolved_file_id,
            file_path=file_path,
            detected_format=detected_format,
            parse_status="failed",
            error_code="PARSE_FAILED",
            error_message=str(exc),
        )


def parse_dataset(paths: Iterable[str | Path], *, dataset_id: str) -> tuple[list[ParseResult], list[NormalizedObjectDraft]]:
    results = [parse_file(path, dataset_id=dataset_id) for path in paths]
    objects = [obj for result in results for obj in result.objects]
    return results, objects


def _parse_xyz(
    file_path: Path,
    *,
    dataset_id: str,
    file_id: str,
    detected_format: DetectedFormat,
) -> ParseResult:
    atoms = ase_read(file_path)
    if isinstance(atoms, list):
        atoms = atoms[0]
    if not isinstance(atoms, Atoms):
        raise ValueError("ASE did not return an Atoms object.")
    if detected_format == DetectedFormat.extxyz and atoms.cell is not None and atoms.cell.volume > 0:
        structure = AseAtomsAdaptor.get_structure(atoms)
        objects = [_structure_object(structure, dataset_id, file_id, detected_format.value)]
    else:
        objects = [_atoms_object(atoms, dataset_id, file_id, detected_format.value)]
    return ParseResult(
        file_id=file_id,
        file_path=file_path,
        detected_format=detected_format,
        parse_status="success",
        objects=objects,
    )


def _parse_zip_archive(
    file_path: Path,
    *,
    dataset_id: str,
    file_id: str,
    max_files: int = 100,
    max_uncompressed_bytes: int = 50 * 1024 * 1024,
    max_depth: int = 5,
) -> ParseResult:
    inner_results: list[ParseResult] = []
    with zipfile.ZipFile(file_path) as archive:
        members = [member for member in archive.infolist() if not member.is_dir()]
        if len(members) > max_files:
            return ParseResult(
                file_id=file_id,
                file_path=file_path,
                detected_format=DetectedFormat.archive,
                parse_status="failed",
                error_code="ARCHIVE_TOO_MANY_FILES",
                error_message=f"ZIP contains {len(members)} files; max_files={max_files}.",
            )
        total_size = sum(member.file_size for member in members)
        if total_size > max_uncompressed_bytes:
            return ParseResult(
                file_id=file_id,
                file_path=file_path,
                detected_format=DetectedFormat.archive,
                parse_status="failed",
                error_code="ARCHIVE_TOO_LARGE",
                error_message=f"ZIP uncompressed size exceeds {max_uncompressed_bytes} bytes.",
            )
        with tempfile.TemporaryDirectory(prefix="mdi_zip_") as tmp_dir:
            root = Path(tmp_dir).resolve()
            for idx, member in enumerate(members):
                safe_name = _safe_archive_name(member.filename, max_depth=max_depth)
                if safe_name is None:
                    inner_results.append(
                        ParseResult(
                            file_id=f"{file_id}_member_{idx + 1}",
                            file_path=file_path,
                            detected_format=DetectedFormat.unknown,
                            parse_status="failed",
                            error_code="ARCHIVE_UNSAFE_PATH",
                            error_message=f"Unsafe ZIP member path: {member.filename}",
                        )
                    )
                    continue
                target = (root / safe_name).resolve()
                if not target.is_relative_to(root):
                    inner_results.append(
                        ParseResult(
                            file_id=f"{file_id}_member_{idx + 1}",
                            file_path=file_path,
                            detected_format=DetectedFormat.unknown,
                            parse_status="failed",
                            error_code="ARCHIVE_UNSAFE_PATH",
                            error_message=f"Unsafe ZIP member path: {member.filename}",
                        )
                    )
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(member))
                inner_results.append(parse_file(target, dataset_id=dataset_id, file_id=f"{file_id}_member_{idx + 1}"))

    objects = [obj for result in inner_results for obj in result.objects]
    if objects and all(result.parse_status == "success" for result in inner_results):
        status = "success"
    elif objects:
        status = "partial"
    else:
        status = "unsupported"
    return ParseResult(
        file_id=file_id,
        file_path=file_path,
        detected_format=DetectedFormat.archive,
        parse_status=status,
        objects=objects,
        error_code=None if status == "success" else "ARCHIVE_PARTIAL_OR_UNSUPPORTED",
        error_message=None if status == "success" else "One or more ZIP members could not be parsed.",
    )


def _parse_json_limited(file_path: Path, *, dataset_id: str, file_id: str) -> ParseResult:
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if _looks_like_structure_dict(data):
        structure = Structure.from_dict(data)
        objects = [_structure_object(structure, dataset_id, file_id, "json_limited")]
    elif _looks_like_table_json(data):
        dataframe = pd.DataFrame(data)
        objects = [_dataframe_object(dataframe, dataset_id, file_id, "json_limited")]
    else:
        return ParseResult(
            file_id=file_id,
            file_path=file_path,
            detected_format=DetectedFormat.json_limited,
            parse_status="unsupported",
            error_code="JSON_LIMITED_UNSUPPORTED",
            error_message="Only pymatgen Structure JSON and simple table JSON are supported in MVP.",
        )
    return ParseResult(
        file_id=file_id,
        file_path=file_path,
        detected_format=DetectedFormat.json_limited,
        parse_status="success",
        objects=objects,
    )


def _structure_object(structure: Structure, dataset_id: str, file_id: str, detected_format: str) -> NormalizedObjectDraft:
    payload = structure.as_dict()
    digest = content_hash(stable_json_dumps(payload))
    object_id = f"obj_structure_{digest[:12]}"
    metadata = {
        "formula": structure.composition.reduced_formula,
        "elements": sorted({element.symbol for element in structure.composition.elements}),
        "chemicalSystem": "-".join(sorted({element.symbol for element in structure.composition.elements})),
        "nAtoms": len(structure),
        "latticeVolume": structure.lattice.volume,
        "periodicity": "periodic",
        "detectedFormat": detected_format,
    }
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id=dataset_id,
        object_type=MaterialObjectType.Structure,
        source_file_ids=[file_id],
        storage_key=f"normalized/{object_id}/structure.json",
        metadata=metadata,
        hash=digest,
        payload=payload,
    )


def _atoms_object(atoms: Atoms, dataset_id: str, file_id: str, detected_format: str) -> NormalizedObjectDraft:
    payload = {
        "symbols": atoms.get_chemical_symbols(),
        "positions": atoms.get_positions().tolist(),
        "cell": atoms.cell.array.tolist(),
        "pbc": atoms.pbc.tolist(),
    }
    digest = content_hash(stable_json_dumps(payload))
    object_id = f"obj_atoms_{digest[:12]}"
    metadata = {
        "formula": atoms.get_chemical_formula(),
        "elements": sorted(set(atoms.get_chemical_symbols())),
        "chemicalSystem": "-".join(sorted(set(atoms.get_chemical_symbols()))),
        "nAtoms": len(atoms),
        "periodicity": "non_periodic",
        "detectedFormat": detected_format,
    }
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id=dataset_id,
        object_type=MaterialObjectType.Atoms,
        source_file_ids=[file_id],
        storage_key=f"normalized/{object_id}/atoms.json",
        metadata=metadata,
        hash=digest,
        payload=payload,
    )


def _dataframe_object(dataframe: pd.DataFrame, dataset_id: str, file_id: str, detected_format: str) -> NormalizedObjectDraft:
    payload = dataframe.to_dict(orient="records")
    digest = content_hash(stable_json_dumps(payload))
    object_id = f"obj_dataframe_{digest[:12]}"
    metadata = {
        "nRows": int(dataframe.shape[0]),
        "nColumns": int(dataframe.shape[1]),
        "columns": [_column_metadata(dataframe, column) for column in dataframe.columns],
        "detectedFormat": detected_format,
    }
    return NormalizedObjectDraft(
        id=object_id,
        dataset_id=dataset_id,
        object_type=MaterialObjectType.DataFrame,
        source_file_ids=[file_id],
        storage_key=f"normalized/{object_id}/data.json",
        metadata=metadata,
        hash=digest,
        payload=payload,
    )


def _coerce_numeric_like_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    converted = dataframe.copy()
    for column in converted.columns:
        series = converted[column]
        if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
            continue
        non_null = series.dropna()
        if non_null.empty:
            continue
        numeric = pd.to_numeric(non_null, errors="coerce")
        if float(numeric.notna().mean()) >= 0.95:
            converted[column] = pd.to_numeric(series, errors="coerce")
    return converted


def _column_metadata(dataframe: pd.DataFrame, column: str) -> dict[str, Any]:
    series = dataframe[column]
    return {
        "name": str(column),
        "dtype": _dtype_name(series),
        "inferredRole": _infer_field_role(str(column)),
        "missingCount": int(series.isna().sum()),
        "uniqueCount": int(series.nunique(dropna=True)),
    }


def _dtype_name(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_numeric_dtype(series):
        return "number"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if isinstance(series.dtype, pd.CategoricalDtype):
        return "category"
    return "string"


def _infer_field_role(column_name: str) -> str | None:
    key = column_name.lower()
    if key in {"formula", "composition", "chemical_formula", "pretty_formula"}:
        return "formula"
    if key in {"target", "y_true", "true", "actual", "label"}:
        return "target"
    if key in {"prediction", "pred", "y_pred", "predicted"}:
        return "prediction"
    if key in {"uncertainty", "std", "y_std", "sigma"}:
        return "uncertainty"
    if key in {"structure_id", "material_id", "id"}:
        return "structure_id"
    return None


def _looks_like_structure_dict(data: Any) -> bool:
    return isinstance(data, dict) and "lattice" in data and "sites" in data


def _looks_like_table_json(data: Any) -> bool:
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return True
    if isinstance(data, dict) and data and all(isinstance(value, list) for value in data.values()):
        lengths = {len(value) for value in data.values()}
        return len(lengths) == 1
    return False


def _safe_archive_name(name: str, *, max_depth: int) -> Path | None:
    normalized = name.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    if not parts or len(parts) > max_depth:
        return None
    if any(part in {".", ".."} for part in parts):
        return None
    if any(":" in part for part in parts):
        return None
    return Path(*parts)


def _file_id(file_path: Path) -> str:
    return f"file_{content_hash(str(file_path.resolve()))[:12]}"
