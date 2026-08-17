from __future__ import annotations

import re
from pathlib import Path


def assert_current_task_queue(root: Path) -> list[str]:
    """Validate the live queue without coupling tests to historical task cardinality."""
    text = (root / "TASKS.md").read_text(encoding="utf-8")
    blocks = re.findall(r"---TASK---.*?---END---", text, flags=re.DOTALL)

    assert len(blocks) == text.count("---TASK---") == text.count("---END---")
    assert re.fullmatch(r"(?:\s*---TASK---.*?---END---\s*)*", text, flags=re.DOTALL)

    processing = [
        block
        for block in blocks
        if "状态：处理中" in block or re.search(r"(?m)^Status:\s*processing\s*$", block)
    ]
    assert len(processing) <= 1
    if processing:
        assert processing[0] == blocks[0]

    return blocks
