"""Source-bound follow-up choices for saved volumetric results.

Free prose cannot establish that a proposed method applies to a field. These
choices describe evidence gaps identified by the Result's limitation codes;
they neither authorize tools nor fabricate an analysis when a provider fails.
"""

from typing import Any


_VOLUMETRIC_FOLLOW_UPS = {
    "ELF_INTEGRAL_NOT_POPULATION": (
        "若需要电子数或盆布居，需补充相应的电子密度数据和布居分析结果；"
        "当前 ELF 场及其体积分不能替代这些证据。"
    ),
    "ELF_CONTOURS_NOT_TOPOLOGY": (
        "若需要化学键、孤对电子或盆拓扑结论，需补充针对该结构的独立分析结果；"
        "ELF 等值面和切片仅供查看已有标量场。"
    ),
    "PARTIAL_DENSITY_IDENTITY_NOT_ESTABLISHED": (
        "若需要指定能带、K 点或轨道身份，需补充对应的源元数据和分析结果。"
    ),
    "PARTIAL_DENSITY_INTEGRAL_NOT_OCCUPANCY": (
        "若需要等值面内的电子数，需补充指定区域的密度体积分及其归一化信息；"
        "当前整胞积分不能替代该结果，也不能直接视为单轨道占据数或概率。"
    ),
}


def follow_up_policy(bundle: Any) -> dict[str, Any] | None:
    data = bundle.model_dump(mode="json") if hasattr(bundle, "model_dump") else dict(bundle)
    limitations = data.get("limitations") or []
    codes = {item.get("code") for item in limitations}
    is_volumetric = bool(codes.intersection(_VOLUMETRIC_FOLLOW_UPS)) or any(
        str(item.get("predicate") or item.get("result_type") or "").startswith("volumetric.")
        for item in [*(data.get("facts") or []), *(data.get("result_items") or [])]
    )
    if not is_volumetric:
        return None
    options = [
        {"text": text, "limitation_refs": [
            item["limitation_id"] for item in limitations
            if item.get("code") == code and item.get("limitation_id")
        ]}
        for code, text in _VOLUMETRIC_FOLLOW_UPS.items() if code in codes
    ]
    return {"mode": "EXACT_SOURCE_CHOICES", "options": [item for item in options if item["limitation_refs"]]}


def follow_up_errors(suggestions: list[str], bundle: Any) -> list[str]:
    policy = follow_up_policy(bundle)
    if policy is None:
        return []
    allowed = {item["text"] for item in policy["options"]}
    if any(text.strip() not in allowed for text in suggestions):
        return [
            "follow_up_suggestions must select exact text from result.follow_up_policy.options "
            "or be empty; do not invent a method, physical interpretation or prerequisite"
        ]
    return []


def project_follow_up_suggestions(suggestions: Any, bundle: Any) -> list[str]:
    """Retain supported choices on historical reads without rewriting records."""
    if not isinstance(suggestions, list):
        return []
    texts = [str(item).strip() for item in suggestions[:8] if isinstance(item, str) and item.strip()]
    policy = follow_up_policy(bundle)
    if policy is not None:
        allowed = {item["text"] for item in policy["options"]}
        texts = [text for text in texts if text in allowed]
    return list(dict.fromkeys(texts))


def report_next_steps_text(interpretation: dict[str, Any], bundle: Any) -> str | None:
    suggestions = (interpretation.get("interpretation") or {}).get("follow_up_suggestions")
    return "；".join(project_follow_up_suggestions(suggestions, bundle)) or None
