from __future__ import annotations

from datetime import datetime, timezone
import json
import re
import uuid
from typing import Any, Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from mdi_api.config import load_settings
from mdi_api.database import create_engine_from_settings
from mdi_api.access import require_project_access
from mdi_api.db import (
    agent2_scientific_interpretations,
    data_profiles,
    datasets,
    jobs,
    messages,
    research_session_runs,
    research_turns,
    scientific_result_snapshots,
    sessions,
)
from mdi_api.interpretation.grounding import project_grounded_communication
from mdi_api.interpretation.projector import AssistantResponseProjector
from mdi_api.interpretation.schemas import ScientificInterpretationOutput
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_llm.research_roles import orchestrate_research_turn


class ResearchSessionCreate(BaseModel):
    title: str = Field(default="未命名研究", min_length=1, max_length=200)
    datasetId: str | None = None


class ResearchSessionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    pinned: bool | None = None
    lifecycle: str | None = Field(default=None, pattern="^(ACTIVE|ARCHIVED|TRASHED)$")


class ResearchSessionBulkActionRequest(BaseModel):
    sessionIds: list[str] = Field(min_length=1, max_length=100)
    action: Literal["PIN", "UNPIN", "ARCHIVE", "RESTORE", "TRASH"]

    @model_validator(mode="after")
    def unique_sessions(self) -> "ResearchSessionBulkActionRequest":
        self.sessionIds = list(
            dict.fromkeys(item.strip() for item in self.sessionIds if item.strip())
        )
        if not self.sessionIds:
            raise ValueError("At least one Research Session is required.")
        return self


class ResearchMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=16_384)
    datasetId: str | None = None


class ResearchAssistantProjectionCreate(BaseModel):
    phase: str = Field(pattern="^(pre_run|clarification|unsupported|failed|post_run)$")
    datasetName: str | None = Field(default=None, max_length=200)
    datasetId: str | None = None
    runId: str | None = Field(default=None, max_length=96)
    steps: list[str] = Field(default_factory=list, max_length=16)
    findings: list[str] = Field(default_factory=list, max_length=8)
    limitations: list[str] = Field(default_factory=list, max_length=8)
    candidates: list[str] = Field(default_factory=list, max_length=8)
    failureCode: str | None = Field(default=None, max_length=96)
    question: str | None = Field(default=None, max_length=16_384)
    provider: str | None = Field(default=None, max_length=64)
    model: str | None = Field(default=None, max_length=200)
    thinkingMode: str = Field(default="standard", pattern="^(quick|standard|deep)$")
    useProvider: bool = False


class ResearchRunBinding(BaseModel):
    sessionId: str = Field(min_length=1, max_length=64)
    jobId: str = Field(min_length=1, max_length=64)


class ScopeResolveRequest(BaseModel):
    question: str = Field(min_length=1, max_length=16_384)


_TOOL_USER_STEP_LABELS = {
    "structure.summary": "整理当前晶体结构的组成与晶格信息",
    "structure.xrd": "根据晶体结构生成理论 XRD 图谱",
    "structure.experimental_xrd_comparison": "比较实验峰与理论峰的位置和强度",
    "table.numeric_summary": "汇总数据中的数值属性",
    "table.property_distribution": "分析材料属性的分布特征",
    "trajectory.summary": "整理轨迹中的结构与时间信息",
    "trajectory.msd": "计算轨迹中的均方位移",
    "electronic.band_structure": "整理电子能带与能量参考",
    "electronic.dos": "整理电子态密度与能量分布",
    "phonon.band": "整理声子色散关系",
    "phonon.dos": "整理声子态密度",
    "phonon.band_dos": "组合声子色散与态密度",
    "phonon.animation": "准备声子振动模式",
    "structure.lattice_summary": "整理晶格参数",
    "structure.spacegroup_summary": "整理空间群信息",
    "structure.composition_from_structure": "从晶体结构提取组成信息",
    "structure.brillouin_zone": "生成布里渊区与高对称路径",
    "structure.volumetric_data": "整理体数据场",
    "structure.coordination_hist": "统计结构中的配位环境",
    "structure.coordination_crystalnn": "分析 CrystalNN 配位环境",
    "structure.coordination_voronoinn": "分析 VoronoiNN 配位环境",
    "structure.local_environment_polyhedra": "分析局部环境多面体",
    "structure.rdf": "计算结构径向分布函数（RDF）",
    "structure.trajectory_viewer": "整理分子动力学轨迹",
    "structure.trajectory_import": "读取分子动力学轨迹",
    "trajectory.viewer": "整理分子动力学轨迹",
    "trajectory.rdf": "计算轨迹径向分布函数（RDF）",
    "trajectory.diffusion": "根据均方位移估计扩散行为",
    "dataset.materials_explorer": "整理材料样本与属性概览",
    "dataset.composition_space": "分析材料组成空间",
    "ml.regression_evaluation": "评估材料属性回归结果",
    "ml.classification_evaluation": "评估材料分类结果",
    "ml.uncertainty_evaluation": "评估预测不确定性",
    "ml.basic_metrics": "汇总预测结果指标",
    "ml.density_scatter": "生成预测值与真实值关系图",
    "ml.error_distribution": "分析预测误差分布",
    "ml.outlier_table": "整理异常样本",
    "table.distribution_summary": "分析材料属性的分布特征",
    "viz.scatter": "生成材料属性关系图",
    "viz.histogram": "生成材料属性分布图",
    "viz.correlation": "计算材料属性之间的相关关系",
}

_TERMINAL_RESEARCH_TURN_STATUSES = (
    "COMPLETED",
    "PARTIAL",
    "FAILED",
    "CANCELED",
    "CANCELLED",
    "UNSUPPORTED",
    "ANSWERED",
    "NEEDS_CLARIFICATION",
)


