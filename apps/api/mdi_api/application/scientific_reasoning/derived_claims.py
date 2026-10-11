"""Bounded evidence requirements for named derived products without numbers.

Callers resolve the persisted citation graph. This is not a general language
verifier, and unrelated bundle facts must not support an individual finding.
"""
from __future__ import annotations

import re
from typing import Any


_PRODUCTS = (
    (r"(?<![A-Za-z_])MAE(?![A-Za-z_])|平均绝对误差|mean absolute error",
     {"ml.mae", "xrd.peak_shift_mae", "mae"}),
    (r"(?<![A-Za-z_])RMSE(?![A-Za-z_])|均方根误差|root mean square(?:d)? error",
     {"ml.rmse", "xrd.peak_shift_rmse", "trajectory.diffusion_fit_rmse", "diffusion_fit_rmse", "rmse"}),
    (r"(?<![A-Za-z_])R(?:²|\s*\^?\s*2)(?![A-Za-z_])|决定系数|R[- ]squared",
     {"ml.r2", "trajectory.diffusion_fit_r2", "trajectory.diffusion_fit_r_squared", "diffusion_fit_r_squared", "r2"}),
    (r"残差(?:图|分布)|residual (?:plot|distribution)s?",
     {"ml.high_error_residual", "ml.mean_signed_error"}),
    (r"(?:绝对)?误差最大(?:的)?样本|高误差样本|high[- ]error samples?|largest[- ]error samples?",
     {"ml.high_error_sample_id", "ml.high_error_absolute_error"}),
)
_PATTERNS = [(re.compile(pattern, re.I), predicates) for pattern, predicates in _PRODUCTS]
_R2_NAME = rf"(?:{_PRODUCTS[2][0]})"
_UNDEFINED_R2 = re.compile(
    rf"{_R2_NAME}\s*(?:为?(?:未定义|无法定义|不可定义)(?:[（(]目标值为常量[）)])?"
    rf"|状态(?:为|是)\s*undefined_constant_target(?![A-Za-z0-9_])"
    rf"|(?:is\s+)?undefined(?:\s*\(constant target\))?)"
    rf"|(?:无法定义|不可定义)\s*{_R2_NAME}", re.I,
)
_NAMES = "(?:" + "|".join(pattern for pattern, _ in _PRODUCTS) + ")"
_LIST = rf"{_NAMES}(?:\s*(?:、|,|，|和|及|与|and|or)\s*{_NAMES})*"
_ABSENT = re.compile(
    rf"(?:"
    rf"(?:当前(?:结果)?|本次(?:结果)?)?\s*(?:尚未|未|没有)(?:计算|生成|提供|保存|列出)\s*{_LIST}"
    rf"|{_LIST}\s*(?:均|都)?(?:尚未|未)(?:计算|生成|提供|保存|列出)"
    rf"|{_LIST}\s+(?:(?:is|are|was|were|has been|have been)\s+)?(?:not (?:computed|calculated|generated|provided|available)|unavailable)"
    rf"|no\s+{_LIST}\s+(?:is|are)\s+available"
    rf")", re.I,
)


def derived_product_errors(text: str, facts: list[dict[str, Any]], label: str) -> list[str]:
    """Require saved predicates; exempt only complete explicit absence clauses.

    Sentence/contrast boundaries prevent unrelated negation ('no training')
    or another missing metric from licensing a positive claim. Ambiguous
    unsupported prose goes through normal provider repair.
    """
    predicates = {str(fact.get("predicate")) for fact in facts if fact.get("value") is not None}
    errors: list[str] = []
    for clause in re.split(r"[。；;!！?？\n]|(?<!\d)\.(?!\d)|(?:但是|但|然而|\bbut\b|\bhowever\b)", text):
        clause = clause.strip(" ，,：: ")
        if not clause or _ABSENT.fullmatch(clause):
            continue
        if _UNDEFINED_R2.search(clause):
            if any(fact.get("predicate") == "ml.r2_status" and fact.get("value") == "undefined_constant_target" for fact in facts):
                # Remove only this explicit statement. A second R² claim in the
                # same clause still needs its own numeric scientific evidence.
                clause = _UNDEFINED_R2.sub("", clause)
            else:
                errors.append(f"{label}: undefined R² lacks referenced ml.r2_status=undefined_constant_target.")
        for pattern, required in _PATTERNS:
            match = pattern.search(clause)
            if match and not predicates.intersection(required):
                errors.append(
                    f"{label}: derived product {match.group(0)!r} lacks "
                    f"referenced scientific facts ({', '.join(sorted(required))}). "
                    "Do not claim it was computed/generated from generic table outputs. "
                    "State missing products in separate explicit absence clauses."
                )
    return list(dict.fromkeys(errors))
