"""Deterministic, read-only architecture contract report for B0-7."""

from __future__ import annotations

import ast
import importlib
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Sequence

from scripts.architecture_scan import (
    API_ROOT,
    HANDLER_PATHS,
    LEGACY_COMPATIBILITY_PREFIXES,
    MDI_ROOT,
    QUEUE_NAMES,
    DynamicReference,
    ImportEdge,
    canonical_python_files,
    frontend_compatibility_edges,
    forbidden_edges,
    layer_for_module,
    module_name,
    public_symbols,
    scan_dynamic_references,
    scan_imports,
    strongly_connected_components,
)


def _add_runtime_paths() -> None:
    for relative in (
        "apps/api",
        "packages/schemas",
        "packages/tool-registry",
        "packages/adapters",
        "packages/artifact-core",
        "packages/material-parsers",
        "services/workers",
        "services/llm",
    ):
        path = str((Path(__file__).resolve().parents[1] / relative).resolve())
        if path not in sys.path:
            sys.path.insert(0, path)


def _resolve_handler(dotted_path: str) -> dict[str, object]:
    module_name_value, attribute = dotted_path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_name_value)
        value = getattr(module, attribute)
        return {
            "handler": dotted_path,
            "callable": callable(value),
            "signature": str(inspect.signature(value)),
            "status": "PASS" if callable(value) else "FAIL",
        }
    except Exception as exc:  # pragma: no cover - environment-specific import diagnostic
        return {
            "handler": dotted_path,
            "callable": False,
            "signature": None,
            "status": "FAIL",
            "errorType": type(exc).__name__,
        }


def _external_module_name(path: Path, root: Path, package: str) -> str:
    relative = path.relative_to(root).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join((package, *parts))


