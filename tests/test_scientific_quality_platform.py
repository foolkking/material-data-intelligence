from __future__ import annotations

from pathlib import Path

from mdi_adapters.registry import ADAPTER_CLASSES
from mdi_api.research_agent.capabilities.extension_validation import (
    validate_capability_extension_platform,
)
from mdi_api.research_agent.capabilities.quality_evidence import (
    QUALITY_EVIDENCE_BY_CAPABILITY,
    ReferenceAuthority,
    ScientificEvidenceKind,
    ScientificQualificationLevel,
    scientific_contract_fingerprint,
)
from mdi_api.research_agent.capabilities.quality_validation import (
    validate_scientific_quality,
)
from mdi_api.research_agent.registry_validation import (
    Agent2Registries,
    build_default_agent2_registries,
)
from mdi_api.scientific_viewers.registry import build_scientific_viewer_registry
from mdi_tool_registry import load_manifests, resolve_adapter_invocability


ROOT = Path(__file__).resolve().parents[1]


def _extension_report(registries: Agent2Registries):
    return validate_capability_extension_platform(
        registries,
        load_manifests(),
        viewer_registry=build_scientific_viewer_registry(),
        adapter_invocability=resolve_adapter_invocability(),
        adapter_names=ADAPTER_CLASSES,
    )


def _quality_report(
    registries: Agent2Registries | None = None,
    *,
    evidence=None,
):
    current = registries or build_default_agent2_registries()
    return validate_scientific_quality(
        _extension_report(current),
        registries=current,
        evidence_by_capability=evidence,
        repository_root=ROOT,
    )


def test_all_canonical_capabilities_have_explicit_evidence_backed_status():
    report = _quality_report()
    assert report.accepted
    assert report.error_count == 0
    assert report.capability_count == 27
    assert report.qualification_counts == {
        "DOMAIN_VALIDATED": 11,
        "EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED": 12,
        "NOT_YET_SCIENTIFICALLY_QUALIFIED": 1,
        "REFERENCE_VALIDATED": 3,
    }
    assert report.reference_case_count == 13
    assert report.invariant_case_count == 11
    assert report.domain_negative_case_count == 22
    assert report.artifact_semantics_case_count == 2
    assert report.result_projection_case_count == 4
    assert report.interpretation_evaluation_case_count == 7
    assert report.report_evaluation_case_count == 2
    assert len(report.inventory_fingerprint) == 64
    assert all(item.status == "VALID" for item in report.capabilities)


def test_quality_evidence_is_bound_to_current_scientific_contract():
    registries = build_default_agent2_registries()
    for manifest in registries.capabilities.list_all():
        evidence = QUALITY_EVIDENCE_BY_CAPABILITY[manifest.capability_id]
        assert evidence.qualified_contract_fingerprint == scientific_contract_fingerprint(
            manifest
        )
        assert manifest.qualification.evidence_fingerprint == evidence.evidence_fingerprint


def test_scientific_contract_change_makes_qualification_stale():
    source = build_default_agent2_registries()
    changed_capabilities = type(source.capabilities)()
    for manifest in source.capabilities.list_all():
        changed_capabilities.register(
            manifest.model_copy(
                update={
                    "scientific_purpose": manifest.scientific_purpose
                    + " Changed scientific meaning."
                }
            )
            if manifest.capability_id == "structure.rdf"
            else manifest
        )
    changed = Agent2Registries(
        object_types=source.object_types,
        requirements=source.requirements,
        capabilities=changed_capabilities,
        result_projectors=source.result_projectors,
        progress_projectors=source.progress_projectors,
        extension_registry=source.extension_registry,
    )
    report = _quality_report(changed)
    assert not report.accepted
    assert any(
        issue.code == "STALE_QUALIFICATION"
        and issue.capability_id == "structure.rdf"
        for issue in report.issues
    )


def test_regression_only_reference_cannot_promote_scientific_quality():
    records = dict(QUALITY_EVIDENCE_BY_CAPABILITY)
    source = records["structure.rdf"]
    links = [
        link.model_copy(update={"reference_authority": ReferenceAuthority.REGRESSION_ONLY})
        if link.kind == ScientificEvidenceKind.REFERENCE
        else link
        for link in source.evidence
    ]
    records["structure.rdf"] = source.model_copy(update={"evidence": links})
    report = _quality_report(evidence=records)
    assert not report.accepted
    codes = {
        issue.code
        for issue in report.issues
        if issue.capability_id == "structure.rdf"
    }
    assert "QUALIFICATION_WITHOUT_REFERENCE" in codes
    assert "REGRESSION_ONLY_PROMOTION" in codes


def test_domain_validation_requires_reference_invariant_and_negative_evidence():
    records = dict(QUALITY_EVIDENCE_BY_CAPABILITY)
    source = records["trajectory.msd"]
    records["trajectory.msd"] = source.model_copy(
        update={
            "evidence": [
                link
                for link in source.evidence
                if link.kind != ScientificEvidenceKind.INVARIANT
            ]
        }
    )
    report = _quality_report(evidence=records)
    assert not report.accepted
    assert any(
        issue.code == "DOMAIN_QUALIFICATION_INCOMPLETE"
        and issue.capability_id == "trajectory.msd"
        for issue in report.issues
    )


def test_external_solver_semantics_are_not_mislabeled_as_independent_validation():
    external = {
        item.capability_id: item
        for item in QUALITY_EVIDENCE_BY_CAPABILITY.values()
        if item.qualification_level
        == ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED
    }
    assert len(external) == 12
    for item in external.values():
        authorities = {link.reference_authority for link in item.evidence}
        assert authorities & {
            ReferenceAuthority.OFFICIAL_LIBRARY_SEMANTICS,
            ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
        }
        assert item.qualification_level != ScientificQualificationLevel.DOMAIN_VALIDATED


def test_numeric_evidence_has_units_tolerance_origin_and_method():
    numeric = [
        link
        for item in QUALITY_EVIDENCE_BY_CAPABILITY.values()
        for link in item.evidence
        if link.numeric
    ]
    assert numeric
    assert all(link.units for link in numeric)
    assert all(link.tolerance is not None for link in numeric)
    assert all(link.reference_origin and link.reference_method for link in numeric)
    assert len({link.tolerance.rationale for link in numeric if link.tolerance}) > 5


def test_every_evidence_node_resolves_to_a_real_focused_test():
    report = _quality_report()
    assert not [
        issue
        for issue in report.issues
        if issue.code == "INVALID_EVIDENCE_TEST_NODE"
    ]


def test_quality_inventory_preserves_applicability_limitations_and_reproducibility():
    report = _quality_report()
    by_id = {item.capability_id: item for item in report.capabilities}
    assert "periodic" in " ".join(by_id["structure.rdf"].applicability_domains)
    assert by_id["ml.regression_evaluation"].reproducibility == "SEEDED_STOCHASTIC"
    assert any(
        "upstream electronic solver" in limitation
        for limitation in by_id["electronic.band_structure"].known_limitations
    )
    assert any(
        "phase identity" in limitation
        for limitation in by_id[
            "diffraction.experimental_theoretical_comparison"
        ].known_limitations
    )
