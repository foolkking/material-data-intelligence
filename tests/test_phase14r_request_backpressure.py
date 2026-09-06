from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from mdi_api.agent2_errors import ResearchResourceLimitExceeded
from mdi_api.research_agent.schemas import CreateResearchTurnRequest
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.agent2 import _http_error
from tests.test_agent2_domain import foundation


def test_concurrent_research_pressure_never_exceeds_durable_project_limit() -> None:
    engine, owner, factory, _objects, _turns = foundation()
    service = ResearchTurnService(factory, max_active_turns_per_project=3)

    def submit(index: int) -> str:
        try:
            service.receive_turn(
                project_id="project",
                session_id="session",
                request=CreateResearchTurnRequest(message=f"Pressure request {index}"),
                current_user=owner,
            )
            return "accepted"
        except ResearchResourceLimitExceeded:
            return "limited"

    with ThreadPoolExecutor(max_workers=12) as pool:
        outcomes = list(pool.map(submit, range(24)))

    assert outcomes.count("accepted") == 3
    assert outcomes.count("limited") == 21
    with engine.connect() as connection:
        from sqlalchemy import func, select
        from mdi_api.db import research_turns

        assert (
            connection.execute(
                select(func.count()).select_from(research_turns)
            ).scalar_one()
            == 3
        )


def test_research_backpressure_returns_typed_retry_hint() -> None:
    response = _http_error(
        ResearchResourceLimitExceeded(
            "当前项目已有过多进行中的研究。",
            limit=4,
            active=4,
        )
    )

    assert response.status_code == 429
    assert response.headers == {"Retry-After": "5"}
    assert response.detail == {
        "code": "PROJECT_ACTIVE_RESEARCH_LIMIT",
        "summary": "当前项目已有过多进行中的研究。",
        "limit": 4,
        "active": 4,
    }
