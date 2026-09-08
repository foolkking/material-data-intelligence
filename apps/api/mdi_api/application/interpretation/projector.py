from __future__ import annotations


from mdi_api.domain.scientific_results.contracts import ResultExecutionStatus, ResultRelevanceStatus, ScientificResultBundle

from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput


class AssistantResponseProjector:
    """Render only validated interpretation data into a user-facing message."""

    def project(self, interpretation: ScientificInterpretationOutput, bundle: ScientificResultBundle, *, effective_relevance: str) -> str:
        lines = [interpretation.title.strip()]
        status_notice = self._status_notice(bundle.execution_status.value, effective_relevance)
        if status_notice:
            lines.append(status_notice)
        lines.append(interpretation.answer_lead.strip())
        for finding in [*interpretation.primary_findings, *interpretation.supporting_findings]:
            lines.append(f"- {finding.statement.strip()}")
        limitations = list(interpretation.limitations)
        if limitations:
            lines.append("\n限制：")
            lines.extend(f"- {item.strip()}" for item in limitations[:16] if item.strip())
        if bundle.warnings:
            lines.append("\n警告：")
            lines.extend(
                f"- {item.message.strip()}"
                for item in bundle.warnings[:16]
                if item.message.strip()
            )
        if interpretation.follow_up_suggestions:
            lines.append("\n可考虑的后续方向：")
            lines.extend(f"- {item.strip()}" for item in interpretation.follow_up_suggestions[:8] if item.strip())
        return "\n".join(line for line in lines if line.strip())[:16000]

    @staticmethod
    def _status_notice(execution: str, relevance: str) -> str:
        notices: list[str] = []
        if execution == ResultExecutionStatus.PARTIAL.value:
            notices.append("当前结果是部分完成的分析，以下解释仅覆盖已成功生成的结果。")
        if relevance == ResultRelevanceStatus.STALE.value:
            notices.append("这是针对原始 ScientificObject 版本的历史结果，不代表当前版本。")
        elif relevance == ResultRelevanceStatus.SOURCE_MISSING.value:
            notices.append("原始结果仍可解释，但对应的 exact source version 当前不可获得。")
        elif relevance == ResultRelevanceStatus.INVALIDATED.value:
            notices.append("该结果仅作为历史记录，不应视为当前有效证据。")
        return "\n".join(notices)


__all__ = ["AssistantResponseProjector"]