def _user_facing_step_label(step: dict[str, Any]) -> str:
    tool_id = str(step.get("toolId") or step.get("tool_id") or "").strip()
    if tool_id in _TOOL_USER_STEP_LABELS:
        return _TOOL_USER_STEP_LABELS[tool_id]
    purpose = str(step.get("userFacingPurpose") or step.get("displayName") or step.get("purpose") or "").strip()
    if purpose and _is_user_facing_interpretation_text(purpose) and not _is_machine_plan_text(purpose):
        return purpose[:512]
    # Prefixes cover newly registered tools without exposing their internal
    # identity. Exact registry metadata remains preferred above.
    prefix_labels = (
        ("trajectory.", "分析分子动力学轨迹"),
        ("phonon.", "分析声子振动性质"),
        ("electronic.", "分析电子结构"),
        ("structure.", "分析晶体结构"),
        ("dataset.", "整理材料数据集"),
        ("composition.", "分析材料组成"),
        ("ml.", "评估材料属性模型"),
        ("table.", "整理材料属性表"),
        ("viz.", "生成材料属性可视化"),
    )
    for prefix, label in prefix_labels:
        if tool_id.startswith(prefix):
            return label
    return "整理当前数据中的科学信息"


def _is_machine_plan_text(value: str) -> bool:
    return bool(re.search(
        r"validated structured AnalysisIntent|eligible registered capability|exact (?:Intent|DataProfile|Registry)|"
        r"parameter-binding facts|inputref|registry\s*(?:hash|version)|plan[_\s-]?id|job[_\s-]?id|toolcall",
        value,
        flags=re.IGNORECASE,
    ))


def _is_user_facing_interpretation_text(value: object) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    return not re.search(
        r"(?:reported\s+(?:count|category|value)|artifact\s*\(s\)|projector|schema|contract|toolcall|inputref|plan[_\s-]?id|job[_\s-]?id|registry\s*(?:hash|version))",
        text,
        flags=re.IGNORECASE,
    )


def list_sessions(project_id: str, current_user: CurrentUser = Depends(get_current_user)) -> list[dict[str, Any]]:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        _require_project(connection, project_id, current_user)
        rows = connection.execute(
            select(sessions)
            .where(sessions.c.project_id == project_id)
            .order_by(sessions.c.is_pinned.desc(), sessions.c.created_at.desc())
        ).mappings().all()
        return [_session_view(row, connection) for row in rows]


