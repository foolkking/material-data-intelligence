from __future__ import annotations

from typing import Any

from mdi_api.scientific_results.schemas import ScientificResultBundle
from .schemas import ReportFigure, ReportFinding, ReportLimitation, ReportSupportingResult, ScientificReportOutput


_METHOD_SUMMARIES = {
    "structure.rdf": "根据晶体结构统计指定截断范围内的原子对距离分布，得到径向分布函数。",
    "diffraction.theoretical_xrd": "根据晶体结构与执行时记录的衍射参数计算理论 XRD 图谱。",
    "diffraction.experimental_theoretical_comparison": "在执行时记录的匹配容差下比较实验与理论 XRD 峰位。",
    "ml.regression_evaluation": "使用已提交的预测与真实值评估回归模型表现。",
    "trajectory.msd": "根据轨迹时间序列计算均方位移，并保留执行时的分量与时间单位。",
    "trajectory.diffusion": "基于已提交的 MSD 结果和拟合区间估计扩散系数。",
    "phonon.band": "沿既定布里渊区路径整理声子色散关系。",
    "phonon.dos": "根据已提交的频率网格整理声子态密度。",
    "phonon.band_dos": "联合呈现同一计算上下文中的声子色散与态密度。",
}


class DeterministicScientificReportComposer:
    """Compose a readable report from validated upstream contracts without new science."""

    def compose(self, *, bundle: ScientificResultBundle, interpretation: dict[str, Any], relevance_status: str) -> ScientificReportOutput:
        interp = interpretation.get("interpretation") or {}
        raw_findings = [*(interp.get("primary_findings") or []), *(interp.get("claims") or [])]
        findings: list[ReportFinding] = []
        for item in raw_findings[:16]:
            findings.append(ReportFinding(
                statement=str(item.get("statement") or item.get("claim") or item.get("text") or "").strip(),
                finding_refs=[str(item.get("finding_id") or item.get("claim_id"))] if item.get("finding_id") or item.get("claim_id") else [],
                fact_refs=[str(value) for value in item.get("fact_refs", item.get("factRefs", []))],
                evidence_refs=[str(value) for value in item.get("evidence_refs", item.get("evidenceRefs", []))],
            ))
        findings = [item for item in findings if item.statement]
        if not findings:
            raise ValueError("validated interpretation contains no reportable findings")
        title = self._title(bundle, interp)
        summary = str(interp.get("answer_lead") or interp.get("answerLead") or findings[0].statement).strip()
        if bundle.execution_status.value == "PARTIAL":
            summary = f"当前结果是部分完成的分析。{summary}"
        if relevance_status == "STALE":
            summary = f"这是针对原始 source version 的历史结果。{summary}"
        elif relevance_status == "SOURCE_MISSING":
            summary = f"原始来源当前不可获得，但历史结果仍可追溯。{summary}"
        elif relevance_status == "INVALIDATED":
            summary = f"该结果仅作为历史记录，不应视为当前有效证据。{summary}"
        figures = [ReportFigure(
            figure_ref=item.figure_id,
            caption=item.caption_seed or item.title or item.figure_type,
            fact_refs=list(item.fact_refs),
            evidence_refs=list(item.evidence_refs),
        ) for item in bundle.figures[:16]]
        supporting = [ReportSupportingResult(result_item_ref=item.id, description=item.title) for item in bundle.result_items if item.role.value == "SUPPORTING"][:32]
        limitations = [ReportLimitation(statement=item.message, source_refs=[item.limitation_id]) for item in bundle.limitations[:32]]
        limitations.extend(ReportLimitation(statement=str(value), source_refs=[]) for value in (interp.get("limitations") or [])[:16])
        if bundle.execution_status.value == "PARTIAL" and not any("partial" in item.statement.lower() or "部分" in item.statement for item in limitations):
            limitations.append(ReportLimitation(statement="部分执行步骤未完成；报告仅覆盖已提交的有效输出。", source_refs=[]))
        if relevance_status in {"STALE", "SOURCE_MISSING", "INVALIDATED"}:
            limitations.append(ReportLimitation(statement={"STALE": "报告基于历史 source version 生成。", "SOURCE_MISSING": "原始 source version 当前不可获得。", "INVALIDATED": "原始 source version 已被标记为失效。"}[relevance_status], source_refs=[]))
        limitations = _dedupe_limitations(limitations)
        methods = [
            _METHOD_SUMMARIES.get(
                item.capability_id,
                "方法信息来自已验证的 ScientificResult，并保留执行时的参数与来源版本。",
            )
            for item in bundle.methods[:16]
        ]
        method_summary = "；".join(methods) or "方法信息来自已验证的 ScientificResult。"
        evidence_refs = sorted({ref for item in findings for ref in item.evidence_refs} | {ref for item in figures for ref in item.evidence_refs} | {item.evidence_id for item in bundle.evidence})
        return ScientificReportOutput(
            title=title,
            research_question=bundle.research_question,
            summary=summary,
            main_findings=findings,
            primary_figures=figures,
            supporting_results=supporting,
            method_summary=method_summary,
            limitations=limitations,
            data_sources=[f"source_{index}" for index, _ in enumerate(bundle.source_object_refs, start=1)],
            evidence_refs=evidence_refs,
            reproducibility_summary="本报告绑定 immutable ScientificResultSnapshot、validated Interpretation 与其 exact source versions；重新打开不会重新执行科学计算。",
        )

    @staticmethod
    def _title(bundle: ScientificResultBundle, interpretation: dict[str, Any]) -> str:
        title = str((interpretation.get("interpretation") or {}).get("title") or "").strip()
        if title and title.lower() not in {"scientific analysis", "analysis report", "材料科学分析"}:
            return title
        if bundle.result_items:
            return bundle.result_items[0].title
        return bundle.research_question[:256]


def _dedupe_limitations(limitations: list[ReportLimitation]) -> list[ReportLimitation]:
    deduped: list[ReportLimitation] = []
    positions: dict[str, int] = {}
    for item in limitations:
        key = " ".join(item.statement.split()).casefold()
        if key not in positions:
            positions[key] = len(deduped)
            deduped.append(item)
            continue
        existing = deduped[positions[key]]
        deduped[positions[key]] = existing.model_copy(
            update={"source_refs": sorted(set(existing.source_refs) | set(item.source_refs))}
        )
    return deduped


__all__ = ["DeterministicScientificReportComposer"]
