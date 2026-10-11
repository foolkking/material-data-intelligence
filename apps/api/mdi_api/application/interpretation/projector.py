from __future__ import annotations


from mdi_api.domain.scientific_results.contracts import ResultExecutionStatus, ResultRelevanceStatus, ScientificResultBundle

from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput


class AssistantResponseProjector:
    """Render only validated interpretation data into a user-facing message."""

    def project(self, interpretation: ScientificInterpretationOutput, bundle: ScientificResultBundle, *, effective_relevance: str, markdown: bool = False) -> str:
        if markdown:
            return self._markdown(interpretation, bundle, effective_relevance=effective_relevance)
        lines = [interpretation.title.strip()]
        status_notice = self._status_notice(bundle.execution_status.value, effective_relevance)
        if status_notice:
            lines.append(status_notice)
        limitations, warnings = self._qualifications(interpretation, bundle)
        findings = self._finding_statements(interpretation, limitations, warnings)
        lead = interpretation.answer_lead.strip()
        if lead and lead not in [*findings, *limitations, *warnings]:
            lines.append(lead)
        lines.extend(f"- {statement}" for statement in findings)
        if limitations:
            lines.append("\n限制：")
            lines.extend(f"- {item}" for item in limitations)
        if warnings:
            lines.append("\n警告：")
            lines.extend(
                f"- {item}" for item in warnings
            )
        if interpretation.follow_up_suggestions:
            lines.append("\n可考虑的后续方向：")
            lines.extend(f"- {item.strip()}" for item in interpretation.follow_up_suggestions[:8] if item.strip())
        return "\n".join(line for line in lines if line.strip())[:16000]

    def _markdown(self, interpretation: ScientificInterpretationOutput, bundle: ScientificResultBundle, *, effective_relevance: str) -> str:
        sections = [f"## {interpretation.title.strip()}"]
        notice = self._status_notice(bundle.execution_status.value, effective_relevance)
        if notice:
            sections.append(notice)
        # Communication derives the lead from the first findings. Render each
        # complete finding once; punctuation in that joined lead is not identity.
        limitations, warnings = self._qualifications(interpretation, bundle)
        sections.extend(self._finding_statements(interpretation, limitations, warnings))
        for heading, items in (
            ("限制", limitations),
            ("警告", warnings),
            ("后续方向", interpretation.follow_up_suggestions[:8]),
        ):
            if items:
                sections.append(f"### {heading}\n\n" + "\n".join(f"- {item.strip()}" for item in items if item.strip()))
        return "\n\n".join(section for section in sections if section.strip())[:16000]

    @staticmethod
    def _finding_statements(interpretation: ScientificInterpretationOutput, limitations: list[str], warnings: list[str]) -> list[str]:
        # An exact qualification can also be returned as a finding. Keep it once
        # in its named section; never merge similar claims or alter stored refs.
        qualifications = set([*limitations, *warnings])
        return list(dict.fromkeys(
            finding.statement.strip()
            for finding in [*interpretation.primary_findings, *interpretation.supporting_findings]
            if finding.statement.strip() and finding.statement.strip() not in qualifications
        ))

    @staticmethod
    def _qualifications(interpretation: ScientificInterpretationOutput, bundle: ScientificResultBundle) -> tuple[list[str], list[str]]:
        limitations = list(dict.fromkeys(item.strip() for item in interpretation.limitations if item.strip()))[:16]
        warnings = list(dict.fromkeys(
            item.message.strip() for item in bundle.warnings
            if item.message.strip() and item.message.strip() not in limitations
        ))[:16]
        return limitations, warnings

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
