"""Deterministic architecture inventory primitives used by Batch 0 guards.

The scanner is intentionally read-only.  It parses source rather than
importing the application, so producing an inventory cannot construct an
engine, connect to Redis, or mutate a runtime service.
"""

from __future__ import annotations

import ast
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPOSITORY_ROOT / "apps" / "api"
MDI_ROOT = API_ROOT / "mdi_api"

CANONICAL_LAYERS = ("application", "domain", "infrastructure", "bootstrap", "transport", "compatibility")

LEGACY_COMPATIBILITY_PREFIXES = (
    "mdi_api.agent2_repositories",
    "mdi_api.database",
    "mdi_api.interpretation",
    "mdi_api.phase2_runtime",
    "mdi_api.project_history",
    "mdi_api.report_composition",
    "mdi_api.repositories",
    "mdi_api.routers",
    "mdi_api.scientific_objects",
    "mdi_api.scientific_reports",
    "mdi_api.scientific_results",
    "mdi_api.workspaces",
)

# These are explicit, source-specific transition edges retained from the
# already-completed Batch 0 boundaries.  They are deliberately not wildcards.
ALLOWLISTED_TRANSITION_EDGES: dict[tuple[str, str], str] = {
    (
        "mdi_api.application.providers.selection",
        "mdi_api.provider_connections",
    ): "B0-1 provider catalogue boundary",
    (
        "mdi_api.application.providers.selection",
        "mdi_llm",
    ): "B0-1 provider contract/client boundary",
    (
        "mdi_api.application.research.worker_entrypoints",
        "mdi_api.research_agent.execution",
    ): "B0-3 existing Research execution authority",
    (
        "mdi_api.application.scientific_reports.entrypoints",
        "mdi_llm",
    ): "B0-3 stable redaction/provider package",
}

CONCRETE_INFRASTRUCTURE_PREFIXES = (
    "mdi_api.config",
    "mdi_api.database",
    "mdi_api.db",
    "mdi_api.phase2_runtime",
    "mdi_api.artifact_storage",
    "mdi_api.provider_connections",
    "mdi_adapters",
    "sqlalchemy",
)
TRANSPORT_PREFIXES = ("mdi_api.routers", "mdi_api.transport", "fastapi", "starlette")
BOOTSTRAP_PREFIXES = ("mdi_api.bootstrap",)

HANDLER_PATHS = (
    "mdi_api.research_agent_worker.run_queued_turn",
    "mdi_api.research_agent_planning_worker.run_queued_planning",
    "mdi_workers.queue_runtime.run_queued_job",
    "mdi_api.scientific_results.worker.run_queued_result_projection",
    "mdi_workers.interpretation_worker.run_queued_interpretation",
    "mdi_workers.report_worker.run_queued_report_generation",
)

QUEUE_NAMES = (
    "mdi-agent-turns",
    "mdi-agent-plans",
    "mdi-jobs",
    "mdi-agent-results",
    "mdi-agent-interpretations",
    "mdi-agent-reports",
)


@dataclass(frozen=True, order=True)
class ImportEdge:
    source: str
    target: str
    path: str
    line: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, order=True)
class DynamicReference:
    path: str
    line: int
    value: str
    kind: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def module_name(path: Path) -> str:
    relative = path.relative_to(API_ROOT).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _package_name(source: str) -> str:
    return source.rsplit(".", 1)[0] if "." in source else source


def resolve_import(source: str, level: int, imported_module: str | None) -> str:
    """Resolve an AST relative import to a deterministic absolute module."""

    if level == 0:
        return imported_module or ""
    base_parts = _package_name(source).split(".")
    remove = level - 1
    if remove:
        base_parts = base_parts[:-remove]
    if imported_module:
        base_parts.extend(imported_module.split("."))
    return ".".join(part for part in base_parts if part)


def python_files(root: Path = API_ROOT) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts and not path.name.startswith(".")
    )


def canonical_python_files() -> list[Path]:
    return sorted(
        path
        for layer in CANONICAL_LAYERS
        for path in python_files(MDI_ROOT / layer)
        if (MDI_ROOT / layer).exists()
    )


def _import_edges_for_tree(path: Path, tree: ast.AST) -> list[ImportEdge]:
    source = module_name(path)
    result: list[ImportEdge] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.append(
                    ImportEdge(source, alias.name, path.relative_to(REPOSITORY_ROOT).as_posix(), node.lineno)
                )
        elif isinstance(node, ast.ImportFrom):
            target = resolve_import(source, node.level, node.module)
            if target:
                result.append(
                    ImportEdge(source, target, path.relative_to(REPOSITORY_ROOT).as_posix(), node.lineno)
                )
    return sorted(set(result))


def scan_imports(paths: Iterable[Path] | None = None) -> list[ImportEdge]:
    edges: list[ImportEdge] = []
    for path in paths or canonical_python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        edges.extend(_import_edges_for_tree(path, tree))
    return sorted(set(edges))


def _starts_with(value: str, prefixes: Iterable[str]) -> bool:
    return any(value == prefix or value.startswith(prefix + ".") for prefix in prefixes)


def layer_for_module(value: str) -> str | None:
    prefix = "mdi_api."
    if not value.startswith(prefix):
        return None
    remainder = value[len(prefix) :]
    return remainder.split(".", 1)[0] if remainder.split(".", 1)[0] in CANONICAL_LAYERS else None