def create_session(project_id: str, request: ResearchSessionCreate, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    session_id = f"research_{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc)
    requested_title = request.title.strip()
    title_override = (
        None
        if requested_title in {"新研究", "未命名研究"}
        else requested_title
    )
    with engine.begin() as connection:
        require_project_access(connection, project_id, current_user, write=True)
        if request.datasetId:
            _require_dataset_or_runtime(connection, project_id, request.datasetId)
        connection.execute(insert(sessions).values(
            id=session_id, project_id=project_id, dataset_id=request.datasetId,
            mode="project", status="active", title_override=title_override,
            is_pinned=False, created_by=current_user.id, created_at=now,
        ))
        row = connection.execute(select(sessions).where(sessions.c.id == session_id)).mappings().one()
        return _session_view(row, connection)


def get_session(session_id: str, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        row = connection.execute(select(sessions).where(sessions.c.id == session_id)).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="研究会话不存在。")
        _require_project(connection, row["project_id"], current_user)
        return _session_view(row, connection)


def update_session(
    session_id: str,
    request: ResearchSessionUpdate,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Update non-scientific Research Session metadata/lifecycle.

    Session lifecycle is a product-management projection. Historical
    ResearchTurns, Results, Artifacts and exact source references remain
    immutable and readable after archive/trash.
    """

    if request.title is None and request.pinned is None and request.lifecycle is None:
        raise HTTPException(status_code=400, detail="至少需要一个会话变更。")
    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        row = connection.execute(
            select(sessions).where(sessions.c.id == session_id).with_for_update()
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="研究会话不存在。")
        require_project_access(connection, row["project_id"], current_user, write=True)
        current_status = str(row["status"] or "active").lower()
        next_status = current_status
        pre_trash_status = row.get("pre_trash_status")
        if request.lifecycle is not None:
            requested_status = request.lifecycle.lower()
            if requested_status in {"archived", "trashed"}:
                active_turns = int(
                    connection.execute(
                        select(func.count()).select_from(research_turns).where(
                            research_turns.c.research_session_id == session_id,
                            func.upper(research_turns.c.status).not_in(
                                _TERMINAL_RESEARCH_TURN_STATUSES
                            ),
                        )
                    ).scalar_one()
                )
                if active_turns:
                    raise HTTPException(
                        status_code=409,
                        detail="研究仍在进行，完成或停止后才能归档或移入回收站。",
                    )
            if requested_status == "trashed":
                if current_status != "trashed":
                    pre_trash_status = (
                        current_status if current_status in {"active", "archived"} else "active"
                    )
                next_status = "trashed"
            elif requested_status == "archived":
                if current_status == "trashed":
                    raise HTTPException(status_code=409, detail="请先从回收站恢复研究记录。")
                next_status = "archived"
                pre_trash_status = None
            else:
                next_status = (
                    str(pre_trash_status)
                    if current_status == "trashed"
                    and str(pre_trash_status) in {"active", "archived"}
                    else "active"
                )
                pre_trash_status = None
        values: dict[str, Any] = {}
        if request.title is not None:
            values["title_override"] = request.title.strip()
        if request.pinned is not None:
            values["is_pinned"] = request.pinned
        if request.lifecycle is not None:
            values["status"] = next_status
            values["pre_trash_status"] = pre_trash_status
        if values:
            connection.execute(
                update(sessions).where(sessions.c.id == session_id).values(**values)
            )
        updated = connection.execute(select(sessions).where(sessions.c.id == session_id)).mappings().one()
        return _session_view(updated, connection)


def bulk_update_sessions(
    project_id: str,
    request: ResearchSessionBulkActionRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Atomically apply one organization/lifecycle action to Research Sessions.

    Every requested Session is locked and authorized before any mutation. This
    prevents a mixed selection, active Turn, or unauthorized Session from
    producing a partially applied bulk action.
    """

    engine = create_engine_from_settings(load_settings())
    with engine.begin() as connection:
        require_project_access(connection, project_id, current_user, write=True)
        rows = connection.execute(
            select(sessions)
            .where(sessions.c.id.in_(request.sessionIds))
            .order_by(sessions.c.id)
            .with_for_update()
        ).mappings().all()
        if len(rows) != len(request.sessionIds):
            raise HTTPException(status_code=404, detail="部分研究记录不存在。")
        if any(str(row["project_id"]) != str(project_id) for row in rows):
            raise HTTPException(status_code=403, detail="部分研究记录不属于当前项目。")

        if request.action in {"ARCHIVE", "TRASH"}:
            active_turns = int(
                connection.execute(
                    select(func.count()).select_from(research_turns).where(
                        research_turns.c.research_session_id.in_(request.sessionIds),
                        func.upper(research_turns.c.status).not_in(
                            _TERMINAL_RESEARCH_TURN_STATUSES
                        ),
                    )
                ).scalar_one()
            )
            if active_turns:
                raise HTTPException(
                    status_code=409,
                    detail="所选研究中仍有任务在进行，已取消全部批量变更。",
                )
        if request.action == "ARCHIVE" and any(
            str(row["status"] or "active").lower() == "trashed" for row in rows
        ):
            raise HTTPException(
                status_code=409,
                detail="所选研究包含回收站记录，请先恢复后再归档。",
            )

        if request.action in {"PIN", "UNPIN"}:
            connection.execute(
                update(sessions)
                .where(sessions.c.id.in_(request.sessionIds))
                .values(is_pinned=request.action == "PIN")
            )
        elif request.action == "ARCHIVE":
            connection.execute(
                update(sessions)
                .where(sessions.c.id.in_(request.sessionIds))
                .values(status="archived", pre_trash_status=None)
            )
        elif request.action == "TRASH":
            for row in rows:
                current_status = str(row["status"] or "active").lower()
                pre_trash_status = row.get("pre_trash_status")
                if current_status != "trashed":
                    pre_trash_status = (
                        current_status
                        if current_status in {"active", "archived"}
                        else "active"
                    )
                connection.execute(
                    update(sessions)
                    .where(sessions.c.id == row["id"])
                    .values(status="trashed", pre_trash_status=pre_trash_status)
                )
        else:
            for row in rows:
                current_status = str(row["status"] or "active").lower()
                pre_trash_status = row.get("pre_trash_status")
                next_status = (
                    str(pre_trash_status)
                    if current_status == "trashed"
                    and str(pre_trash_status) in {"active", "archived"}
                    else "active"
                )
                connection.execute(
                    update(sessions)
                    .where(sessions.c.id == row["id"])
                    .values(status=next_status, pre_trash_status=None)
                )

    return {
        "action": request.action,
        "sessionIds": request.sessionIds,
        "count": len(request.sessionIds),
    }


def bind_research_session_run(
    session_id: str,
    job_id: str,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Persist the one-to-one owning session for a Planner run.

    The binding is a presentation/history projection only. Planner, Job and
    Artifact authorities remain unchanged, while the server verifies both
    records belong to the same Project before writing the association.
    """

    engine = create_engine_from_settings(load_settings())
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        session = connection.execute(
            select(sessions).where(sessions.c.id == session_id)
        ).mappings().first()
        if not session:
            raise HTTPException(status_code=404, detail="研究会话不存在。")
        require_project_access(connection, session["project_id"], current_user, write=True)
        job = connection.execute(
            select(jobs).where(jobs.c.id == job_id)
        ).mappings().first()
        if not job:
            raise HTTPException(status_code=404, detail="分析运行不存在。")
        if str(job["project_id"]) != str(session["project_id"]):
            raise HTTPException(status_code=403, detail="分析运行不属于当前项目。")
        bound = _bind_run(connection, session_id=session_id, job_id=job_id, created_at=now)
        return {
            "sessionId": session_id,
            "jobId": job_id,
            # Older installations can still serve historical sessions before
            # migration 0014 is applied. Keep that read/write path honest: the
            # run exists, but its normalized history link is pending migration.
            "bindingStatus": "bound" if bound else "migration_required",
        }


def validate_research_session_project(
    session_id: str,
    project_id: str,
    current_user: CurrentUser,
) -> None:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        session = connection.execute(
            select(sessions).where(sessions.c.id == session_id)
        ).mappings().first()
        if not session:
            raise HTTPException(status_code=404, detail="研究会话不存在。")
        if str(session["project_id"]) != str(project_id):
            raise HTTPException(status_code=403, detail="研究会话不属于当前项目。")
        require_project_access(connection, project_id, current_user, write=True)


def reconcile_research_run_projection(
    job_id: str,
    current_user: CurrentUser,
    *,
    phase: str = "post_run",
    failure_code: str | None = None,
) -> dict[str, Any] | None:
    """Reconcile a terminal assistant message from persisted run facts."""

    engine = create_engine_from_settings(load_settings())
    try:
        with engine.connect() as connection:
            # A modern Agent2 turn is the authoritative session binding. Use
            # it first so terminal interpretation reconciliation works even
            # when the legacy compatibility projection is absent.
            binding = connection.execute(
                select(research_turns.c.research_session_id.label("session_id"), jobs.c.dataset_id)
                .join(jobs, jobs.c.id == research_turns.c.job_id)
                .where(research_turns.c.job_id == job_id, research_turns.c.research_session_id.is_not(None))
                .order_by(research_turns.c.created_at.desc(), research_turns.c.id.desc())
            ).mappings().first()
            if not binding:
                binding = connection.execute(
                    select(research_session_runs.c.session_id, jobs.c.dataset_id)
                    .join(jobs, jobs.c.id == research_session_runs.c.job_id)
                    .where(research_session_runs.c.job_id == job_id)
                ).mappings().first()
    except SQLAlchemyError as exc:
        if "research_turns" not in str(exc).lower() and "research_session_runs" not in str(exc).lower():
            raise
        # Rolling deployments may lack one of the additive relation tables;
        # retain the legacy compatibility path when it is still available.
        try:
            with engine.connect() as connection:
                binding = connection.execute(
                    select(research_session_runs.c.session_id, jobs.c.dataset_id)
                    .join(jobs, jobs.c.id == research_session_runs.c.job_id)
                    .where(research_session_runs.c.job_id == job_id)
                ).mappings().first()
        except SQLAlchemyError as fallback_exc:
            if "research_session_runs" in str(fallback_exc).lower():
                return None
            raise
    if not binding:
        return None
    return create_assistant_projection(
        str(binding["session_id"]),
        ResearchAssistantProjectionCreate(
            phase=phase,
            datasetId=str(binding["dataset_id"]) if binding["dataset_id"] else None,
            runId=job_id,
            failureCode=failure_code,
        ),
        current_user,
    )


def create_message(session_id: str, request: ResearchMessageCreate, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    message_id = f"message_{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc)
    content = request.content.strip()
    with engine.begin() as connection:
        session = connection.execute(select(sessions).where(sessions.c.id == session_id)).mappings().first()
        if not session:
            raise HTTPException(status_code=404, detail="研究会话不存在。")
        require_project_access(connection, session["project_id"], current_user, write=True)
        if str(session["status"] or "active").lower() != "active":
            raise HTTPException(status_code=409, detail="归档或回收的研究记录不可继续写入，请先恢复。")
        if request.datasetId:
            _require_dataset_or_runtime(connection, session["project_id"], request.datasetId)
            # `sessions` intentionally has no mutable updated_at column in the
            # current contract.  Message.created_at is the durable activity
            # clock used by the session view, so only bind the selected dataset.
            connection.execute(
                update(sessions)
                .where(sessions.c.id == session_id)
                .values(dataset_id=request.datasetId)
            )
        connection.execute(insert(messages).values(
            id=message_id, session_id=session_id, role="user", content_summary=content,
            payload_json={"source": "research_composer"}, created_at=now,
        ))
        row = connection.execute(select(messages).where(messages.c.id == message_id)).mappings().one()
        return _message_view(row)


def create_assistant_projection(
    session_id: str,
    request: ResearchAssistantProjectionCreate,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Persist a user-facing assistant projection without exposing CoT.

    The client supplies only bounded observable facts.  The server owns the
    copy, phase identity and durable assistant role.
    """

    engine = create_engine_from_settings(load_settings())
    now = datetime.now(timezone.utc)
    with engine.begin() as connection:
        session = connection.execute(
            select(sessions).where(sessions.c.id == session_id)
        ).mappings().first()
        if not session:
            raise HTTPException(status_code=404, detail="研究会话不存在。")
        require_project_access(connection, session["project_id"], current_user, write=True)
        dataset_name = request.datasetName
        if request.datasetId:
            dataset = _require_dataset_or_runtime(connection, session["project_id"], request.datasetId)
            dataset_name = str(dataset.get("name") or dataset_name or "") or None
        projection = request.model_copy(update={"datasetName": dataset_name})
        projection_metadata: dict[str, Any] = {}
        if request.runId:
            existing = _existing_run_projection(
                connection,
                session_id=session_id,
                run_id=request.runId,
                phase=request.phase,
            )
            if existing is not None:
                return _message_view(existing)
            run = _require_run_for_project(request.runId, session["project_id"])
            _bind_run(connection, session_id=session_id, job_id=request.runId, created_at=now)
            projection, projection_metadata = _ground_projection_from_run(projection, run)
        content = _assistant_projection_text(projection)
        if projection.phase == "pre_run" and projection.useProvider:
            content, role_metadata = _provider_research_turn_text(projection, content)
            projection_metadata.update(role_metadata)
        message_id = f"message_{uuid.uuid4().hex}"
        connection.execute(insert(messages).values(
            id=message_id,
            session_id=session_id,
            role="agent",
            content_summary=content,
            payload_json={
                "source": "research_assistant_projection",
                "phase": request.phase,
                "runId": request.runId,
                "datasetId": request.datasetId,
                "projectionVersion": "ResearchAssistantProjection/1.0",
                "researchRole": "scientific_interpreter" if request.phase == "post_run" else "research_turn_orchestrator",
                **projection_metadata,
            },
            created_at=now,
        ))
        row = connection.execute(
            select(messages).where(messages.c.id == message_id)
        ).mappings().one()
        return _message_view(row)


def resolve_scope(project_id: str, request: ScopeResolveRequest, current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    engine = create_engine_from_settings(load_settings())
    with engine.connect() as connection:
        _require_project(connection, project_id, current_user)
        dataset_rows = connection.execute(select(datasets).where(datasets.c.project_id == project_id).order_by(datasets.c.created_at.asc())).mappings().all()
        catalog: list[dict[str, Any]] = []
        for dataset in dataset_rows:
            profile = connection.execute(select(data_profiles).where(data_profiles.c.dataset_id == dataset["id"]).order_by(data_profiles.c.created_at.desc())).mappings().first()
            profile_json = dict(profile["profile_json"] or {}) if profile else {}
            catalog.append({
                "datasetId": dataset["id"], "name": dataset["name"], "status": dataset["status"],
                "profileId": profile["id"] if profile else None, "profileReady": bool(profile),
                "semantics": _semantic_names(profile_json), "files": _file_names(dataset),
            })
    catalog = _merge_runtime_catalog(project_id, catalog)
    question = request.question.strip().lower()
    if not catalog:
        return {"outcome": "UNSUPPORTED", "status": "UNSUPPORTED", "message": "项目中还没有可用于分析的数据。", "reason": "项目中还没有可用于分析的数据。", "catalog": []}
    if "预测误差" in question and not any("prediction" in x for item in catalog for x in item["semantics"]):
        return {"outcome": "UNSUPPORTED", "status": "UNSUPPORTED", "message": "当前数据缺少真实值和预测值列，无法计算预测误差。", "reason": "当前数据缺少真实值和预测值列，无法计算预测误差。", "catalog": catalog}
    scored = sorted(((sum(1 for token in _tokens(question) if token in json.dumps(item, ensure_ascii=False).lower()), item) for item in catalog), key=lambda value: value[0], reverse=True)
    if len(scored) == 1 or (scored[0][0] > 0 and (len(scored) == 1 or scored[0][0] > scored[1][0])):
        item = scored[0][1]
        return {"outcome": "READY", "status": "READY", "datasetId": item["datasetId"], "dataset_id": item["datasetId"], "profileId": item["profileId"], "profile_id": item["profileId"], "dataset": item, "dataset_name": item["name"], "available_semantics": item["semantics"], "catalog": catalog}
    if len(catalog) > 1:
        return {"outcome": "NEEDS_CLARIFICATION", "status": "NEEDS_CLARIFICATION", "message": "这个问题可能涉及多个数据集，请先选择本次分析使用的数据。", "reason": "这个问题可能涉及多个数据集，请先选择本次分析使用的数据。", "candidates": catalog, "catalog": catalog}
    item = catalog[0]
    return {"outcome": "READY", "status": "READY", "datasetId": item["datasetId"], "dataset_id": item["datasetId"], "profileId": item["profileId"], "profile_id": item["profileId"], "dataset": item, "dataset_name": item["name"], "available_semantics": item["semantics"], "catalog": catalog}


def _require_project(connection, project_id: str, current_user: CurrentUser) -> dict[str, Any]:
    return require_project_access(connection, project_id, current_user)


def _assistant_projection_text(request: ResearchAssistantProjectionCreate) -> str:
    dataset = request.datasetName or "当前已选择的数据"
    if request.phase == "pre_run":
        steps = [item.strip() for item in request.steps if item.strip()][:4]
        projection = orchestrate_research_turn(
            "本次项目研究",
            scope={"status": "READY", "dataset_name": dataset},
            plan={"steps": [{"userFacingPurpose": item} for item in steps]},
        )
        return projection.assistantMessage
    if request.phase == "clarification":
        projection = orchestrate_research_turn(
            "请选择数据范围",
            scope={"status": "NEEDS_CLARIFICATION", "candidates": [{"name": item} for item in request.candidates if item.strip()]},
        )
        return projection.assistantMessage
    if request.phase == "unsupported":
        return f"当前 {dataset} 缺少完成这项分析所需的科学属性，因此没有创建分析运行。"
    if request.phase == "failed":
        code = str(request.failureCode or "").upper()
        if code == "COORDINATION_ALGORITHM_CLARIFICATION_REQUIRED":
            return "径向分布可以直接计算；局部环境分析还需要确认使用 CrystalNN 还是 VoronoiNN 配位算法。确认后再创建分析运行。"
        if code == "DIFFUSION_FIT_WINDOW_REQUIRED":
            return "扩散估计需要明确拟合时间窗，或明确使用当前数据提供的完整时间范围。确认前不会创建分析运行。"
        if code == "DIFFUSION_FIT_WINDOW_INVALID":
            return "扩散拟合时间窗无效：起始时间必须早于结束时间。请修正区间后再提交。"
        if code == "DIFFUSION_FIT_WINDOW_OUT_OF_RANGE":
            return "扩散拟合时间窗超出当前轨迹的可验证时间范围。请选择范围内的区间，或明确使用完整提供范围。"
        if code == "DIFFUSION_TIME_RANGE_UNAVAILABLE":
            return "当前轨迹没有可验证的时间语义，因此不会推断扩散系数。可以先计算均方位移并保留这一限制。"
        if code == "NEEDS_CLARIFICATION":
            return "当前问题还缺少一个会改变科学方法的选择。请补充方法、范围或数据选择；确认前不会创建分析运行。"
        if "CAPABILITY" in code or "ELIGIB" in code:
            return "当前已验证的分析能力无法完整覆盖这个问题。请尝试缩小问题范围，或选择更匹配的数据。没有创建分析运行。"
        if "DURABLE_ROOT_INPUTS" in code:
            return "当前数据尚未准备好用于执行分析。请等待导入完成后重试。没有创建分析运行。"
        if "PROVIDER" in code:
            return "研究助手暂时无法准备分析方案。请检查模型设置后重试。没有创建分析运行。"
        return "分析方案未能通过当前数据和科学能力的验证，因此没有创建分析运行。"
    findings = [item.strip() for item in request.findings if item.strip()][:3]
    limitations = [item.strip() for item in request.limitations if item.strip()][:2]
    parts = ["分析已经完成。"]
    if findings:
        parts.append("\n".join(findings))
    if limitations:
        parts.append("当前限制：" + "；".join(limitations))
    parts.append("可以在右侧查看科学结果、依据与来源。")
    return "\n\n".join(parts)


def _provider_research_turn_text(
    request: ResearchAssistantProjectionCreate,
    fallback: str,
) -> tuple[str, dict[str, Any]]:
    """Run the advisory Research Turn role and fail closed to grounded copy.

    The model receives only the research question, selected dataset name and
    persisted user-facing Plan steps. It cannot create or alter an executable
    AnalysisPlan, and its JSON must pass ``ResearchTurnProjection`` validation
    before any text is persisted.
    """

    try:
        from mdi_api.routers.planner import _planner_user_config_from_request, _select_planner_provider

        selected_provider = _select_planner_provider(request.provider)
        config = _planner_user_config_from_request(request, selected_provider=selected_provider)
        question = str(request.question or "本次项目研究").strip()
        facts = {
            "question": question,
            "selectedDataset": request.datasetName or "当前已选择的数据",
            "validatedPlanSteps": list(request.steps[:16]),
        }
        response = selected_provider.generate_research_turn(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是材料研究助手。仅返回 JSON，不输出隐藏推理。"
                        "字段必须是 schemaVersion='1.0', mode='analyze', assistantMessage, "
                        "scientificIntent, scopeHints, planSummary, clarificationQuestion=null, "
                        "sessionTitleCandidate, groundingRefs。不得添加数字、单位、材料、证据或执行步骤；"
                        "只能改写给定问题、数据集名称和已验证分析步骤。"
                    ),
                },
                {"role": "user", "content": json.dumps(facts, ensure_ascii=False, separators=(",", ":"))},
            ],
            user_config=config,
        )
        projection = orchestrate_research_turn(
            question,
            scope={"status": "READY", "dataset_name": request.datasetName},
            plan={"steps": [{"userFacingPurpose": item} for item in request.steps]},
            provider_payload=response.raw_json,
        )
        if projection.mode != "analyze":
            raise ValueError("Research Turn Provider returned an incompatible mode")
        return projection.assistantMessage, {
            "llmRoleExecution": "provider_validated",
            "llmRoleProvider": request.provider or getattr(getattr(selected_provider, "meta", None), "name", "configured"),
            "llmRoleModel": response.model,
        }
    except Exception:
        return fallback, {"llmRoleExecution": "grounded_fallback"}


def _require_dataset(connection, project_id: str, dataset_id: str) -> dict[str, Any]:
    row = connection.execute(select(datasets).where(datasets.c.id == dataset_id, datasets.c.project_id == project_id)).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="数据集不存在。")
    return row


