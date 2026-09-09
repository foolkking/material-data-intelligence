from __future__ import annotations

import ast
from importlib import import_module
from pathlib import Path


def test_scientific_result_queue_and_reconciler_legacy_paths_preserve_identity():
    legacy_queue = import_module("mdi_api.scientific_results.queue")
    canonical_queue = import_module("mdi_api.infrastructure.scientific_results.queue")
    legacy_reconciler = import_module("mdi_api.scientific_results.reconciler")
    canonical_reconciler = import_module("mdi_api.infrastructure.scientific_results.reconciler")

    queue_symbols = (
        "DisabledResultProjectionQueue",
        "InMemoryResultProjectionQueue",
        "RedisRQResultProjectionQueue",
        "ResultProjectionQueue",
        "ResultProjectionQueueSubmitResult",
        "result_projection_queue_from_settings",
    )
    for symbol in queue_symbols:
        assert getattr(legacy_queue, symbol) is getattr(canonical_queue, symbol)
    assert legacy_reconciler.ScientificResultReconciler is canonical_reconciler.ScientificResultReconciler


def test_scientific_result_compatibility_modules_have_no_implementation_definitions():
    root = Path(__file__).resolve().parents[1]
    for relative_path in (
        "apps/api/mdi_api/scientific_results/queue.py",
        "apps/api/mdi_api/scientific_results/reconciler.py",
    ):
        tree = ast.parse((root / relative_path).read_text(encoding="utf-8"))
        assert not any(
            isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            for node in tree.body
        )
