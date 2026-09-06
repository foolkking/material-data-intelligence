from __future__ import annotations

import logging
from typing import Any

from mdi_api.observability import bounded_identifier, log_exception_event


logger = logging.getLogger("mdi.worker")


def rq_exception_correlation(job: Any) -> dict[str, str]:
    correlation: dict[str, str] = {}
    safe_job_id = bounded_identifier(getattr(job, "id", None))
    if safe_job_id is not None:
        correlation["jobId"] = safe_job_id

    function_name = str(getattr(job, "func_name", "") or "")
    arguments = tuple(getattr(job, "args", ()) or ())
    first_argument = bounded_identifier(arguments[0]) if arguments else None
    if first_argument is None:
        return correlation
    if function_name.endswith(
        (
            "run_queued_turn",
            "run_queued_planning",
            "run_queued_result_projection",
            "run_queued_interpretation",
        )
    ):
        correlation["researchTurnId"] = first_argument
    elif function_name.endswith("run_queued_report_generation"):
        correlation["reportGenerationId"] = first_argument
    elif function_name.endswith("run_queued_job"):
        correlation["jobId"] = first_argument
    return correlation


def rq_exception_handler(
    job: Any,
    _exception_type: type[BaseException],
    exception: BaseException,
    _traceback: object,
) -> bool:
    """Capture a bounded event while preserving RQ's normal failure handling."""

    log_exception_event(
        logger,
        component="worker",
        error=exception,
        correlation=rq_exception_correlation(job),
    )
    return True


__all__ = ["rq_exception_correlation", "rq_exception_handler"]
