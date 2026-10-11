from __future__ import annotations

from typing import Any
from mdi_api.application.scientific_reasoning.follow_ups import report_next_steps_text

from mdi_api.domain.scientific_results.contracts import ScientificFigure, ScientificResultBundle
from mdi_api.domain.scientific_reports.contracts import (
    ReportFigure,
    ReportFinding,
    ReportLimitation,
    ReportNarrativeSection,
    ReportSupportingResult,
    ScientificReportOutput,
)


_METHOD_SUMMARIES = {
    "reference.convert_units": "按版本化 SI 定义换算显式输入数值，保留原单位、目标单位及温差语义。",
    "generation.function_curve": "根据显式参数在指定区间等距采样受控数学函数，并保留全部采样点。",
    "composition.from_formula": "解析输入化学式的化学计量数，计算原子分数和原子百分比。",
    "viz.inline_xy": "解析本次消息中的原始数值表，按指定列绘图，保留全部数值与原始行序。",
    "generation.ideal_crystal": "从指定晶格原型、元素和晶格参数生成理想模型；连接表示最短周期近邻。",
    "reference.periodic_table": "根据版本化元素参考资料绘制周期表，按所选参考性质着色，并保留元素筛选与高亮。",
    "reference.compare_elements": "按同一性质定义和单位比较所选元素的参考值，明确保留参考资料中的缺值。",
    "volumetric.data": "读取来源中的体数据场，整理网格、物理量与单位，并根据保存的网格数值计算场统计量。",
    "structure.rdf": "根据晶体结构统计指定截断范围内的原子对距离分布，得到径向分布函数。",
    "diffraction.theoretical_xrd": "根据晶体结构与执行时记录的衍射参数计算理论 XRD 图谱。",
    "diffraction.experimental_theoretical_comparison": "在执行时记录的匹配容差下比较实验与理论 XRD 峰位。",
    "ml.regression_evaluation": "使用已提交的预测与真实值评估回归模型表现。",
    "trajectory.msd": "根据轨迹时间序列计算均方位移，并保留执行时的分量与时间单位。",
    "trajectory.diffusion": "基于已提交的 MSD 结果和拟合区间估计扩散系数。",
    "phonon.band": "沿既定布里渊区路径整理声子色散关系。",
    "phonon.dos": "根据已提交的频率网格整理声子态密度。",
    "phonon.band_dos": "联合呈现同一计算上下文中的声子色散与态密度。",
    "structure.coordination_crystalnn": "使用 CrystalNN 对精确结构版本中的局部配位环境进行分析。",
    "structure.coordination_voronoinn": "使用 VoronoiNN 对同一精确结构版本中的局部配位环境进行分析。",
}

_ANALYSIS_TOPICS = {
    "reference.convert_units": "科学单位换算",
    "generation.function_curve": "参数化函数曲线",
    "composition.from_formula": "化学式组成",
    "viz.inline_xy": "输入数值表及其图形",
    "generation.ideal_crystal": "理想晶格示意",
    "reference.periodic_table": "元素周期表与参考性质",
    "reference.compare_elements": "元素参考性质比较",
    "volumetric.data": "体数据场及其统计量",
    "structure.rdf": "径向分布函数",
    "diffraction.theoretical_xrd": "理论 XRD 图谱",
    "diffraction.experimental_theoretical_comparison": "实验与理论 XRD 峰位比较",
    "ml.regression_evaluation": "回归模型评估",
    "trajectory.msd": "轨迹均方位移",
    "trajectory.diffusion": "指定时间窗的扩散拟合",
    "phonon.band": "声子色散",
    "phonon.dos": "声子态密度",
    "phonon.band_dos": "声子色散与态密度",
    "structure.coordination_crystalnn": "CrystalNN 局部配位环境",
    "structure.coordination_voronoinn": "VoronoiNN 局部配位环境",
}