def _scan_external_imports(root: Path, package: str) -> list[ImportEdge]:
    edges: list[ImportEdge] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        source = _external_module_name(path, root, package)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(
                        ImportEdge(
                            source,
                            alias.name,
                            path.relative_to(Path(__file__).resolve().parents[1]).as_posix(),
                            node.lineno,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = source.rsplit(".", 1)[0]
                    parts = base.split(".")[: -(node.level - 1) or None]
                    target = ".".join((*parts, *(node.module or "").split("."))).rstrip(".")
                else:
                    target = node.module or ""
                if target:
                    edges.append(
                        ImportEdge(
                            source,
                            target,
                            path.relative_to(Path(__file__).resolve().parents[1]).as_posix(),
                            node.lineno,
                        )
                    )
    return sorted(set(edges))


def _scan_frontend_references() -> list[DynamicReference]:
    root = Path(__file__).resolve().parents[1] / "apps" / "web"
    references: set[DynamicReference] = set()
    patterns = (
        ("next-dynamic-import", re.compile(r"\bimport\(\s*[\"']([^\"']+)[\"']")),
        ("worker-url", re.compile(r"new\s+URL\(\s*[\"']([^\"']+)[\"']")),
        (
            "route-reference",
            re.compile(r"(?:router\.(?:push|prefetch)|fetch)\(\s*[`\"']([^`\"']+)"),
        ),
    )
    for suffix in ("*.ts", "*.tsx", "*.mjs"):
        for path in sorted(root.rglob(suffix)):
            if any(part in path.parts for part in (".next", "node_modules", "coverage")):
                continue
            text = path.read_text(encoding="utf-8")
            for kind, pattern in patterns:
                for match in pattern.finditer(text):
                    value = match.group(1)
                    if value:
                        references.add(
                            DynamicReference(
                                path.relative_to(Path(__file__).resolve().parents[1]).as_posix(),
                                text.count("\n", 0, match.start()) + 1,
                                value[:256],
                                kind,
                            )
                        )
    return sorted(references)


def _launcher_references() -> dict[str, list[str]]:
    root = Path(__file__).resolve().parents[1]
    patterns = {
        "api": re.compile(r"uvicorn\s+mdi_api\.main:app"),
        "worker": re.compile(r"python(?:\.exe)?\s+-m\s+mdi_workers\.worker_entrypoint"),
    }
    result: dict[str, set[str]] = {key: set() for key in patterns}
    for path in sorted((root / "scripts").glob("*")):
        if not path.is_file() or path.suffix.lower() not in {".ps1", ".py", ".yml", ".yaml", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for key, pattern in patterns.items():
            if pattern.search(text):
                result[key].add(path.relative_to(root).as_posix())
    return {key: sorted(values) for key, values in result.items()}


def _public_surface() -> dict[str, list[str]]:
    root = Path(__file__).resolve().parents[1]
    modules: dict[str, Path] = {
        "mdi_api.repositories": MDI_ROOT / "repositories.py",
        "mdi_schemas.worker_queues": root / "packages" / "schemas" / "mdi_schemas" / "worker_queues.py",
    }
    for path in canonical_python_files():
        modules[module_name(path)] = path
    for dotted in HANDLER_PATHS:
        module, _ = dotted.rsplit(".", 1)
        candidate = API_ROOT / Path(*module.split(".")).with_suffix(".py")
        if candidate.exists():
            modules[module] = candidate
        elif candidate.with_name("__init__.py").exists():
            modules[module] = candidate.with_name("__init__.py")
    return {name: public_symbols(path) for name, path in sorted(modules.items())}


def _tool_adapter_identity() -> dict[str, object]:
    _add_runtime_paths()
    result: dict[str, object] = {
        "toolIds": [],
        "adapterIds": [],
        "status": "PASS",
    }
    try:
        registry_module = importlib.import_module("mdi_tool_registry")
        registry = registry_module.load_manifests()
        result["toolIds"] = sorted(str(tool.toolId) for tool in registry.tools)
    except Exception as exc:  # pragma: no cover - diagnostic only
        result["status"] = "FAIL"
        result["toolErrorType"] = type(exc).__name__
    try:
        adapters = importlib.import_module("mdi_adapters.registry")
        result["adapterIds"] = sorted(str(adapter_id) for adapter_id in adapters.ADAPTER_CLASSES)
    except Exception as exc:  # pragma: no cover - diagnostic only
        result["status"] = "FAIL"
        result["adapterErrorType"] = type(exc).__name__
    return result


def _queue_identity() -> dict[str, object]:
    _add_runtime_paths()
    try:
        manifest = importlib.import_module("mdi_schemas.worker_queues")
        definitions = tuple(manifest.WORKER_QUEUE_MANIFEST)
        names = tuple(definition.default_name for definition in definitions)
        handlers = tuple(definition.handler for definition in definitions)
        return {
            "queueNames": list(names),
            "handlers": list(handlers),
            "queueNamesMatchFrozen": names == QUEUE_NAMES,
            "handlerPathsMatchFrozen": handlers == HANDLER_PATHS,
            "status": "PASS" if names == QUEUE_NAMES and handlers == HANDLER_PATHS else "FAIL",
        }
    except Exception as exc:  # pragma: no cover - diagnostic only
        return {"queueNames": [], "handlers": [], "status": "FAIL", "errorType": type(exc).__name__}


def build_architecture_report() -> dict[str, object]:
    _add_runtime_paths()
    canonical_edges = scan_imports()
    worker_edges = _scan_external_imports(
        Path(__file__).resolve().parents[1] / "services" / "workers" / "mdi_workers",
        "mdi_workers",
    )
    all_edges = sorted(set(canonical_edges + worker_edges))
    backend_findings = forbidden_edges(canonical_edges)
    frontend_findings = frontend_compatibility_edges()
    findings = backend_findings + frontend_findings
    queue = _queue_identity()
    handlers = [_resolve_handler(path) for path in HANDLER_PATHS]
    tool_adapter = _tool_adapter_identity()
    return {
        "schemaVersion": "ArchitectureReport/1.0",
        "scope": {
            "canonical": "apps/api/mdi_api/{application,domain,infrastructure,bootstrap,transport,compatibility}",
            "worker": "services/workers/mdi_workers",
            "frontend": "apps/web",
        },
        "importEdges": [edge.as_dict() for edge in canonical_edges],
        "workerImportEdges": [edge.as_dict() for edge in worker_edges],
        "forbiddenEdges": findings,
        "cycles": strongly_connected_components(canonical_edges),
        "compatibilityDirection": {
            "canonicalToCompatibility": sorted(
                [
                    edge.as_dict()
                    for edge in canonical_edges
                    if layer_for_module(edge.target) == "compatibility"
                    or edge.target.startswith(LEGACY_COMPATIBILITY_PREFIXES)
                ]
                + frontend_findings,
                key=lambda item: tuple(str(item.get(key, "")) for key in ("source", "target", "path", "line")),
            ),
            "legacyFacadeToCanonical": sorted(
                edge.as_dict()
                for edge in all_edges
                if edge.source in {"mdi_api.repositories", "mdi_api.phase2_runtime"}
                and layer_for_module(edge.target) in {"application", "infrastructure", "domain"}
            ),
        },
        "dynamicReferences": [
            reference.as_dict()
            for reference in sorted(set(scan_dynamic_references()) | set(_scan_frontend_references()))
        ],
        "publicSurface": _public_surface(),
        "handlerResolution": handlers,
        "queueIdentity": queue,
        "toolAdapterIdentity": tool_adapter,
        "launcherReferences": _launcher_references(),
        "testIdentityReferences": {
            "handlers": sorted(
                {
                    value
                    for path in (Path(__file__).resolve().parents[1] / "tests").rglob("*")
                    if path.is_file() and path.suffix in {".py", ".ts", ".tsx", ".mjs"}
                    for value in HANDLER_PATHS
                    if value in path.read_text(encoding="utf-8", errors="ignore")
                }
            ),
            "queues": sorted(
                {
                    value
                    for path in (Path(__file__).resolve().parents[1] / "tests").rglob("*")
                    if path.is_file() and path.suffix in {".py", ".ts", ".tsx", ".mjs"}
                    for value in QUEUE_NAMES
                    if value in path.read_text(encoding="utf-8", errors="ignore")
                }
            ),
        },
        "status": (
            "PASS"
            if not findings
            and queue["status"] == "PASS"
            and all(item["status"] == "PASS" for item in handlers)
            and tool_adapter["status"] == "PASS"
            else "FAIL"
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    report = build_architecture_report()
    print(
        json.dumps(
            report,
            ensure_ascii=False,
            sort_keys=True,
            indent=2 if args.pretty else None,
            separators=None if args.pretty else (",", ":"),
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