def _require_dataset_or_runtime(connection, project_id: str, dataset_id: str) -> dict[str, Any]:
    try:
        return _require_dataset(connection, project_id, dataset_id)
    except HTTPException:
        from mdi_api.phase2_runtime import get_phase2_runtime

        dataset = get_phase2_runtime().datasets.get(dataset_id)
        if dataset is None or dataset.project_id != project_id:
            raise
        return dataset.summary()


def _existing_run_projection(
    connection: Any,
    *,
    session_id: str,
    run_id: str,
    phase: str,
) -> Any | None:
    rows = connection.execute(
        select(messages)
        .where(messages.c.session_id == session_id, messages.c.role == "agent")
        .order_by(messages.c.created_at.asc())
    ).mappings().all()
    for row in rows:
        payload = row["payload_json"] or {}
        if (
            payload.get("source") == "research_assistant_projection"
            and payload.get("runId") == run_id
            and payload.get("phase") == phase
        ):
            return row
    return None


def _ground_projection_from_run(
    request: ResearchAssistantProjectionCreate,
    run: dict[str, Any],
) -> tuple[ResearchAssistantProjectionCreate, dict[str, Any]]:
    """Project user copy only from persisted, validated execution facts."""

    plan = run.get("analysisPlan") or {}
    if request.phase == "pre_run":
        steps = []
        for step in plan.get("steps") or []:
            if not isinstance(step, dict):
                continue
            label = _user_facing_step_label(step)
            if label:
                steps.append(label)
        return request.model_copy(update={"steps": steps[:16], "findings": [], "limitations": []}), {
            "groundedBy": ["analysis_plan"],
            "planHash": run.get("planHash"),
        }
    if request.phase != "post_run":
        return request, {}

    from mdi_api.routers.planner import list_planner_job_interpretations

    interpretation_result = list_planner_job_interpretations(str(request.runId))
    interpretations = interpretation_result.get("interpretations") or []
    if not interpretations:
        raise HTTPException(status_code=409, detail="科学解释尚未生成，暂时不能写入完成回应。")
    interpretation = interpretations[0]
    # Prefer the strict role projection when the secured Evidence endpoint is
    # available. Older/local records may not expose evidence in the list
    # response, so retain the existing grounded claim fallback for compatibility.
    try:
        from mdi_api.routers.planner import get_planner_interpretation_evidence
        from mdi_llm.research_roles import project_grounded_interpretation

        evidence_response = get_planner_interpretation_evidence(str(interpretation.get("interpretationId")))
        evidence_items = evidence_response.get("evidenceItems") or []
        artifact_ids = [str(item.get("sourceArtifactId")) for item in evidence_items if isinstance(item, dict) and item.get("sourceArtifactId")]
        projected = project_grounded_interpretation(
            interpretation,
            evidence_items=evidence_items,
            artifact_ids=artifact_ids,
        )
        if projected.findings:
            return request.model_copy(update={"steps": [], "findings": [item.text for item in projected.findings[:8]], "limitations": projected.limitations[:8]}), {
                "groundedBy": ["scientific_interpretation", "evidence_contract"],
                "interpretationId": interpretation.get("interpretationId"),
                "bundleId": interpretation.get("bundleId"),
            }
    except Exception:
        # Compatibility fallback below remains bounded and filters technical
        # interpretation copy before it reaches a durable assistant message.
        pass
    claims = interpretation.get("claims") or []
    findings = [
        str(item.get("renderedText")).strip()
        for item in claims
        if isinstance(item, dict)
        and item.get("claimType") != "LIMITATION"
        and _is_user_facing_interpretation_text(item.get("renderedText"))
    ]
    limitations = [
        str(item).strip()
        for item in interpretation.get("globalLimitations") or []
        if _is_user_facing_interpretation_text(item)
    ]
    limitations.extend(
        str(item.get("renderedText")).strip()
        for item in claims
        if isinstance(item, dict)
        and item.get("claimType") == "LIMITATION"
        and _is_user_facing_interpretation_text(item.get("renderedText"))
    )
    return request.model_copy(update={"steps": [], "findings": findings[:8], "limitations": limitations[:8]}), {
        "groundedBy": ["scientific_interpretation"],
        "interpretationId": interpretation.get("interpretationId"),
        "bundleId": interpretation.get("bundleId"),
    }


