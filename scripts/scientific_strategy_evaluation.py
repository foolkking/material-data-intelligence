"""Run the bounded deterministic scientific-strategy corpus.

This is a strategy evaluator, not a provider runner. Live provider cases are
explicitly opt-in elsewhere and are never a default CI dependency.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mdi_api.research_agent.strategy.evaluation import evaluate_strategy_cases
from mdi_api.research_agent.strategy.fixtures import golden_strategy_cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output",
        default="docs/agent2/strategy/generated/strategy_evaluation.json",
    )
    args = parser.parse_args()
    report = evaluate_strategy_cases(golden_strategy_cases())
    payload = report.to_dict()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    if args.check and not report.accepted:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
