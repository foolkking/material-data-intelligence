from __future__ import annotations

import asyncio
import os

import pytest

from mdi_api.research_agent.evaluation import AgentEvaluationRunner, load_phase2_p0_cases
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient
from mdi_api.research_agent.registry_validation import build_default_agent2_registries


def test_phase2_p0_fixtures_are_complete_strict_and_pass_contract_evaluation():
    cases = load_phase2_p0_cases()
    assert [case.case_id for case in cases] == [f"C{index:02d}" for index in range(1, 16)]
    assert all(len(case.paraphrases) >= 3 for case in cases)
    runner = AgentEvaluationRunner(build_default_agent2_registries())
    results = [runner.evaluate_fixture(case) for case in cases]
    assert all(result.passed for result in results), [result for result in results if not result.passed]


def test_phase2_fake_provider_paraphrase_contract_matrix_is_100_percent():
    cases = load_phase2_p0_cases()
    runner = AgentEvaluationRunner(build_default_agent2_registries())
    evaluated = 0
    passed = 0
    for case in cases:
        for _message in [case.message, *case.paraphrases]:
            result = runner.evaluate_fixture(case)
            evaluated += 1
            passed += int(result.passed)
    assert evaluated == 60
    assert passed == evaluated


def _live_enabled() -> bool:
    return os.getenv("MDI_RUN_AGENT2_LIVE") == "1" and bool(os.getenv("DEEPSEEK_KEY"))


@pytest.mark.live_llm
@pytest.mark.skipif(not _live_enabled(), reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification")
def test_live_deepseek_canonical_qualification():
    cases = {case.case_id: case for case in load_phase2_p0_cases()}
    runner = AgentEvaluationRunner(build_default_agent2_registries())
    client = DeepSeekStructuredLLMClient()
    case_ids = ["C01", "C02", "C03", "C05", "C07"]
    results = [asyncio.run(runner.evaluate_live(cases[case_id], client)) for case_id in case_ids]
    assert all(result.passed for result in results), [result for result in results if not result.passed]


@pytest.mark.live_llm
@pytest.mark.skipif(not _live_enabled(), reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification")
def test_live_deepseek_parameter_and_selection_sensitive_cases():
    cases = {case.case_id: case for case in load_phase2_p0_cases()}
    runner = AgentEvaluationRunner(build_default_agent2_registries())
    client = DeepSeekStructuredLLMClient()
    results = [
        asyncio.run(runner.evaluate_live(cases[case_id], client, message=message))
        for case_id in ("C04", "C06")
        for message in [cases[case_id].message, *cases[case_id].paraphrases]
    ]
    failures = [result for result in results if not result.passed]
    assert not failures, failures


@pytest.mark.live_llm
@pytest.mark.skipif(not _live_enabled(), reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification")
def test_live_deepseek_ui_selection_precedence():
    case = next(case for case in load_phase2_p0_cases() if case.case_id == "C06")
    runner = AgentEvaluationRunner(build_default_agent2_registries())
    client = DeepSeekStructuredLLMClient()
    results = [
        asyncio.run(runner.evaluate_live(case, client, message=message))
        for message in [case.message, *case.paraphrases]
    ]
    failures = [result for result in results if not result.passed]
    assert not failures, failures


@pytest.mark.live_llm
@pytest.mark.skipif(not _live_enabled(), reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification")
def test_live_deepseek_paraphrase_routing_at_least_95_percent():
    runner = AgentEvaluationRunner(build_default_agent2_registries())
    client = DeepSeekStructuredLLMClient()
    cases = [
        case for case in load_phase2_p0_cases()
        if not case.expected.rejected_before_provider
        and case.expected.validation_error_code is None
    ]
    results = [
        asyncio.run(runner.evaluate_live(case, client, message=message))
        for case in cases
        for message in [case.message, *case.paraphrases]
    ]
    passed = sum(result.passed for result in results)
    failures = [result for result in results if not result.passed]
    details = "\n".join(
        f"{result.case_id}: action={result.action}; code={result.validation_error_code}; detail={result.detail}"
        for result in failures
    )
    assert passed / len(results) >= 0.95, f"passed={passed}/{len(results)}\n{details}"