def _require_run_for_project(run_id: str, project_id: str) -> dict[str, Any]:
    """Ensure a persisted assistant projection cannot reference another Project."""

    try:
        from mdi_api.routers.planner import get_planner_job

        job = get_planner_job(run_id)
        job_project = str(job.get("projectId") or job.get("project_id") or "")
        if job_project and job_project != project_id:
            raise HTTPException(status_code=403, detail="运行结果不属于当前项目。")
        if job_project:
            return job
    except HTTPException:
        raise
    except Exception:
        pass
    try:
        from mdi_api.phase2_runtime import get_phase2_job

        job = get_phase2_job(run_id)
        if str(job.get("projectId") or job.get("project_id") or "") != project_id:
            raise HTTPException(status_code=403, detail="运行结果不属于当前项目。")
        return job
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=404, detail="运行结果不存在。") from exc


def _merge_runtime_catalog(project_id: str, catalog: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Include parsed local-runtime datasets missing from the SQL catalog."""

    from mdi_api.phase2_runtime import get_phase2_runtime

    known = {str(item.get("datasetId")) for item in catalog}
    runtime = get_phase2_runtime()
    for dataset in runtime.datasets.values():
        if dataset.project_id != project_id or dataset.id in known:
            continue
        profile = dataset.profile.model_dump(mode="json")
        catalog.append({
            "datasetId": dataset.id,
            "name": dataset.name,
            "status": dataset.status,
            "profileId": dataset.profile.profileId,
            "profileReady": True,
            "semantics": _semantic_names(profile),
            "files": [str(item.get("name") or item.get("fileName") or "") for item in dataset.files],
        })
    return catalog


def _session_view(row, connection) -> dict[str, Any]:
    message_rows = connection.execute(select(messages).where(messages.c.session_id == row["id"]).order_by(messages.c.created_at.asc())).mappings().all()
    scientific_message_projections = _scientific_message_projections(
        message_rows,
        connection,
        project_id=str(row["project_id"]),
    )
    created_at = _iso(row["created_at"])
    first_question = next((str(item["content_summary"]).strip() for item in message_rows if item["role"] == "user" and str(item["content_summary"]).strip()), "")
    title_override = str(row.get("title_override") or "").strip()
    generated_title = first_question[:56] + ("…" if len(first_question) > 56 else "") if first_question else "新研究"
    title = title_override or generated_title
    latest_message_at = _iso(message_rows[-1]["created_at"]) if message_rows else created_at
    try:
        run_rows = connection.execute(
            select(
                research_session_runs.c.job_id,
                research_session_runs.c.created_at,
                research_turns.c.id.label("research_turn_id"),
            )
            .join(jobs, jobs.c.id == research_session_runs.c.job_id)
            .outerjoin(research_turns, research_turns.c.job_id == research_session_runs.c.job_id)
            .where(research_session_runs.c.session_id == row["id"], jobs.c.project_id == row["project_id"])
            .order_by(research_session_runs.c.created_at.asc(), research_session_runs.c.job_id.asc())
        ).mappings().all()
    except SQLAlchemyError as exc:
        if "research_session_runs" not in str(exc).lower():
            raise
        # A pre-0014 local database remains readable while migrations are
        # pending. Message payloads are compatibility evidence, not the new
        # association authority.
        seen: set[str] = set()
        run_rows = []
        for item in message_rows:
            payload = item["payload_json"] or {}
            job_id = str(payload.get("runId") or "") if isinstance(payload, dict) else ""
            if job_id and job_id not in seen:
                seen.add(job_id)
                run_rows.append({"job_id": job_id, "created_at": item["created_at"]})
    # Modern Agent2 turns are authoritative for the session relationship. A
    # turn can legitimately exist without the legacy compatibility row, so
    # merge those direct bindings into the session projection as well. This
    # keeps run-only history links resolvable without inferring identity from
    # a Job identifier string.
    try:
        direct_turn_rows = connection.execute(
            select(
                research_turns.c.job_id,
                research_turns.c.created_at,
                research_turns.c.id.label("research_turn_id"),
            )
            .join(jobs, jobs.c.id == research_turns.c.job_id)
            .where(
                research_turns.c.research_session_id == row["id"],
                research_turns.c.project_id == row["project_id"],
                research_turns.c.job_id.is_not(None),
                jobs.c.project_id == row["project_id"],
            )
            .order_by(research_turns.c.created_at.asc(), research_turns.c.id.asc())
        ).mappings().all()
    except SQLAlchemyError as exc:
        if "research_turns" not in str(exc).lower():
            raise
        direct_turn_rows = []
    by_job = {str(item["job_id"]): item for item in run_rows}
    for item in direct_turn_rows:
        by_job[str(item["job_id"])] = item
    run_rows = sorted(
        by_job.values(),
        key=lambda item: (_iso(item["created_at"]), str(item["job_id"])),
    )
    run_references = [{
        "jobId": item["job_id"],
        "createdAt": _iso(item["created_at"]),
        "researchTurnId": str(item["research_turn_id"]) if item.get("research_turn_id") else None,
    } for item in run_rows]
    return {
        "id": row["id"],
        "projectId": row["project_id"],
        "project_id": row["project_id"],
        "datasetId": row["dataset_id"],
        "dataset_id": row["dataset_id"],
        "title": title,
        "status": row["status"],
        "pinned": bool(row.get("is_pinned")),
        "createdAt": created_at,
        "created_at": created_at,
        "updated_at": latest_message_at,
        "messages": [
            _message_view(
                item,
                content_override=scientific_message_projections.get(str(item["id"])),
            )
            for item in message_rows
        ],
        "runIds": [item["job_id"] for item in run_rows],
        "runReferences": run_references,
    }


def _message_view(row, *, content_override: str | None = None) -> dict[str, Any]:
    created_at = _iso(row["created_at"])
    payload = dict(row["payload_json"] or {})
    if content_override is not None:
        payload["contentProjection"] = "GROUNDED_READ_MODEL_2_0"
    return {
        "id": row["id"],
        "sessionId": row["session_id"],
        "session_id": row["session_id"],
        "role": "assistant" if row["role"] == "agent" else row["role"],
        "content": content_override if content_override is not None else row["content_summary"],
        "payload": payload,
        "createdAt": created_at,
        "created_at": created_at,
    }


def _scientific_message_projections(
    message_rows: list[Any],
    connection: Any,
    *,
    project_id: str,
) -> dict[str, str]:
    """Batch-project historical scientific finals through current grounding.

    Persisted Message content remains immutable audit evidence. The session
    read model uses the exact persisted Interpretation and Result to present a
    bounded, current communication projection without N+1 queries or any
    scientific recomputation.
    """
    message_by_interpretation: dict[uuid.UUID, list[str]] = {}
    for row in message_rows:
        payload = row["payload_json"] or {}
        if (
            row["role"] != "agent"
            or payload.get("messageKind") != "ASSISTANT_FINAL"
            or payload.get("source") != "agent2_scientific_interpreter"
        ):
            continue
        try:
            interpretation_id = uuid.UUID(str(payload.get("interpretationId")))
        except (TypeError, ValueError):
            continue
        message_by_interpretation.setdefault(interpretation_id, []).append(str(row["id"]))
    if not message_by_interpretation:
        return {}
    try:
        interpretation_rows = connection.execute(
            select(agent2_scientific_interpretations).where(
                agent2_scientific_interpretations.c.id.in_(
                    list(message_by_interpretation)
                ),
                agent2_scientific_interpretations.c.project_id == project_id,
            )
        ).mappings().all()
        snapshot_ids = [row["result_snapshot_id"] for row in interpretation_rows]
        snapshot_rows = connection.execute(
            select(scientific_result_snapshots).where(
                scientific_result_snapshots.c.id.in_(snapshot_ids),
                scientific_result_snapshots.c.project_id == project_id,
            )
        ).mappings().all()
    except SQLAlchemyError:
        # Pre-Phase-6 compatibility databases remain readable; no historical
        # content is rewritten or treated as a new scientific authority.
        return {}
    snapshots = {row["id"]: row for row in snapshot_rows}
    projected: dict[str, str] = {}
    projector = AssistantResponseProjector()
    for interpretation_row in interpretation_rows:
        snapshot = snapshots.get(interpretation_row["result_snapshot_id"])
        if (
            snapshot is None
            or str(interpretation_row["project_id"]) != project_id
            or str(snapshot["project_id"]) != project_id
        ):
            continue
        try:
            bundle = ScientificResultBundle.model_validate(snapshot["bundle_json"])
            raw = (interpretation_row["output_json"] or {}).get("interpretation")
            interpretation = project_grounded_communication(
                ScientificInterpretationOutput.model_validate(raw),
                bundle,
            )
            content = projector.project(
                interpretation,
                bundle,
                effective_relevance=bundle.relevance_status.value,
            )
        except (TypeError, ValueError):
            continue
        for message_id in message_by_interpretation.get(interpretation_row["id"], []):
            projected[message_id] = content
    return projected


def _bind_run(connection: Any, *, session_id: str, job_id: str, created_at: datetime) -> bool:
    try:
        existing = connection.execute(
            select(research_session_runs).where(research_session_runs.c.job_id == job_id)
        ).mappings().first()
    except SQLAlchemyError as exc:
        # Migration 0014 is additive. A rolling deployment may briefly run an
        # API process against the pre-migration database; do not turn a valid
        # Planner run or assistant projection into a 500 during that window.
        if "research_session_runs" in str(exc).lower():
            return False
        raise
    if existing and str(existing["session_id"]) != str(session_id):
        raise HTTPException(status_code=409, detail="分析运行已关联到其他研究会话。")
    if not existing:
        try:
            connection.execute(
                insert(research_session_runs).values(
                    session_id=session_id,
                    job_id=job_id,
                    created_at=created_at,
                )
            )
        except SQLAlchemyError as exc:
            if "research_session_runs" in str(exc).lower():
                return False
            raise
    return True


def _semantic_names(profile_json: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("recognizedProperties", "recognized_properties", "semantics", "recognizedSemantics"):
        candidate = profile_json.get(key)
        if isinstance(candidate, list):
            values.extend(str(item.get("name", item.get("semanticId", item))) if isinstance(item, dict) else str(item) for item in candidate)
    for column in profile_json.get("semanticColumns") or []:
        if not isinstance(column, dict):
            continue
        if column.get("column"):
            values.append(str(column["column"]))
        for role in column.get("roles") or []:
            if isinstance(role, dict) and role.get("role"):
                values.append(str(role["role"]))
    for resource in profile_json.get("resourceSemantics") or []:
        if not isinstance(resource, dict):
            continue
        values.extend(str(capability) for capability in resource.get("capabilities") or [])
    for readiness in profile_json.get("analysisReadiness") or []:
        if not isinstance(readiness, dict):
            continue
        if readiness.get("dataStatus") == "READY" and readiness.get("platformStatus") == "AVAILABLE" and readiness.get("capability"):
            values.append(str(readiness["capability"]))
    return sorted(set(values))[:80]


def _file_names(dataset: dict[str, Any]) -> list[str]:
    metadata = dataset.get("metadata_json") or {}
    files = metadata.get("files", []) if isinstance(metadata, dict) else []
    return [str(item.get("name", item)) if isinstance(item, dict) else str(item) for item in files][:80]


def _tokens(value: str) -> set[str]:
    return {token for token in value.replace("，", " ").replace("、", " ").split() if len(token) > 1}


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None