def is_forbidden_edge(edge: ImportEdge) -> tuple[str, str] | None:
    source_layer = layer_for_module(edge.source)
    if source_layer is None:
        return None
    if (edge.source, edge.target) in ALLOWLISTED_TRANSITION_EDGES:
        return None
    target_layer = layer_for_module(edge.target)
    if target_layer == "compatibility":
        return "CANONICAL_TO_COMPATIBILITY", "canonical implementation may not import compatibility"
    if source_layer == "domain":
        if _starts_with(edge.target, TRANSPORT_PREFIXES):
            return "DOMAIN_TO_TRANSPORT", "domain must be transport-neutral"
        if _starts_with(edge.target, BOOTSTRAP_PREFIXES):
            return "DOMAIN_TO_BOOTSTRAP", "domain must not depend on composition"
        if _starts_with(edge.target, CONCRETE_INFRASTRUCTURE_PREFIXES):
            return "DOMAIN_TO_CONCRETE_INFRASTRUCTURE", "domain must not depend on infrastructure"
    if source_layer == "application":
        if _starts_with(edge.target, TRANSPORT_PREFIXES):
            return "APPLICATION_TO_TRANSPORT", "application must not import transport"
        if _starts_with(edge.target, CONCRETE_INFRASTRUCTURE_PREFIXES):
            return "APPLICATION_TO_CONCRETE_INFRASTRUCTURE", "application must use ports"
    if _starts_with(edge.target, LEGACY_COMPATIBILITY_PREFIXES):
        return "CANONICAL_TO_COMPATIBILITY", "canonical implementation may not import a legacy facade"
    return None


def frontend_compatibility_edges() -> list[dict[str, object]]:
    """Find canonical frontend modules importing the legacy app/components facades."""

    web_root = REPOSITORY_ROOT / "apps" / "web"
    canonical_roots = tuple(web_root / name for name in ("features", "scientific-viewers", "shared"))
    import_pattern = re.compile(
        r"(?:from\s+|import\(\s*)[\"']([^\"']*app/components/[^\"']+)[\"']"
    )
    findings: list[dict[str, object]] = []
    for root in canonical_roots:
        if not root.exists():
            continue
        for suffix in ("*.ts", "*.tsx", "*.mjs"):
            for path in sorted(root.rglob(suffix)):
                text = path.read_text(encoding="utf-8")
                for match in import_pattern.finditer(text):
                    findings.append(
                        {
                            "source": path.relative_to(REPOSITORY_ROOT).as_posix(),
                            "target": match.group(1),
                            "path": path.relative_to(REPOSITORY_ROOT).as_posix(),
                            "line": text.count("\n", 0, match.start()) + 1,
                            "rule": "CANONICAL_TO_COMPATIBILITY",
                            "reason": "canonical frontend module may not import app/components compatibility",
                        }
                    )
    return sorted(
        findings,
        key=lambda item: tuple(str(item[key]) for key in ("source", "target", "path", "line")),
    )


def forbidden_edges(edges: Iterable[ImportEdge] | None = None) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for edge in edges or scan_imports():
        result = is_forbidden_edge(edge)
        if result:
            rule, reason = result
            findings.append(
                {
                    **edge.as_dict(),
                    "rule": rule,
                    "reason": reason,
                }
            )
    return sorted(findings, key=lambda item: tuple(str(item[key]) for key in ("source", "target", "path", "line")))


def allowlisted_edges(edges: Iterable[ImportEdge] | None = None) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for edge in edges or scan_imports():
        reason = ALLOWLISTED_TRANSITION_EDGES.get((edge.source, edge.target))
        if reason:
            result.append({**edge.as_dict(), "reason": reason})
    return sorted(result, key=lambda item: tuple(str(item[key]) for key in ("source", "target", "path", "line")))


def _literal_strings(tree: ast.AST) -> Iterable[tuple[int, str]]:
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.lineno, node.value


_DOTTED_REFERENCE = re.compile(
    r"(?:mdi_api|mdi_workers|mdi_tool_registry|mdi_adapters)(?:\.[A-Za-z_][A-Za-z0-9_]*){1,}"
)


def scan_dynamic_references(
    roots: Iterable[Path] = (API_ROOT, REPOSITORY_ROOT / "services" / "workers", REPOSITORY_ROOT / "packages"),
) -> list[DynamicReference]:
    references: set[DynamicReference] = set()
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError:
                continue
            for line, value in _literal_strings(tree):
                for match in _DOTTED_REFERENCE.findall(value):
                    references.add(
                        DynamicReference(
                            path.relative_to(REPOSITORY_ROOT).as_posix(),
                            line,
                            match,
                            "python-dotted-string",
                        )
                    )
    return sorted(references)


def public_symbols(path: Path) -> list[str]:
    """Return a static, import-free public top-level symbol census."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                names.add(node.name)
        elif isinstance(node, ast.Import):
            names.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.update(alias.asname or alias.name for alias in node.names if alias.name != "*")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    names.add(target.id)
    return sorted(names)


def strongly_connected_components(edges: Iterable[ImportEdge]) -> list[list[str]]:
    graph: dict[str, set[str]] = {}
    for edge in edges:
        if layer_for_module(edge.source) and layer_for_module(edge.target):
            graph.setdefault(edge.source, set()).add(edge.target)
            graph.setdefault(edge.target, set())

    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for child in sorted(graph[node]):
            if child not in indices:
                visit(child)
                lowlinks[node] = min(lowlinks[node], lowlinks[child])
            elif child in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[child])
        if lowlinks[node] == indices[node]:
            component: list[str] = []
            while True:
                child = stack.pop()
                on_stack.remove(child)
                component.append(child)
                if child == node:
                    break
            if len(component) > 1 or node in graph[node]:
                components.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return sorted(components)
