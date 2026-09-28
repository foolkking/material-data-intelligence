"""Evidence-backed scientific qualification for canonical Capabilities.

The records in this module do not execute scientific code and are not another
Capability registry.  They link each canonical Capability to focused,
repository-owned evidence and to the scientific contract that evidence
actually qualified.  The separate contract fingerprint intentionally excludes
the qualification summary itself, avoiding a self-referential hash.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from mdi_api.research_agent.schemas import CapabilityManifest, CapabilityQualification


QUALITY_EVIDENCE_VERSION = "1.0"


class ScientificQualificationLevel(StrEnum):
    STRUCTURAL_ONLY = "STRUCTURAL_ONLY"
    REFERENCE_VALIDATED = "REFERENCE_VALIDATED"
    DOMAIN_VALIDATED = "DOMAIN_VALIDATED"
    CROSS_IMPLEMENTATION_VALIDATED = "CROSS_IMPLEMENTATION_VALIDATED"
    EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED = (
        "EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED"
    )
    NOT_YET_SCIENTIFICALLY_QUALIFIED = "NOT_YET_SCIENTIFICALLY_QUALIFIED"


class ScientificEvidenceKind(StrEnum):
    REFERENCE = "REFERENCE"
    INVARIANT = "INVARIANT"
    DOMAIN_NEGATIVE = "DOMAIN_NEGATIVE"
    ADAPTER_SEMANTICS = "ADAPTER_SEMANTICS"
    ARTIFACT_SEMANTICS = "ARTIFACT_SEMANTICS"
    RESULT_PROJECTION = "RESULT_PROJECTION"
    INTERPRETATION = "INTERPRETATION"
    REPORT = "REPORT"
    INTEGRATION = "INTEGRATION"
    REGRESSION = "REGRESSION"


class ReferenceAuthority(StrEnum):
    ANALYTICAL = "ANALYTICAL"
    INDEPENDENT_IMPLEMENTATION = "INDEPENDENT_IMPLEMENTATION"
    PUBLISHED_REFERENCE = "PUBLISHED_REFERENCE"
    CURATED_KNOWN_RESULT = "CURATED_KNOWN_RESULT"
    SYNTHETIC_EXACT = "SYNTHETIC_EXACT"
    OFFICIAL_LIBRARY_SEMANTICS = "OFFICIAL_LIBRARY_SEMANTICS"
    EXTERNAL_SOLVER_SEMANTICS = "EXTERNAL_SOLVER_SEMANTICS"
    REGRESSION_ONLY = "REGRESSION_ONLY"


class ScientificTolerance(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    absolute: float | None = Field(default=None, ge=0)
    relative: float | None = Field(default=None, ge=0)
    unit: str = Field(min_length=1, max_length=48)
    rationale: str = Field(min_length=8, max_length=512)
    domain_rule: str | None = Field(default=None, min_length=3, max_length=512)

    @model_validator(mode="after")
    def has_numeric_or_domain_bound(self) -> "ScientificTolerance":
        if (
            self.absolute is None
            and self.relative is None
            and self.domain_rule is None
        ):
            raise ValueError("tolerance requires an absolute, relative, or domain bound")
        return self


class ScientificEvidenceLink(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_.-]{2,127}$")
    kind: ScientificEvidenceKind
    reference_authority: ReferenceAuthority
    test_node: str = Field(min_length=8, max_length=512)
    reference_origin: str = Field(min_length=8, max_length=1024)
    reference_method: str = Field(min_length=3, max_length=512)
    reference_version: str = Field(min_length=1, max_length=128)
    expected_semantics: list[str] = Field(min_length=1, max_length=16)
    units: list[str] = Field(default_factory=list, max_length=16)
    conventions: list[str] = Field(default_factory=list, max_length=16)
    tolerance: ScientificTolerance | None = None
    numeric: bool = False
    applicability: list[str] = Field(default_factory=list, max_length=16)
    limitations: list[str] = Field(default_factory=list, max_length=16)
    case_count: int = Field(default=1, ge=1, le=128)
    notes: str | None = Field(default=None, max_length=1024)

    @model_validator(mode="after")
    def numeric_evidence_has_tolerance(self) -> "ScientificEvidenceLink":
        if self.numeric and self.tolerance is None:
            raise ValueError("numeric scientific evidence requires an explicit tolerance")
        return self


class CapabilityQualityEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    capability_version: str = "1.0"
    qualification_level: ScientificQualificationLevel
    qualified_contract_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    applicability_domains: list[str] = Field(min_length=1, max_length=16)
    known_limitations: list[str] = Field(default_factory=list, max_length=32)
    reproducibility: Literal[
        "DETERMINISTIC",
        "SEEDED_STOCHASTIC",
        "NONDETERMINISTIC_EXTERNAL",
        "UNKNOWN",
    ]
    evidence: list[ScientificEvidenceLink] = Field(min_length=1, max_length=32)

    @computed_field
    @property
    def evidence_counts(self) -> dict[str, int]:
        counts = Counter(item.kind.value for item in self.evidence)
        return {key: counts[key] for key in sorted(counts)}

    @computed_field
    @property
    def evidence_fingerprint(self) -> str:
        return _digest(
            self.model_dump(
                mode="json",
                exclude={"evidence_fingerprint"},
            )
        )


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def scientific_contract_fingerprint(manifest: CapabilityManifest) -> str:
    """Fingerprint the qualified scientific contract, excluding evidence state."""

    return _digest(
        manifest.model_dump(
            mode="json",
            exclude={
                "qualification",
            },
        )
    )


def _tolerance(
    unit: str,
    rationale: str,
    *,
    absolute: float | None = None,
    relative: float | None = None,
    domain_rule: str | None = None,
) -> ScientificTolerance:
    return ScientificTolerance(
        absolute=absolute,
        relative=relative,
        unit=unit,
        rationale=rationale,
        domain_rule=domain_rule,
    )


def _link(
    evidence_id: str,
    kind: ScientificEvidenceKind,
    authority: ReferenceAuthority,
    test_node: str,
    origin: str,
    method: str,
    semantics: list[str],
    *,
    version: str = "repository-current",
    units: list[str] | None = None,
    conventions: list[str] | None = None,
    tolerance: ScientificTolerance | None = None,
    numeric: bool = False,
    applicability: list[str] | None = None,
    limitations: list[str] | None = None,
    case_count: int = 1,
    notes: str | None = None,
) -> ScientificEvidenceLink:
    return ScientificEvidenceLink(
        evidence_id=evidence_id,
        kind=kind,
        reference_authority=authority,
        test_node=test_node,
        reference_origin=origin,
        reference_method=method,
        reference_version=version,
        expected_semantics=semantics,
        units=units or [],
        conventions=conventions or [],
        tolerance=tolerance,
        numeric=numeric,
        applicability=applicability or [],
        limitations=limitations or [],
        case_count=case_count,
        notes=notes,
    )


_RESULT_PROJECTION = _link(
    "shared.result-projection.v1",
    ScientificEvidenceKind.RESULT_PROJECTION,
    ReferenceAuthority.CURATED_KNOWN_RESULT,
    "tests/test_agent2_results.py::test_canonical_projector_uses_verified_production_contract_and_grounded_facts",
    "Canonical Phase 5 ScientificResult projector fixtures.",
    "Artifact-to-ScientificResult semantic projection",
    ["facts, evidence, methods, limitations, and exact source refs remain bounded"],
)
_INTERPRETATION = _link(
    "shared.interpretation-grounding.v1",
    ScientificEvidenceKind.INTERPRETATION,
    ReferenceAuthority.CURATED_KNOWN_RESULT,
    "tests/test_grounded_interpretation.py::test_five_real_contract_families_project_and_interpret_deterministically",
    "Canonical deterministic multi-family interpretation fixtures.",
    "ScientificResult-grounded interpretation contract",
    ["numeric and source claims remain within projected Result authority"],
    case_count=5,
)
_INTERPRETATION_LIMITS = _link(
    "shared.interpretation-partial-limit.v1",
    ScientificEvidenceKind.INTERPRETATION,
    ReferenceAuthority.CURATED_KNOWN_RESULT,
    "tests/test_grounded_interpretation.py::test_partial_result_is_ready_with_limits_and_never_claims_failed_artifact",
    "Canonical partial ScientificResult interpretation fixture.",
    "Partial-result epistemic restraint",
    ["partial and failed outputs remain explicit limitations rather than complete claims"],
)
_INTERPRETATION_REJECTION = _link(
    "shared.interpretation-unsupported-claim.v1",
    ScientificEvidenceKind.INTERPRETATION,
    ReferenceAuthority.CURATED_KNOWN_RESULT,
    "tests/test_grounded_interpretation.py::test_strict_provider_rejects_forbidden_qualifier_after_one_repair",
    "Canonical provider-output grounding rejection fixture.",
    "Unsupported scientific qualifier rejection",
    ["unsupported stability/superiority qualifiers fail after one bounded repair"],
)
_REPORT = _link(
    "shared.report-grounding.v1",
    ScientificEvidenceKind.REPORT,
    ReferenceAuthority.CURATED_KNOWN_RESULT,
    "tests/test_agent_quality_evaluation.py::test_phase14r_report_quality_evaluator_passes_grounded_complete_report",
    "Canonical grounded report composition fixtures.",
    "Result/Interpretation-to-Report source fidelity contract",
    ["report facts, units, evidence, methods, and limitations retain source bindings"],
)
_REPORT_NEGATIVE = _link(
    "shared.report-quality-negative.v1",
    ScientificEvidenceKind.REPORT,
    ReferenceAuthority.CURATED_KNOWN_RESULT,
    "tests/test_agent_quality_evaluation.py::test_phase14r_report_quality_evaluator_fails_missing_authority_and_limits",
    "Canonical Report fixture with missing source authority and limitations.",
    "Report fail-closed quality rubric",
    ["missing sources, evidence, limitations, or grounding prevents quality qualification"],
)
_ARTIFACT = _link(
    "shared.artifact-semantics.v1",
    ScientificEvidenceKind.ARTIFACT_SEMANTICS,
    ReferenceAuthority.CURATED_KNOWN_RESULT,
    "tests/test_agent2_results.py::test_canonical_projector_uses_verified_production_contract_and_grounded_facts",
    "Canonical typed Artifact fixtures consumed by all registered Result projectors.",
    "Artifact schema and semantic-field preservation",
    ["typed payload, schema version, source identity, units, and method metadata remain projector-readable"],
)


def _evidence(
    capability_id: str,
    level: ScientificQualificationLevel,
    contract_fingerprint: str,
    applicability: list[str],
    limitations: list[str],
    reproducibility: Literal[
        "DETERMINISTIC",
        "SEEDED_STOCHASTIC",
        "NONDETERMINISTIC_EXTERNAL",
        "UNKNOWN",
    ],
    links: list[ScientificEvidenceLink],
) -> CapabilityQualityEvidence:
    return CapabilityQualityEvidence(
        capability_id=capability_id,
        qualification_level=level,
        qualified_contract_fingerprint=contract_fingerprint,
        applicability_domains=applicability,
        known_limitations=limitations,
        reproducibility=reproducibility,
        evidence=[
            *links,
            _ARTIFACT,
            _RESULT_PROJECTION,
            _INTERPRETATION,
            _INTERPRETATION_LIMITS,
            _INTERPRETATION_REJECTION,
            _REPORT,
            _REPORT_NEGATIVE,
        ],
    )


# These fingerprints are intentionally frozen to the qualified scientific
# contracts.  The quality validator reports STALE_QUALIFICATION when a
# Capability's scientific contract changes without corresponding evidence
# review.  They bind evidence to scientific semantics while excluding Tool,
# Viewer and projector implementation bindings, which have their own registry
# validation and provenance.
_QUALIFIED_CONTRACT_FINGERPRINTS = {
    "data.composition_analysis": "17de88fff16f32573f57933070be4521a23f51645d1e485436b0357cd0ff89e7",
    "data.composition_space": "d45f072b0b92bad31107b21d8ff59d678126132398db8b612a566331f6677853",
    "data.materials_explorer": "c09a528193fc16ff07c1cba3fcc0d794398954f25f33a51939d91fb6a19af2d6",
    "data.table_analysis": "2651390865f7e16854c1fd1466817625282dd375546f041d98d475687c35188a",
    "diffraction.experimental_theoretical_comparison": "bf6ed324c7d9fd5af7dd1849bedd20bd286337269d03ae56b4b161c085661447",
    "diffraction.theoretical_xrd": "6e20914cfa9174cf1e50fa92e635431a5e59ee44f13fb4d8f483c9a6dea3647f",
    "electronic.band_structure": "29ac10aa8d76d36f3756ca77d2a43dd42aa385b9088c7b2dd5eeab01009f4425",
    "electronic.dos": "ac2f4e905235fd90031e1cada92fa7cec8397ffe3e3bfc9281f6b9561eb25956",
    "ml.regression_evaluation": "79a3113f065aac6e9da6f8cc9e86dbfa35358ea20e193fa245957cd80e426864",
    "ml.uncertainty_evaluation": "60faffa1fee3fc7b3b50d97787c8a899a312873798b0d83727ca3c00fcd31aab",
    "ml.classification_evaluation": "f7533e16f895e6e59e91565af0a5aa4fdeef241d4f9456fd1c7d2130b2028bce",
    "phonon.band": "6a738cde1f40a6a4988117cee8b09723a61e5c71e7dd37091523889474670cf4",
    "phonon.band_dos": "8df6523520f2ca12a180dd8814d7498184addab98810abd1eeac939eb38708c1",
    "phonon.dos": "3752ed3bd332f3baa1fdfacfd3cb87df28181b4beb5224d5183ff9d0b72ff259",
    "structure.coordination_crystalnn": "e9dcae845348ead7327eecb5d62db752dce98475b52a1e3f5c0e715dc62b961c",
    "structure.coordination_analysis": "7ff2ab685817d774e05c3be652332ea276987338ba1634f5d8151b560cd859ed",
    "structure.coordination_hist": "b86d5a9d829f235a3f2da9e80c22a705bc9ff6f9d8a9fffeb6f6ed1340fb0a6d",
    "structure.coordination_voronoinn": "d770462bd141183bee69e949d35890070c95dc6936e13746623edccddc898b7f",
    "structure.rdf": "e668b60e6091810da7971ac0a344fbf3ab460455a476f09e4e251d45cebd94b3",
    "structure.brillouin_zone": "22b82f9f47d5acc5e692699fda0c1ab870171f93655c6a847f1d570e166fff0d",
    "structure.summary": "5f9078398f9a9033f1292df62e8f6b35ef72e0ecbe9868856468a0ab338e3739",
    "structure.viewer_scene": "1b5b35e74b990ad417bf8746b3aa3f502611adc05a69e360528a3d3f39f7e8c4",
    "trajectory.diffusion": "e23a262dc9ec5095d7c12e50a5077653774dbc893101b1016a10ae38706ac367",
    "trajectory.msd": "a8bbab194f7e669e3890a19df01b49467a070591a1df57d3efa14d20e11dfbbc",
    "trajectory.rdf": "4a3a573ce47813348b54c1f9d690492c01891665b8f5100a7015b705b30d5903",
    "trajectory.viewer_scene": "9bcbbf265f188c24e4d22f6b6ef77fde8e45eb0ec86eed16b2f5247b45af081e",
    "volumetric.data": "eb4ba242f1473625c2a3081751060b26bfed9070253e4f21314b829689bea45e",
}


def _qualified_fingerprint(capability_id: str) -> str:
    expected = _QUALIFIED_CONTRACT_FINGERPRINTS[capability_id]
    if expected == "0" * 64:
        raise ValueError(f"pending scientific contract fingerprint: {capability_id}")
    return expected


def _records() -> list[CapabilityQualityEvidence]:
    result_projection_rdf = _link(
        "structure.rdf.result.v1",
        ScientificEvidenceKind.RESULT_PROJECTION,
        ReferenceAuthority.CURATED_KNOWN_RESULT,
        "tests/test_agent2_results.py::test_rdf_projects_authoritative_range_and_bin_width_with_units",
        "Canonical RDF Artifact and ScientificResult fixtures.",
        "RDF semantic projection",
        ["range and bin width retain angstrom units; curve remains a series"],
        units=["angstrom"],
    )
    return [
        _evidence(
            "volumetric.data",
            ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED,
            _qualified_fingerprint("volumetric.data"),
            ["bounded parser-validated VASP volumetric or single-dataset Gaussian CUBE fields"],
            [
                "The Tool parses and normalizes supplied volumetric data; it does not run an external solver.",
                "Renderer, arbitrary slicing, and direct-volume computation remain application-owned presentation concerns.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "volumetric.contract.v1",
                    ScientificEvidenceKind.ARTIFACT_SEMANTICS,
                    ReferenceAuthority.CURATED_KNOWN_RESULT,
                    "tests/test_volumetric_contract.py::test_schema_family_and_security_snapshot_are_exact",
                    "Canonical Phase 10J volumetric contract fixtures.",
                    "Volumetric grid, payload, field, dataset, and manifest validation",
                    ["typed volumetric artifacts preserve bounded source identity, schema versions, checksums, and security policy"],
                ),
                _link(
                    "volumetric.adapter.v1",
                    ScientificEvidenceKind.ADAPTER_SEMANTICS,
                    ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
                    "tests/test_elf_orbital_product.py::test_runtime_artifact_semantics_are_source_native_and_canonical",
                    "Repository-owned VASP/CUBE parser and adapter fixtures.",
                    "Bounded source parsing and canonical artifact export",
                    ["supported volumetric sources produce validated canonical field and dataset artifacts"],
                ),
                _link(
                    "volumetric.integration.v1",
                    ScientificEvidenceKind.INTEGRATION,
                    ReferenceAuthority.CURATED_KNOWN_RESULT,
                    "tests/integration/test_product_closure_service_backed.py::test_phase10j1_service_backed_volumetric_parser_adapter_closure",
                    "Service-backed volumetric parser/tool integration fixture.",
                    "Registered Tool execution and artifact publication",
                    ["the registered volumetric Tool executes with the typed source and publishes bounded artifacts"],
                ),
            ],
        ),
        _evidence(
            "structure.rdf",
            ScientificQualificationLevel.REFERENCE_VALIDATED,
            _qualified_fingerprint("structure.rdf"),
            ["periodic crystal structures with a valid lattice"],
            [
                "Finite-cell histogram and normalization conventions remain method-specific.",
                "Non-periodic structures are rejected.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "structure.rdf.synthetic.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_rdf.py::test_rdf_generates_numeric_json_plot_summary_and_recipe",
                    "Small repository-owned crystal with directly inspectable pair distances.",
                    "Bounded periodic pair-distance histogram",
                    ["numeric RDF bins and pair series are produced from exact structure input"],
                    units=["angstrom", "dimensionless"],
                    tolerance=_tolerance(
                        "angstrom",
                        "Pair-distance bin placement follows the declared bin width.",
                        absolute=1e-8,
                    ),
                    numeric=True,
                ),
                _link(
                    "structure.rdf.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_rdf.py::test_rdf_rejects_non_periodic_and_resource_limit_excesses",
                    "Synthetic non-periodic and oversized structure fixtures.",
                    "Declared applicability boundary",
                    ["non-periodic and resource-limit inputs fail explicitly"],
                ),
                result_projection_rdf,
            ],
        ),
        _evidence(
            "structure.coordination_hist",
            ScientificQualificationLevel.REFERENCE_VALIDATED,
            _qualified_fingerprint("structure.coordination_hist"),
            ["ordered periodic crystal structures under a declared cutoff"],
            [
                "Coordination depends on the selected cutoff.",
                "Disordered structures are rejected rather than coerced.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "structure.coordination-hist.reference.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_coordination.py::test_algorithm_produces_inert_algorithm_specific_artifact",
                    "Repository-owned ordered crystal with explicit neighbor semantics.",
                    "Distance-cutoff coordination counting",
                    ["algorithm-specific coordination output preserves bounded neighbor facts"],
                    units=["count", "angstrom"],
                    tolerance=_tolerance(
                        "count",
                        "Coordination counts and site identities are discrete exact values.",
                        absolute=0,
                    ),
                    numeric=True,
                ),
                _link(
                    "structure.coordination-hist.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_coordination.py::test_periodic_image_and_checksum_order_are_deterministic",
                    "Equivalent periodic image ordering fixture.",
                    "Deterministic coordination ordering",
                    ["periodic image and output ordering do not change the scientific result"],
                ),
                _link(
                    "structure.coordination-hist.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_coordination.py::test_disorder_is_typed_and_never_coerced",
                    "Synthetic disordered structure fixture.",
                    "Ordered-structure applicability boundary",
                    ["disorder is rejected with a typed failure"],
                ),
            ],
        ),
        _evidence(
            "structure.coordination_crystalnn",
            ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED,
            _qualified_fingerprint("structure.coordination_crystalnn"),
            ["ordered periodic structures supported by pymatgen CrystalNN"],
            [
                "Scientific neighbor assignment is delegated to pymatgen CrystalNN.",
                "This evidence validates platform semantics, not CrystalNN independently.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "structure.crystalnn.external.v1",
                    ScientificEvidenceKind.ADAPTER_SEMANTICS,
                    ReferenceAuthority.OFFICIAL_LIBRARY_SEMANTICS,
                    "tests/test_coordination.py::test_algorithm_produces_inert_algorithm_specific_artifact",
                    "pymatgen CrystalNN output exercised through the canonical Adapter.",
                    "Official-library semantic mapping",
                    ["algorithm identity, neighbor facts, units, and artifact schema are preserved"],
                    units=["count", "angstrom"],
                    version="locked pymatgen dependency",
                ),
                _link(
                    "structure.crystalnn.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_coordination.py::test_disorder_is_typed_and_never_coerced",
                    "Repository-owned disordered structure fixture.",
                    "Adapter applicability boundary",
                    ["unsupported disorder fails explicitly"],
                ),
            ],
        ),
        _evidence(
            "structure.coordination_voronoinn",
            ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED,
            _qualified_fingerprint("structure.coordination_voronoinn"),
            ["ordered periodic structures supported by pymatgen VoronoiNN"],
            [
                "Scientific neighbor assignment is delegated to pymatgen VoronoiNN.",
                "This evidence validates platform semantics, not VoronoiNN independently.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "structure.voronoinn.external.v1",
                    ScientificEvidenceKind.ADAPTER_SEMANTICS,
                    ReferenceAuthority.OFFICIAL_LIBRARY_SEMANTICS,
                    "tests/test_coordination.py::test_algorithm_produces_inert_algorithm_specific_artifact",
                    "pymatgen VoronoiNN output exercised through the canonical Adapter.",
                    "Official-library semantic mapping",
                    ["algorithm identity, neighbor facts, units, and artifact schema are preserved"],
                    units=["count", "angstrom"],
                    version="locked pymatgen dependency",
                ),
                _link(
                    "structure.voronoinn.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_coordination.py::test_algorithm_parameters_are_strict_and_bounded",
                    "Repository-owned invalid parameter fixtures.",
                    "Bounded Adapter parameter contract",
                    ["unknown and out-of-domain parameters fail explicitly"],
                ),
            ],
        ),
        _evidence(
            "diffraction.theoretical_xrd",
            ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED,
            _qualified_fingerprint("diffraction.theoretical_xrd"),
            ["periodic crystal structures accepted by pymatgen XRDCalculator"],
            [
                "Peak intensities follow pymatgen broadening and normalization conventions.",
                "The platform does not independently validate the diffraction solver.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "xrd.theoretical.external.v1",
                    ScientificEvidenceKind.ADAPTER_SEMANTICS,
                    ReferenceAuthority.OFFICIAL_LIBRARY_SEMANTICS,
                    "tests/test_xrd.py::test_xrd_generates_numeric_json_plot_summary_and_recipe",
                    "pymatgen XRDCalculator output exercised through the canonical Adapter.",
                    "Powder XRD platform mapping",
                    ["2theta positions, relative intensities, HKL metadata, and Cu K-alpha convention are preserved"],
                    units=["degree", "relative_intensity"],
                    tolerance=_tolerance(
                        "degree",
                        "Peak comparison uses the sealed Phase 11 0.15 degree 2theta policy.",
                        absolute=0.15,
                    ),
                    numeric=True,
                    version="locked pymatgen dependency",
                ),
                _link(
                    "xrd.theoretical.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_xrd.py::test_xrd_rejects_invalid_params_and_malformed_input",
                    "Malformed structures and invalid wavelength/range fixtures.",
                    "XRD applicability and parameter boundary",
                    ["invalid scientific inputs fail before artifact production"],
                ),
            ],
        ),
        _evidence(
            "diffraction.experimental_theoretical_comparison",
            ScientificQualificationLevel.REFERENCE_VALIDATED,
            _qualified_fingerprint("diffraction.experimental_theoretical_comparison"),
            ["monotonic experimental and theoretical XRD peak resources with compatible wavelength"],
            [
                "Peak matching is bounded by the declared 2theta tolerance.",
                "A match does not establish phase identity.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "xrd.comparison.analytic.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_experimental_xrd.py::test_match_preserves_both_unmatched_sets_and_residuals",
                    "Hand-checkable experimental/theoretical peak tables.",
                    "Nearest compatible peak matching",
                    ["matched residuals and both unmatched sets equal the analytical fixture"],
                    units=["degree"],
                    tolerance=_tolerance(
                        "degree",
                        "Peak identity is accepted only within the declared matching window.",
                        absolute=0.15,
                    ),
                    numeric=True,
                ),
                _link(
                    "xrd.comparison.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_experimental_xrd.py::test_zero_match_is_valid_and_deterministic",
                    "Disjoint hand-checkable peak sets.",
                    "Deterministic empty matching",
                    ["zero matches remain a valid deterministic scientific outcome"],
                ),
                _link(
                    "xrd.comparison.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_experimental_xrd.py::test_wavelength_mismatch_and_nonmonotonic_resource_are_rejected",
                    "Synthetic wavelength-mismatch and nonmonotonic fixtures.",
                    "Comparison applicability boundary",
                    ["incompatible wavelength and ordering fail explicitly"],
                ),
            ],
        ),
        _evidence(
            "trajectory.rdf",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("trajectory.rdf"),
            ["periodic atomic trajectories with valid cells and species"],
            [
                "Finite-size normalization and binning remain explicit method conventions.",
                "Ambiguous periodic geometry is rejected.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "trajectory.rdf.reference.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.INDEPENDENT_IMPLEMENTATION,
                    "tests/test_trajectory_analytics.py::test_rdf_batch_pair_distances_match_scalar_minimum_image",
                    "ASE scalar minimum-image distances used independently of the batch path.",
                    "Batch-vs-scalar periodic minimum-image comparison",
                    ["pair distances agree under periodic geometry"],
                    units=["angstrom"],
                    tolerance=_tolerance(
                        "angstrom",
                        "Batch and scalar ASE minimum-image distances share floating-point geometry.",
                        absolute=1e-10,
                        relative=1e-10,
                    ),
                    numeric=True,
                    version="locked ASE dependency",
                ),
                _link(
                    "trajectory.rdf.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_trajectory_analytics.py::test_triclinic_rdf_uses_ase_geometric_minimum_image",
                    "Synthetic triclinic periodic trajectory.",
                    "Periodic representation invariance",
                    ["triclinic minimum-image geometry is preserved"],
                ),
                _link(
                    "trajectory.rdf.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_trajectory_analytics.py::test_msd_triclinic_partial_pbc_and_ambiguous_steps",
                    "Synthetic ambiguous and partial-PBC trajectory fixtures.",
                    "Trajectory geometry applicability boundary",
                    ["ambiguous unwrap semantics fail explicitly"],
                ),
            ],
        ),
        _evidence(
            "trajectory.msd",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("trajectory.msd"),
            ["atomic trajectories with explicit timestep and unambiguous periodic unwrap"],
            [
                "MSD semantics depend on the declared origin/reference policy.",
                "Ambiguous image steps are rejected rather than guessed.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "trajectory.msd.analytic.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_trajectory_analytics.py::test_boundary_crossing_msd_uses_unwrapped_positions",
                    "Synthetic one-particle boundary-crossing trajectory with hand-computed MSD.",
                    "Unwrapped displacement squared",
                    ["MSD equals 0.0625, 0.25, and 0.5625 angstrom squared"],
                    units=["angstrom^2", "ps"],
                    tolerance=_tolerance(
                        "angstrom^2",
                        "Synthetic displacement is analytically exact; tolerance covers floating point.",
                        absolute=1e-12,
                        relative=1e-10,
                    ),
                    numeric=True,
                ),
                _link(
                    "trajectory.msd.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_trajectory_contract.py::test_wrapped_and_unwrapped_coordinates_preserve_semantics",
                    "Equivalent wrapped and unwrapped trajectory representations.",
                    "Periodic representation invariance",
                    ["equivalent coordinate representations produce the same MSD"],
                ),
                _link(
                    "trajectory.msd.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_trajectory_analytics.py::test_msd_triclinic_partial_pbc_and_ambiguous_steps",
                    "Synthetic ambiguous image-step trajectory.",
                    "Unwrap applicability boundary",
                    ["ambiguous periodic motion fails explicitly"],
                ),
            ],
        ),
        _evidence(
            "trajectory.diffusion",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("trajectory.diffusion"),
            ["linear diffusive MSD windows with explicit timestep and fit range"],
            [
                "Ballistic/non-diffusive windows are rejected.",
                "Reported diffusion is conditional on the selected fit regime.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "trajectory.diffusion.analytic.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_trajectory_analytics.py::test_diffusion_accepts_linear_msd_and_rejects_ballistic",
                    "Synthetic linear and ballistic MSD curves with hand-computable regimes.",
                    "Einstein-relation linear fit",
                    ["linear MSD gives diffusion coefficient 0.1 and ballistic input is rejected"],
                    units=["angstrom^2/ps", "dimensionless"],
                    tolerance=_tolerance(
                        "angstrom^2/ps",
                        "Analytical linear fixture; tolerance covers least-squares floating point.",
                        absolute=1e-12,
                        relative=1e-10,
                        domain_rule="R2 >= 0.9 and 0.8 <= alpha <= 1.2",
                    ),
                    numeric=True,
                ),
                _link(
                    "trajectory.diffusion.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.CURATED_KNOWN_RESULT,
                    "tests/test_trajectory_analytics.py::test_real_unwrapped_extxyz_closes_msd_to_diffusion_dependency",
                    "Curated unwrapped extxyz trajectory with independently recorded expected fit.",
                    "MSD-to-diffusion dependency replay",
                    ["fit window and diffusion remain stable across the typed Artifact boundary"],
                    units=["angstrom^2/ps"],
                    tolerance=_tolerance(
                        "angstrom^2/ps",
                        "Curated reference value 0.038618 is compared at fixture precision.",
                        absolute=1e-6,
                        relative=1e-5,
                    ),
                    numeric=True,
                ),
                _link(
                    "trajectory.diffusion.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_trajectory_analytics.py::test_diffusion_requires_explicit_window_and_persisted_checksum",
                    "Missing-window and lineage-mismatch fixtures.",
                    "Fit-window and provenance boundary",
                    ["implicit fit ranges and unbound MSD artifacts are rejected"],
                ),
            ],
        ),
        _evidence(
            "data.materials_explorer",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("data.materials_explorer"),
            ["authorized profiled tabular materials datasets"],
            [
                "This capability summarizes/query-projects data; it does not infer scientific causality.",
                "Mixed units are rejected.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "data.explorer.reference.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_dataset_materials_explorer.py::test_materials_explorer_builds_coherent_profile_bound_product",
                    "Small hand-checkable tabular dataset.",
                    "Descriptive statistics and bounded sample projection",
                    ["counts, ranges, and profile-bound values agree with the fixture"],
                    units=["dimensionless"],
                    tolerance=_tolerance(
                        "dimensionless",
                        "Hand-computable fixture statistics use floating-point comparison.",
                        absolute=1e-12,
                        relative=1e-10,
                    ),
                    numeric=True,
                ),
                _link(
                    "data.explorer.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_dataset_materials_explorer.py::test_group_comparison_is_explicit_and_never_uses_row_order",
                    "Equivalent tabular rows in different order.",
                    "Row-order invariance",
                    ["aggregate group comparison does not depend on row order"],
                ),
                _link(
                    "data.explorer.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_dataset_materials_explorer.py::test_invalid_comparison_bindings_and_mixed_units_are_typed",
                    "Synthetic foreign binding and mixed-unit datasets.",
                    "Dataset applicability boundary",
                    ["invalid bindings and mixed units fail explicitly"],
                ),
            ],
        ),
        _evidence(
            "data.composition_space",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("data.composition_space"),
            ["profiled materials datasets with parseable formulas"],
            [
                "PCA is center-only under the declared convention.",
                "K-means remains an exploratory clustering projection, not scientific class truth.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "data.composition.reference.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_composition_space.py::test_profile_bound_atomic_number_basis_and_normalized_fractions",
                    "Small formula set with hand-computable atomic fractions.",
                    "Formula parsing and normalized composition basis",
                    ["atomic fractions sum to one and retain material identity"],
                    units=["fraction"],
                    tolerance=_tolerance(
                        "fraction",
                        "Normalized atomic fractions are analytically determined.",
                        absolute=1e-12,
                        relative=1e-10,
                    ),
                    numeric=True,
                ),
                _link(
                    "data.composition.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_composition_space.py::test_center_only_pca_sign_explained_variance_and_replay_are_deterministic",
                    "Small deterministic composition matrix.",
                    "PCA sign and replay convention",
                    ["center-only PCA and explained variance follow the declared convention"],
                    units=["fraction", "dimensionless"],
                    tolerance=_tolerance(
                        "dimensionless",
                        "PCA reference comparison follows deterministic sign normalization.",
                        absolute=1e-10,
                        relative=1e-10,
                    ),
                    numeric=True,
                ),
                _link(
                    "data.composition.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_composition_space.py::test_pca_rejects_insufficient_sample_count_and_rank",
                    "Synthetic insufficient-rank composition matrices.",
                    "PCA applicability boundary",
                    ["insufficient samples/rank fail explicitly"],
                ),
            ],
        ),
        _evidence(
            "ml.regression_evaluation",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("ml.regression_evaluation"),
            ["profile-bound supervised prediction/evaluation tables with paired truth and prediction"],
            [
                "Metrics describe predictive association, not causality.",
                "Model training correctness is outside this evaluation capability.",
            ],
            "SEEDED_STOCHASTIC",
            [
                _link(
                    "ml.regression.reference.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_materials_ml_evaluation.py::test_metric_definitions_handle_constant_target_and_curve_bounding",
                    "Small arrays with hand-computable regression metrics.",
                    "MAE/RMSE/R2 metric definitions",
                    ["metric values and constant-target behavior match analytical definitions"],
                    units=["target_unit", "dimensionless"],
                    tolerance=_tolerance(
                        "target_unit",
                        "Metrics are analytical sums and square roots over bounded arrays.",
                        absolute=1e-12,
                        relative=1e-10,
                    ),
                    numeric=True,
                ),
                _link(
                    "ml.regression.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_materials_ml_evaluation.py::test_payload_replay_is_deterministic_and_plot_sampling_does_not_change_metrics",
                    "Equivalent paired evaluation rows and bounded plot samples.",
                    "Metric replay and presentation-sampling invariance",
                    ["plot sampling does not change authoritative metrics"],
                ),
                _link(
                    "ml.regression.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_materials_ml_evaluation.py::test_typed_semantic_unit_uncertainty_and_cap_failures",
                    "Synthetic unit, uncertainty, and resource-cap violations.",
                    "ML evaluation applicability boundary",
                    ["semantic/unit mismatch and unsupported uncertainty fail explicitly"],
                ),
            ],
        ),
        _evidence(
            "ml.uncertainty_evaluation",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("ml.uncertainty_evaluation"),
            ["profile-bound supervised prediction tables with paired truth, prediction, and uncertainty"],
            [
                "Uncertainty diagnostics are association and retention diagnostics, not calibration proof.",
                "Model training and uncertainty-generation correctness are outside this evaluation capability.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "ml.uncertainty.reference.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_materials_ml_evaluation.py::test_uncertainty_product_has_explicit_association_and_retention_policy",
                    "Small prediction table with explicit uncertainty values.",
                    "Uncertainty association and error-decay semantics",
                    ["uncertainty association, reliability bins, and bounded error decay are emitted"],
                ),
                _link(
                    "ml.uncertainty.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_materials_ml_evaluation.py::test_uncertainty_product_has_explicit_association_and_retention_policy",
                    "Equivalent uncertainty-bearing prediction rows.",
                    "Uncertainty replay and association invariance",
                    ["uncertainty diagnostics remain tied to the same profile bindings and bounded rows"],
                ),
                _link(
                    "ml.uncertainty.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_materials_ml_evaluation.py::test_typed_semantic_unit_uncertainty_and_cap_failures",
                    "Negative uncertainty and missing-binding fixtures.",
                    "Uncertainty applicability boundary",
                    ["negative, missing, or ambiguous uncertainty bindings fail explicitly"],
                ),
            ],
        ),
        _evidence(
            "ml.classification_evaluation",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("ml.classification_evaluation"),
            ["profile-bound supervised classification tables with labels or bounded class probabilities"],
            [
                "Classification metrics describe the supplied labels and predictions, not model-training quality.",
                "ROC/PR curves are unavailable for single-class inputs.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "ml.classification.reference.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_materials_ml_evaluation.py::test_classification_product_preserves_class_labels_and_binary_curves",
                    "Small binary classification table with known class labels.",
                    "Classification metrics and curve semantics",
                    ["class labels, confusion matrix, accuracy, and bounded binary curves are preserved"],
                ),
                _link(
                    "ml.classification.invariant.v1",
                    ScientificEvidenceKind.INVARIANT,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_materials_ml_evaluation.py::test_classification_product_preserves_class_labels_and_binary_curves",
                    "Equivalent classification rows with stable labels.",
                    "Classification replay invariance",
                    ["class labels and bounded metrics remain stable under equivalent row presentation"],
                ),
                _link(
                    "ml.classification.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_materials_ml_evaluation.py::test_classification_missing_probability_multiclass_and_unknown_positive_policy",
                    "Missing probability, multiclass, and positive-class policy fixtures.",
                    "Classification applicability boundary",
                    ["missing predictions, ambiguous classes, and unsupported probability bindings fail explicitly"],
                ),
            ],
        ),
        _evidence(
            "structure.brillouin_zone",
            ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED,
            _qualified_fingerprint("structure.brillouin_zone"),
            [
                "one ordered periodic crystal structure within the bounded Brillouin-zone contract"
            ],
            [
                "Primitive-cell standardization and high-symmetry paths use the locked pymatgen implementation.",
                "The result describes reciprocal geometry for the exact supplied structure and does not infer phonon eigenvectors.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "structure.brillouin-zone.external.v1",
                    ScientificEvidenceKind.ADAPTER_SEMANTICS,
                    ReferenceAuthority.OFFICIAL_LIBRARY_SEMANTICS,
                    "tests/test_brillouin_zone_adapter.py::test_valid_simple_cubic_emits_six_valid_inert_artifacts",
                    "Curated periodic structures executed through the registered Brillouin-zone Adapter.",
                    "Reciprocal lattice, Wigner-Seitz zone, and high-symmetry path mapping",
                    [
                        "the complete six-artifact package validates and remains source-bound"
                    ],
                    units=["angstrom^-1", "angstrom^-3"],
                    version="locked pymatgen dependency",
                ),
                _link(
                    "structure.brillouin-zone.reference.v1",
                    ScientificEvidenceKind.REFERENCE,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_brillouin_zone_contract.py::test_reciprocal_duality_volume_and_coordinate_round_trip",
                    "Analytical reciprocal-duality fixtures for bounded lattices.",
                    "Reciprocal basis and coordinate round-trip",
                    [
                        "B=2*pi*A^-T and reciprocal coordinate round trips match the analytical reference"
                    ],
                    units=["angstrom^-1", "angstrom^-3"],
                    tolerance=_tolerance(
                        "angstrom^-1",
                        "Reciprocal basis and coordinate comparisons use the sealed numerical contract.",
                        absolute=1e-11,
                        relative=1e-11,
                    ),
                    numeric=True,
                ),
                _link(
                    "structure.brillouin-zone.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_brillouin_zone_adapter.py::test_dimensionality_singular_and_ill_conditioned_inputs_are_typed",
                    "Synthetic non-periodic, singular, and ill-conditioned structure fixtures.",
                    "Brillouin-zone applicability boundary",
                    [
                        "invalid lattice geometry fails before scientific Artifact publication"
                    ],
                ),
                _link(
                    "structure.brillouin-zone.result-projection.v1",
                    ScientificEvidenceKind.RESULT_PROJECTION,
                    ReferenceAuthority.ANALYTICAL,
                    "tests/test_agent2_results.py::test_brillouin_zone_projector_requires_complete_verified_triad_and_projects_kpath_count",
                    "Verified reciprocal-lattice, Brillouin-zone, and k-path production fixtures.",
                    "Complete reciprocal-space ScientificResult projection",
                    [
                        "all three primary schemas are required before publication",
                        "the high-symmetry point count is derived from the verified k-path points",
                    ],
                    units=["count"],
                ),
            ],
        ),
        _evidence(
            "structure.summary",
            ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED,
            _qualified_fingerprint("structure.summary"),
            ["authorized periodic crystal structures with bounded site counts and valid lattices"],
            [
                "Space-group labels use the declared pymatgen/spglib tolerances and describe only the supplied structure.",
                "The summary does not infer physical properties, stability, or causal mechanisms.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "structure.summary.adapter.v2",
                    ScientificEvidenceKind.ADAPTER_SEMANTICS,
                    ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
                    "tests/test_lightweight_structure_adapters.py::test_structure_summary_generates_json_summary_and_recipe",
                    "Curated periodic crystal structures evaluated by the registered structure.summary Tool.",
                    "Composition, lattice, and pymatgen/spglib symmetry summary",
                    ["formula, site count, lattice parameters, space group, and crystal system remain source-bound"],
                    units=["angstrom", "degree", "angstrom^3"],
                    tolerance=_tolerance(
                        "angstrom",
                        "The adapter preserves rounded source lattice values; symmetry uses explicit fixed tolerances.",
                        absolute=1e-8,
                    ),
                    numeric=True,
                ),
                _link(
                    "structure.summary.result.v2",
                    ScientificEvidenceKind.RESULT_PROJECTION,
                    ReferenceAuthority.CURATED_KNOWN_RESULT,
                    "tests/test_agent2_capabilities.py::test_structure_summary_projects_authoritative_lattice_and_symmetry_facts",
                    "Canonical structure.summary Artifact with known lattice and symmetry fields.",
                    "Typed ScientificResult fact projection",
                    ["lattice and symmetry facts retain exact Artifact locators and never derive from viewer output"],
                ),
            ],
        ),
        _evidence(
            "structure.viewer_scene",
            ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED,
            _qualified_fingerprint("structure.viewer_scene"),
            ["authorized crystal structures with bounded viewer-scene resource limits"],
            [
                "The viewer scene is an inert presentation artifact and is not scientific computation.",
                "Scene output does not establish material identity or physical causality.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "structure.viewer.reference.v1",
                    ScientificEvidenceKind.ADAPTER_SEMANTICS,
                    ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
                    "tests/test_viewer_scene_adapter.py::test_viewer_scene_adapter_generates_canonical_scene_manifest_summary_and_recipe",
                    "Curated crystal structure viewer fixture.",
                    "Viewer scene and manifest contract",
                    ["scene, manifest, summary, and recipe remain schema-valid and bounded"],
                ),
                _link(
                    "structure.viewer.domain.v1",
                    ScientificEvidenceKind.DOMAIN_NEGATIVE,
                    ReferenceAuthority.SYNTHETIC_EXACT,
                    "tests/test_viewer_scene_adapter.py::test_viewer_scene_adapter_rejects_invalid_params_and_numeric_values",
                    "Invalid viewer parameters and non-finite structure fixtures.",
                    "Viewer resource and numeric boundary",
                    ["invalid parameters and non-finite structure values fail before publication"],
                ),
            ],
        ),
        _evidence(
            "trajectory.viewer_scene",
            ScientificQualificationLevel.NOT_YET_SCIENTIFICALLY_QUALIFIED,
            _qualified_fingerprint("trajectory.viewer_scene"),
            ["validated atomic trajectories within the formal bounded trajectory viewer contract"],
            [
                "The viewer product is an inert presentation output and is not a trajectory analytics capability.",
                "MSD, diffusion, RDF, dynamic bonds, editing, and video export remain separate capabilities or unsupported surfaces.",
            ],
            "DETERMINISTIC",
            [
                _link(
                    "trajectory.viewer.contract.v1",
                    ScientificEvidenceKind.ADAPTER_SEMANTICS,
                    ReferenceAuthority.CURATED_KNOWN_RESULT,
                    "tests/test_agent2_capabilities.py::test_p10_c04_trajectory_viewer_is_agent2_reachable_without_question_matching",
                    "Formal bounded trajectory viewer adapter contract.",
                    "Agent2 capability binding to the canonical trajectory viewer Tool",
                    ["the semantic trajectory-view requirement resolves to the registered viewer Tool and complete inert artifact family"],
                ),
            ],
        ),
        *[
            _evidence(
                capability_id,
                ScientificQualificationLevel.EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED,
                _qualified_fingerprint(capability_id),
                applicability,
                limitations,
                "DETERMINISTIC",
                links,
            )
            for capability_id, applicability, limitations, links in [
                (
                    "electronic.band_structure",
                    ["supplied electronic band resources with explicit energy reference metadata"],
                    [
                        "The platform validates parsing and band semantics, not the upstream electronic solver.",
                        "Metal-like classification is policy-qualified rather than material truth.",
                    ],
                    [
                        _link(
                            "electronic.band.external.v1",
                            ScientificEvidenceKind.ADAPTER_SEMANTICS,
                            ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
                            "tests/test_electronic_band_dos.py::test_indirect_gap_vbm_cbm_and_source_qualified_classification",
                            "Curated supplied electronic band fixture.",
                            "Band parser and semantic classification",
                            ["gap, VBM, CBM, units, and source-qualified classification are preserved"],
                            units=["eV"],
                            tolerance=_tolerance(
                                "eV",
                                "Electronic energy fixtures use the sealed 1e-8 eV policy.",
                                absolute=1e-8,
                            ),
                            numeric=True,
                        ),
                        _link(
                            "electronic.band.domain.v1",
                            ScientificEvidenceKind.DOMAIN_NEGATIVE,
                            ReferenceAuthority.SYNTHETIC_EXACT,
                            "tests/test_electronic_band_dos.py::test_missing_fermi_preserves_raw_band_but_rejects_fermi_view",
                            "Synthetic missing-Fermi band fixture.",
                            "Electronic metadata boundary",
                            ["raw band remains available while unsupported Fermi-relative view is rejected"],
                        ),
                    ],
                ),
                (
                    "electronic.dos",
                    ["supplied electronic DOS resources with explicit energy and density semantics"],
                    [
                        "The platform validates parsing/projection, not the upstream electronic solver.",
                        "Partial DOS is preserved without recomputation.",
                    ],
                    [
                        _link(
                            "electronic.dos.external.v1",
                            ScientificEvidenceKind.ADAPTER_SEMANTICS,
                            ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
                            "tests/test_electronic_band_dos.py::test_dos_preserves_total_partial_projection_and_no_recomputation",
                            "Curated supplied total/partial DOS fixture.",
                            "DOS parser and semantic projection",
                            ["energy units, total/partial series, and no-recomputation boundary are preserved"],
                            units=["eV", "states/eV"],
                            tolerance=_tolerance(
                                "eV",
                                "Electronic energy fixtures use the sealed 1e-8 eV policy.",
                                absolute=1e-8,
                            ),
                            numeric=True,
                        ),
                        _link(
                            "electronic.dos.domain.v1",
                            ScientificEvidenceKind.DOMAIN_NEGATIVE,
                            ReferenceAuthority.SYNTHETIC_EXACT,
                            "tests/test_electronic_band_dos.py::test_checked_resource_and_artifact_schemas_are_strict",
                            "Malformed electronic resource and Artifact fixtures.",
                            "Strict electronic schema boundary",
                            ["unknown or malformed semantic fields fail explicitly"],
                        ),
                    ],
                ),
                (
                    "phonon.band",
                    ["supplied phonopy band resources with explicit frequency units"],
                    [
                        "The platform validates parser/semantic mapping, not force-constant generation.",
                        "Negative frequencies are retained as supplied and not reinterpreted as stability proof.",
                    ],
                    [
                        _link(
                            "phonon.band.external.v1",
                            ScientificEvidenceKind.ADAPTER_SEMANTICS,
                            ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
                            "tests/test_phonon_bands.py::test_phonopy_yaml_maps_qpoints_segments_branches_and_negative_frequency",
                            "Curated phonopy YAML band fixture.",
                            "Phonopy band parser and semantic mapping",
                            ["q-points, path segments, branches, sign, and frequency units are preserved"],
                            units=["THz"],
                            tolerance=_tolerance(
                                "THz",
                                "Near-zero frequencies use producer-specific 1e-6/1e-5 THz policy.",
                                absolute=1e-6,
                                relative=1e-5,
                            ),
                            numeric=True,
                        ),
                        _link(
                            "phonon.band.domain.v1",
                            ScientificEvidenceKind.DOMAIN_NEGATIVE,
                            ReferenceAuthority.SYNTHETIC_EXACT,
                            "tests/test_phonon_bands.py::test_invalid_canonical_input_is_rejected_before_artifact_export",
                            "Malformed canonical phonon band fixtures.",
                            "Phonon band schema boundary",
                            ["invalid bands fail before Artifact export"],
                        ),
                    ],
                ),
                (
                    "phonon.dos",
                    ["supplied total/projected phonon DOS with declared frequency unit"],
                    [
                        "The platform validates DOS conversion/projection, not force-constant generation.",
                        "Partial projections do not imply a complete modal sum.",
                    ],
                    [
                        _link(
                            "phonon.dos.external.v1",
                            ScientificEvidenceKind.ADAPTER_SEMANTICS,
                            ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
                            "tests/test_phonon_dos.py::test_phonopy_total_dos_converts_frequency_density_and_preserves_integral",
                            "Curated phonopy total DOS fixture in convertible units.",
                            "Frequency/density unit conversion with Jacobian",
                            ["frequency conversion and integrated DOS are preserved"],
                            units=["THz", "states/THz"],
                            tolerance=_tolerance(
                                "dimensionless",
                                "Numerical integration must remain invariant under the declared unit conversion.",
                                absolute=1e-8,
                                relative=1e-7,
                            ),
                            numeric=True,
                        ),
                        _link(
                            "phonon.dos.domain.v1",
                            ScientificEvidenceKind.DOMAIN_NEGATIVE,
                            ReferenceAuthority.SYNTHETIC_EXACT,
                            "tests/test_phonon_dos.py::test_malformed_sources_fail_before_artifact_export",
                            "Malformed total/projected DOS fixtures.",
                            "Phonon DOS schema boundary",
                            ["malformed sources fail before Artifact export"],
                        ),
                    ],
                ),
                (
                    "phonon.band_dos",
                    ["compatible supplied phonon band and DOS resources"],
                    [
                        "Composition is reference-only and does not recompute either source.",
                        "Structure/hash incompatibility is terminal.",
                    ],
                    [
                        _link(
                            "phonon.band-dos.external.v1",
                            ScientificEvidenceKind.ADAPTER_SEMANTICS,
                            ReferenceAuthority.EXTERNAL_SOLVER_SEMANTICS,
                            "tests/test_phonon_band_dos.py::test_density_conversion_preserves_integral_and_scales_broadening",
                            "Curated band/DOS fixtures with analytically convertible units.",
                            "Reference-only composition and density Jacobian",
                            ["DOS integral and broadening semantics survive conversion/composition"],
                            units=["THz", "states/THz"],
                            tolerance=_tolerance(
                                "dimensionless",
                                "Integrated density remains invariant under exact Jacobian conversion.",
                                absolute=1e-8,
                                relative=1e-7,
                            ),
                            numeric=True,
                        ),
                        _link(
                            "phonon.band-dos.domain.v1",
                            ScientificEvidenceKind.DOMAIN_NEGATIVE,
                            ReferenceAuthority.SYNTHETIC_EXACT,
                            "tests/test_phonon_band_dos.py::test_structure_mismatch_and_hash_mismatch_fail_before_success_products",
                            "Synthetic source identity/hash mismatch fixtures.",
                            "Composite source compatibility boundary",
                            ["incompatible sources fail before a combined product exists"],
                        ),
                    ],
                ),
            ]
        ],
    ]


def _contract_coverage_records() -> list[CapabilityQualityEvidence]:
    shared_links = [
        _link(
            "agent2.contract-coverage.reference.v1",
            ScientificEvidenceKind.REFERENCE,
            ReferenceAuthority.CURATED_KNOWN_RESULT,
            "tests/test_agent2_planning.py::test_mandatory_capability_tool_suites_bind_complete_stable_coverage",
            "Registered multi-requirement capability suites with exact Tool coverage.",
            "Mandatory capability-to-Tool coverage",
            [
                "every registered mandatory Tool is bound exactly once",
                "repeated binding preserves the same mandatory Tool family",
            ],
        ),
        _link(
            "agent2.contract-coverage.invariant.v1",
            ScientificEvidenceKind.INVARIANT,
            ReferenceAuthority.CURATED_KNOWN_RESULT,
            "tests/test_agent2_planning.py::test_mandatory_capability_tool_suites_bind_complete_stable_coverage",
            "Repeated immutable CapabilityPlan binding.",
            "Deterministic coverage stability",
            ["mandatory capability coverage is independent of Tool insertion order"],
        ),
        _link(
            "agent2.contract-coverage.negative.v1",
            ScientificEvidenceKind.DOMAIN_NEGATIVE,
            ReferenceAuthority.SYNTHETIC_EXACT,
            "tests/test_agent2_results.py::test_mandatory_tool_coverage_projection_rejects_missing_tool_output",
            "Synthetic incomplete execution with one mandatory Tool output omitted.",
            "Incomplete contract projection rejection",
            ["missing mandatory Tool output prevents authoritative Result publication"],
        ),
    ]
    return [
        _evidence(
            "data.composition_analysis",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("data.composition_analysis"),
            ["profiled materials tables with parseable formula/composition columns"],
            [
                "Composition distributions are descriptive.",
                "Unparseable formulas remain explicit bounded warnings or typed failures.",
            ],
            "DETERMINISTIC",
            shared_links,
        ),
        _evidence(
            "data.table_analysis",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("data.table_analysis"),
            ["profiled tabular datasets with at least two numeric columns"],
            [
                "Correlation and scatter products are descriptive and do not establish causality.",
                "Selected columns remain bounded by the registered Tool schemas.",
            ],
            "DETERMINISTIC",
            shared_links,
        ),
        _evidence(
            "structure.coordination_analysis",
            ScientificQualificationLevel.DOMAIN_VALIDATED,
            _qualified_fingerprint("structure.coordination_analysis"),
            ["validated periodic crystal structures within coordination resource limits"],
            [
                "CrystalNN and VoronoiNN retain their distinct method assumptions.",
                "Local-environment polyhedra consume an exact committed coordination Artifact.",
            ],
            "DETERMINISTIC",
            shared_links,
        ),
    ]


QUALITY_EVIDENCE_BY_CAPABILITY: dict[str, CapabilityQualityEvidence] = {
    item.capability_id: item for item in [*_records(), *_contract_coverage_records()]
}


def get_capability_quality_evidence(capability_id: str) -> CapabilityQualityEvidence:
    return QUALITY_EVIDENCE_BY_CAPABILITY[capability_id]


def qualification_for_capability(capability_id: str) -> CapabilityQualification:
    evidence = get_capability_quality_evidence(capability_id)
    counts = evidence.evidence_counts
    return CapabilityQualification(
        level=evidence.qualification_level.value,
        evidence_refs=sorted({item.test_node for item in evidence.evidence}),
        validated_domains=evidence.applicability_domains,
        known_limitations=evidence.known_limitations,
        evidence_version=QUALITY_EVIDENCE_VERSION,
        evidence_fingerprint=evidence.evidence_fingerprint,
        reference_case_count=counts.get(ScientificEvidenceKind.REFERENCE.value, 0),
        invariant_case_count=counts.get(ScientificEvidenceKind.INVARIANT.value, 0),
        domain_negative_case_count=counts.get(
            ScientificEvidenceKind.DOMAIN_NEGATIVE.value,
            0,
        ),
        result_projection_case_count=counts.get(
            ScientificEvidenceKind.RESULT_PROJECTION.value,
            0,
        ),
        interpretation_evaluation_count=counts.get(
            ScientificEvidenceKind.INTERPRETATION.value,
            0,
        ),
        report_evaluation_count=counts.get(ScientificEvidenceKind.REPORT.value, 0),
        reproducibility=evidence.reproducibility,
    )


__all__ = [
    "CapabilityQualityEvidence",
    "QUALITY_EVIDENCE_BY_CAPABILITY",
    "QUALITY_EVIDENCE_VERSION",
    "ReferenceAuthority",
    "ScientificEvidenceKind",
    "ScientificEvidenceLink",
    "ScientificQualificationLevel",
    "ScientificTolerance",
    "get_capability_quality_evidence",
    "qualification_for_capability",
    "scientific_contract_fingerprint",
]