_DIFFUSION_REJECTIONS = {
    "INSUFFICIENT_DURATION": "拟合窗口时长不足",
    "INSUFFICIENT_POINTS": "拟合点数不足",
    "INSUFFICIENT_ORIGIN_COVERAGE": "时间原点覆盖率不足",
    "NON_POSITIVE_SLOPE": "拟合斜率非正",
    "POOR_LINEAR_FIT": "线性拟合质量未达标",
    "INSUFFICIENT_MSD_SIGNAL": "均方位移信号不足",
    "BALLISTIC_LIKE_WINDOW": "窗口呈类弹道特征",
    "NON_DIFFUSIVE_WINDOW": "窗口未满足扩散判据",
}


def _report_figure(figure: ScientificFigure, bundle: ScientificResultBundle) -> ReportFigure:
    """Keep complete figure support within the report's citation bounds.

    Large figures may contain hundreds of facts. A saved evidence record can
    cite the same facts as one group; it cannot introduce unrelated support or
    discard the tail of the figure's scientific data.
    """
    fact_refs = list(dict.fromkeys(figure.fact_refs))
    evidence_refs = list(dict.fromkeys(figure.evidence_refs))
    if len(fact_refs) > 32:
        desired = set(fact_refs)
        covered = {ref for evidence in bundle.evidence if evidence.evidence_id in evidence_refs
                   for ref in evidence.supports_fact_refs}
        remaining = desired - covered
        candidates = [evidence for evidence in bundle.evidence
                      if evidence.evidence_id not in evidence_refs and evidence.supports_fact_refs
                      and set(evidence.supports_fact_refs).issubset(desired)]
        while len(remaining) > 32 and candidates and len(evidence_refs) < 32:
            selected = min(candidates, key=lambda evidence: (
                -len(remaining.intersection(evidence.supports_fact_refs)), evidence.evidence_id,
            ))
            supported = remaining.intersection(selected.supports_fact_refs)
            if not supported:
                break
            evidence_refs.append(selected.evidence_id)
            remaining.difference_update(supported)
            candidates.remove(selected)
        fact_refs = [ref for ref in fact_refs if ref in remaining]
    # If exact saved evidence cannot cover the figure within these bounds,
    # validation still rejects it; never silently truncate its citations.
    return ReportFigure(
        figure_ref=figure.figure_id,
        caption=figure.caption_seed or figure.title or figure.figure_type,
        fact_refs=fact_refs,
        evidence_refs=evidence_refs,
    )


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
                reasoning_assessment=item.get("reasoning_assessment"),
            ))
        findings = [item for item in findings if item.statement]
        if not findings:
            raise ValueError("validated interpretation contains no reportable findings")
        title = self._title(bundle, interp)
        # The answer lead can be a concatenation of complete findings. It is
        # not an abstract: keep the overview separate from the closing verdict.
        topics = list(dict.fromkeys(
            _ANALYSIS_TOPICS.get(item.capability_id, "所选数据的科学结果")
            for item in bundle.methods
        ))
        summary = f"本次分析围绕{'、'.join(topics) or '所选数据的科学结果'}展开。"
        comparison = _comparison_finding(bundle, raw_findings)
        scopes = list(dict.fromkeys(str(item.get("scope") or "").strip().rstrip("。.") for item in raw_findings))
        aggregate_scope = _comparison_scope(bundle, raw_findings, comparison)
        if aggregate_scope:
            scopes = [aggregate_scope]
        # A scope repeated as the complete opening clause of a more specific
        # scope adds no information. Keep the longer qualified text intact;
        # never infer equivalence between different or conflicting scopes.
        scopes = [scope for scope in scopes if not any(
            other.startswith(scope) and len(other) > len(scope)
            and other[len(scope)] in "，,；;。 " for other in scopes
        )]
        scope_overview = _join_sentences([scope for scope in scopes if scope and scope != "current ScientificResult scope"])
        if bundle.provenance.model_dump(mode="json").get("execution_scope") == "PROJECT" and not bundle.source_object_refs:
            # Free-text interpretation scope may mention a reference's broader
            # coverage. The abstract describes this saved operation; it must
            # not promote those unprojected quantities to result claims.
            scope_overview = _join_sentences(["平台参考资料与本次参数" if bundle.provenance.model_dump(mode="json").get("reference_sources") else "本次输入参数或文本数据"])
        if scope_overview:
            scope_overview = "研究范围：" + scope_overview
        # Do not truncate a qualification mid-sentence when a mixed report has
        # many distinct scopes. The complete scopes remain with the findings.
        if len(scope_overview) <= 2000:
            summary = scope_overview + summary
        compact_conclusion = _diffusion_conclusion(bundle, raw_findings)
        if compact_conclusion is not None:
            summary += "扩散拟合已完成，但所选窗口未通过诊断判据。"
        if bundle.execution_status.value == "PARTIAL":
            summary = f"当前结果是部分完成的分析。{summary}"
        if relevance_status == "STALE":
            summary = f"这是针对原始 source version 的历史结果。{summary}"
        elif relevance_status == "SOURCE_MISSING":
            summary = f"原始来源当前不可获得，但历史结果仍可追溯。{summary}"
        elif relevance_status == "INVALIDATED":
            summary = f"该结果仅作为历史记录，不应视为当前有效证据。{summary}"
        figures = [_report_figure(item, bundle) for item in bundle.figures[:16]]
        supporting = [ReportSupportingResult(result_item_ref=item.id, description=item.title) for item in bundle.result_items if item.role.value == "SUPPORTING"][:32]
        limitations = [ReportLimitation(statement=item.message, source_refs=[item.limitation_id]) for item in bundle.limitations[:32]]
        limitations.extend(ReportLimitation(statement=str(value), source_refs=[]) for value in (interp.get("limitations") or [])[:16])
        # Validated per-finding limitations belong in the report's limitation
        # section even when the interpreter has no top-level limitations list.
        known_limitations = {item.statement for item in limitations}
        for finding in raw_findings:
            for value in (finding.get("reasoning_assessment") or {}).get("limitations", []):
                statement = str(value).strip()
                if statement and statement not in known_limitations and len(limitations) < 32:
                    limitations.append(ReportLimitation(statement=statement, source_refs=[]))
                    known_limitations.add(statement)
        if bundle.execution_status.value == "PARTIAL" and not any("partial" in item.statement.lower() or "部分" in item.statement for item in limitations):
            limitations.append(ReportLimitation(statement="部分执行步骤未完成；报告仅覆盖已提交的有效输出。", source_refs=[]))
        if relevance_status in {"STALE", "SOURCE_MISSING", "INVALIDATED"}:
            limitations.append(ReportLimitation(statement={"STALE": "报告基于历史 source version 生成。", "SOURCE_MISSING": "原始 source version 当前不可获得。", "INVALIDATED": "原始 source version 已被标记为失效。"}[relevance_status], source_refs=[]))
        if not limitations:
            limitations.append(ReportLimitation(
                statement="ScientificResult 未提供额外方法限制；报告不补充未来源的算法常识。",
                source_refs=[],
            ))
        limitations = _dedupe_limitations(limitations)
        methods = [
            _METHOD_SUMMARIES.get(
                item.capability_id,
                "方法信息来自已验证的 ScientificResult，并保留执行时的参数与来源版本。",
            )
            for item in bundle.methods[:16]
        ]
        method_summary = _join_sentences(methods) or "方法信息来自已验证的 ScientificResult。"
        evidence_refs = sorted({ref for item in findings for ref in item.evidence_refs} | {ref for item in figures for ref in item.evidence_refs} | {item.evidence_id for item in bundle.evidence})
        supporting_findings = [
            item for item in (interp.get("supporting_findings") or [])
            if isinstance(item, dict) and str(item.get("statement") or item.get("claim") or item.get("text") or "").strip()
        ][:8]
        scientific_supporting_findings = [
            item
            for item in supporting_findings
            if item.get("fact_refs", item.get("factRefs", []))
            and not any(_finding_content(item) == _finding_content(primary) for primary in raw_findings[:16])
        ]
        if scientific_supporting_findings:
            discussion_text = _join_sentences([
                str(item.get("statement") or item.get("claim") or item.get("text")).strip()
                for item in scientific_supporting_findings
            ])
            discussion_fact_refs = sorted({
                str(ref)
                for item in scientific_supporting_findings
                for ref in item.get("fact_refs", item.get("factRefs", []))
            })
            discussion_evidence_refs = sorted({
                str(ref)
                for item in scientific_supporting_findings
                for ref in item.get("evidence_refs", item.get("evidenceRefs", []))
            })
        else:
            # An optional discussion needs distinct validated content. Repeating
            # the primary findings does not add a scientific interpretation.
            discussion_text = ""
            # Legacy explicit discussion text may inherit these references.
            discussion_fact_refs = sorted({ref for item in findings[:4] for ref in item.fact_refs})
            discussion_evidence_refs = sorted({ref for item in findings[:4] for ref in item.evidence_refs})
        discussion = self._narrative_section(
            interp.get("discussion"),
            discussion_text,
            fact_refs=discussion_fact_refs,
            evidence_refs=discussion_evidence_refs,
        )
        conclusion = self._narrative_section(
            interp.get("conclusion"),
            _join_sentences([item.statement for item in findings]),
            # Keep complete statements and their qualifications together.
            # Never shorten arbitrary scientific prose at a sentence boundary.
            fact_refs=sorted({ref for item in findings for ref in item.fact_refs}),
            evidence_refs=sorted({ref for item in findings for ref in item.evidence_refs}),
        )
        if compact_conclusion is not None:
            conclusion = compact_conclusion
        elif not interp.get("conclusion"):
            conclusion = _regression_conclusion(bundle, raw_findings) or _comparison_conclusion(comparison) or conclusion
        next_steps_text = report_next_steps_text(interpretation, bundle)
        next_steps = ReportNarrativeSection(text=next_steps_text) if next_steps_text else None
        return ScientificReportOutput(
            title=title,
            research_question=bundle.research_question,
            summary=summary,
            discussion=discussion,
            conclusion=conclusion,
            next_steps=next_steps,
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
    def _narrative_section(
        value: Any,
        fallback: str,
        *,
        fact_refs: list[str],
        evidence_refs: list[str],
    ) -> ReportNarrativeSection | None:
        if isinstance(value, dict):
            text = str(value.get("text") or value.get("statement") or "").strip()
            fact_refs = [str(ref) for ref in value.get("fact_refs", value.get("factRefs", fact_refs))]
            evidence_refs = [str(ref) for ref in value.get("evidence_refs", value.get("evidenceRefs", evidence_refs))]
        else:
            text = str(value or "").strip()
        if not text:
            text = fallback.strip()
        # Optional roll-ups may exceed the contract when many topics are
        # combined. Their complete claims remain in main_findings; omitting a
        # redundant roll-up is safer than silently removing its citations.
        if not text or len(text) > 6000 or len(set(fact_refs)) > 32 or len(set(evidence_refs)) > 32:
            return None
        return ReportNarrativeSection(text=text, fact_refs=list(dict.fromkeys(fact_refs)), evidence_refs=list(dict.fromkeys(evidence_refs)))

    @staticmethod
    def _title(bundle: ScientificResultBundle, interpretation: dict[str, Any]) -> str:
        capabilities = {item.capability_id for item in bundle.methods}
        if {
            "structure.coordination_crystalnn",
            "structure.coordination_voronoinn",
        }.issubset(capabilities):
            return "CrystalNN 与 VoronoiNN 局部配位环境比较"
        title = str(interpretation.get("title") or "").strip()
        if title and title.lower() not in {"scientific analysis", "analysis report", "材料科学分析"}:
            return title
        if bundle.result_items:
            return bundle.result_items[0].title
        return bundle.research_question[:256]


def _finding_content(item: dict[str, Any]) -> dict[str, Any]:
    """Compare complete scoped content, excluding only its finding identity."""
    content = {key: value for key, value in item.items() if key not in {"finding_id", "claim_id", "reasoning_assessment"}}
    if item.get("reasoning_assessment") is not None:
        content["reasoning_assessment"] = {
            key: value for key, value in item["reasoning_assessment"].items() if key != "claim_id"
        }
    return content


def _join_sentences(sentences: list[str]) -> str:
    rendered: list[str] = []
    for sentence in sentences:
        text = sentence.strip()
        if not text:
            continue
        rendered.append(text if text.endswith(("。", "！", "？", ".", "!", "?")) else f"{text}。")
    return "".join(rendered)


def _comparison_finding(bundle: ScientificResultBundle, findings: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Select one validated comparison covering every exact primary source."""
    primary = [item for item in bundle.result_items if item.role.value == "PRIMARY"]
    if len(primary) < 2 or len({item.result_type for item in primary}) != 1:
        return None
    if any(len(item.scientific_object_refs) != 1 for item in primary):
        return None
    sources = {(ref.object_id, ref.version_id) for item in primary for ref in item.scientific_object_refs}
    if len(sources) != len(primary) or sources != {(ref.object_id, ref.version_id) for ref in bundle.source_object_refs}:
        return None
    facts = {fact.fact_id: fact for fact in bundle.facts}
    required_qualifiers = {str(value) for item in findings for value in
                           (item.get("reasoning_assessment") or {}).get("required_qualifiers", item.get("qualifiers") or [])}
    candidates = []
    for finding in findings:
        assessment = finding.get("reasoning_assessment") or {}
        if (assessment.get("accepted") is not True or assessment.get("outcome") != "SUPPORTED"
                or assessment.get("claim_type") != "QUANTITATIVE_COMPARISON"
                or assessment.get("contradicting_refs") or assessment.get("defects")
                or not str(finding.get("statement") or "").strip()
                or not str(assessment.get("scope") or finding.get("scope") or "").strip()):
            continue
        if any((item.get("reasoning_assessment") or {}).get("claim_type") != "DIRECT_OBSERVATION"
               or (item.get("reasoning_assessment") or {}).get("accepted") is not True
               or (item.get("reasoning_assessment") or {}).get("contradicting_refs")
               for item in findings if item is not finding):
            continue
        if not required_qualifiers.issubset(set(assessment.get("required_qualifiers", finding.get("qualifiers") or []))):
            continue
        refs = set(finding.get("fact_refs") or [])
        groups = [refs.intersection(item.fact_refs) for item in primary]
        if not refs or not refs.issubset(facts) or any(not group for group in groups):
            continue
        if set.union(*groups) != refs or sum(map(len, groups)) != len(refs):
            continue
        signatures = [{(facts[ref].predicate, facts[ref].unit) for ref in group} for group in groups]
        if any(len(signature) != len(group) or signature != signatures[0] for signature, group in zip(signatures, groups)):
            continue
        candidates.append(finding)
    return candidates[0] if len(candidates) == 1 else None


def _comparison_scope(bundle: ScientificResultBundle, findings: list[dict[str, Any]], comparison: dict[str, Any] | None) -> str | None:
    if comparison is None:
        return None
    qualifiers = set()
    covered_sources = set()
    primary = [item for item in bundle.result_items if item.role.value == "PRIMARY"]
    for finding in findings:
        if finding is comparison:
            continue
        owners = [item for item in primary if set(finding.get("fact_refs") or []).intersection(item.fact_refs)]
        if len(owners) != 1:
            return None
        source = owners[0].scientific_object_refs[0]
        name = source.display_name or ""
        scope = str(finding.get("scope") or "").strip().rstrip("。.")
        if not name or not scope.startswith(name + " "):
            return None
        qualifiers.add(scope[len(name):].strip())
        covered_sources.add((source.object_id, source.version_id))
    if len(qualifiers) != 1 or len(covered_sources) != len(primary):
        return None
    qualification = next(iter(qualifiers))
    count = len(primary)
    numerals = [str(count), "零一二三四五六七八九"[count]] if count < 10 else [str(count)]
    aggregate = str(comparison.get("scope") or "").strip().rstrip("。.")
    if qualification and aggregate in {f"{number}{classifier}{qualification}" for number in numerals for classifier in ("个", "份", "种")}:
        return aggregate
    return None


def _comparison_conclusion(finding: dict[str, Any] | None) -> ReportNarrativeSection | None:
    if finding is None:
        return None
    statement = str(finding["statement"]).strip()
    assessment = finding.get("reasoning_assessment") or {}
    qualifiers = assessment.get("required_qualifiers", finding.get("qualifiers") or [])
    scope = str(assessment.get("scope") or finding.get("scope") or "").strip()
    sentences = [statement, *(str(value) for value in qualifiers if str(value).strip() and str(value).rstrip("。.") not in statement)]
    if scope and scope.rstrip("。.") not in statement:
        sentences.append(f"适用范围：{scope}")
    return DeterministicScientificReportComposer._narrative_section(
        None, _join_sentences(list(dict.fromkeys(sentences))),
        fact_refs=list(finding.get("fact_refs") or []), evidence_refs=list(finding.get("evidence_refs") or []),
    )


def _regression_conclusion(bundle: ScientificResultBundle, findings: list[dict[str, Any]]) -> ReportNarrativeSection | None:
    """Keep complete validated overall assessments, not the entire sample list.

    This applies only to one unambiguous evaluation with one saved fact for
    each overall metric. Mixed topics/models keep their existing narrative.
    """
    primary = [item for item in bundle.result_items if item.role.value == "PRIMARY"]
    if len(primary) != 1 or primary[0].result_type != "ml.regression.evaluation":
        return None
    r2_predicate = "ml.r2"
    owned_facts = [fact for fact in bundle.facts if fact.fact_id in primary[0].fact_refs]
    if not any(fact.predicate == r2_predicate for fact in owned_facts):
        states = [fact for fact in owned_facts if fact.predicate == "ml.r2_status"]
        if len(states) != 1 or states[0].value != "undefined_constant_target":
            return None
        r2_predicate = "ml.r2_status"
    metrics = {predicate: [fact.fact_id for fact in owned_facts if fact.predicate == predicate]
               for predicate in ("ml.sample_count", "ml.mae", "ml.rmse", r2_predicate)}
    if any(len(refs) != 1 for refs in metrics.values()):
        return None
    required = {refs[0] for predicate, refs in metrics.items() if predicate != "ml.sample_count"}
    candidates = [item for item in findings if required.intersection(item.get("fact_refs", []))]
    # Each metric must have one unambiguous complete finding. Never choose
    # between overlapping assessments or conflate different analysis scopes.
    if any(sum(ref in item.get("fact_refs", []) for item in candidates) != 1 for ref in required):
        return None
    scopes = {str((item.get("reasoning_assessment") or {}).get("scope") or item.get("scope") or "").strip()
              for item in candidates}
    if len(candidates) > 1 and (len(scopes) != 1 or not next(iter(scopes))):
        return None
    statements = []
    for finding in candidates:
        statement = str(finding.get("statement") or "").strip()
        if not statement:
            return None
        assessment = finding.get("reasoning_assessment") or {}
        qualifications = list(dict.fromkeys(assessment.get("required_qualifiers", finding.get("qualifiers") or [])))
        statements.append(_join_sentences([statement, *(str(value) for value in qualifications if str(value).strip() and str(value).rstrip("。.") not in statement)]))
    text = _join_sentences(statements)
    if len(candidates) > 1:
        scope = next(iter(scopes)).rstrip("。.")
        if scope not in text:
            text = _join_sentences([text, f"适用范围：{scope}"])
    return DeterministicScientificReportComposer._narrative_section(
        None, text, fact_refs=list(dict.fromkeys(ref for item in candidates for ref in item.get("fact_refs", []))),
        evidence_refs=list(dict.fromkeys(ref for item in candidates for ref in item.get("evidence_refs", []))),
    )


def _diffusion_conclusion(bundle: ScientificResultBundle, findings: list[dict[str, Any]]) -> ReportNarrativeSection | None:
    """Render a saved rejection, never re-derive a regime from fit statistics.

    Only a single, unambiguous diffusion result can use this compact verdict.
    Mixed scientific topics and accepted/unknown statuses retain the complete
    validated findings instead of receiving a guessed generic conclusion.
    """
    primary = [item for item in bundle.result_items if item.role.value == "PRIMARY"]
    if not primary or any(item.result_type not in {"trajectory.msd", "trajectory.diffusion"} for item in primary):
        return None
    diffusion = [item for item in primary if item.result_type == "trajectory.diffusion"]
    if len(diffusion) != 1:
        return None
    result = diffusion[0]
    diagnostic = [fact for fact in bundle.facts if fact.fact_id in result.fact_refs and fact.predicate == "trajectory.diffusion_regime"]
    if len(diagnostic) != 1 or not isinstance(diagnostic[0].value, str):
        return None
    fact = diagnostic[0]
    reason = _DIFFUSION_REJECTIONS.get(fact.value)
    if reason is None:
        return None
    bound_findings = [item for item in findings if fact.fact_id in item.get("fact_refs", [])]
    if not bound_findings:
        return None
    scopes = list(dict.fromkeys(str(item.get("scope") or "").strip() for item in bound_findings))
    # Preserve source attribution and required qualifications from the already
    # validated finding. A user's declared synthetic scope is not tool proof.
    scope_text = _join_sentences([f"适用范围：{scope}" for scope in scopes if scope and scope != "current ScientificResult scope"])
    text = f"{reason}，所选窗口被拒绝，不能成立扩散系数。{scope_text}"
    qualifiers = list(dict.fromkeys(
        str(value) for item in bound_findings
        for value in (item.get("reasoning_assessment") or {}).get("required_qualifiers", item.get("qualifiers") or [])
        if str(value).strip()
    ))
    missing = [value for value in qualifiers if value not in text]
    if missing:
        text += f"适用限定：{'、'.join(missing)}。"
    if len(text) > 6000:
        return None
    return DeterministicScientificReportComposer._narrative_section(
        None, text,
        fact_refs=sorted({ref for item in bound_findings for ref in item.get("fact_refs", [])}),
        evidence_refs=sorted({ref for item in bound_findings for ref in item.get("evidence_refs", [])}),
    )


def _dedupe_limitations(limitations: list[ReportLimitation]) -> list[ReportLimitation]:
    deduped: list[ReportLimitation] = []
    positions: dict[str, int] = {}
    for item in limitations:
        # Reviewed translations of the same canonical method limitation.
        # Other qualifiers and wording remain distinct; never fuzzy-match prose.
        aliases = {
            "结果投影器未从 RDF 曲线推断峰位或配位壳层。": "The result projector does not infer peaks or coordination shells from the RDF curve.",
            "结果投影不会从 RDF 曲线中推断峰位或配位壳层。": "The result projector does not infer peaks or coordination shells from the RDF curve.",
        }
        key = " ".join(aliases.get(item.statement, item.statement).split()).casefold()
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
