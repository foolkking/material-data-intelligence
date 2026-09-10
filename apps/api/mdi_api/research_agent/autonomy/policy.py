from __future__ import annotations

from mdi_api.research_agent.autonomy.schemas import (
    AutonomyPolicy,
    CapabilityQualificationSnapshot,
)
from mdi_api.research_agent.capabilities.quality_evidence import (
    get_capability_quality_evidence,
    scientific_contract_fingerprint,
)
from mdi_api.research_agent.schemas import CapabilityManifest


DEFAULT_AUTONOMY_POLICY = AutonomyPolicy()

_COST_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


class CapabilityAutonomyPolicy:
    """Deterministic quality/cost gate for autonomous capability selection."""

    def __init__(self, policy: AutonomyPolicy = DEFAULT_AUTONOMY_POLICY) -> None:
        self.policy = policy

    def qualification_snapshot(
        self, manifest: CapabilityManifest
    ) -> CapabilityQualificationSnapshot:
        level = manifest.qualification.level
        contract_fingerprint = scientific_contract_fingerprint(manifest)
        evidence_current = False
        reason = "QUALIFICATION_LEVEL_NOT_ALLOWED"
        try:
            evidence = get_capability_quality_evidence(manifest.capability_id)
            evidence_current = (
                evidence.capability_version == manifest.version
                and evidence.qualified_contract_fingerprint == contract_fingerprint
                and evidence.evidence_fingerprint
                == manifest.qualification.evidence_fingerprint
            )
        except KeyError:
            evidence_current = False
        cost = (
            manifest.resource_profile.expected_cost_class
            if manifest.resource_profile.expected_cost_class != "DERIVED_FROM_TOOL"
            else "MEDIUM"
        )
        cost_allowed = _COST_ORDER[cost] <= _COST_ORDER[self.policy.max_cost_class]
        allowed = (
            level in self.policy.allowed_qualification_levels
            and evidence_current
            and cost_allowed
        )
        if not evidence_current:
            reason = "QUALIFICATION_EVIDENCE_STALE_OR_MISSING"
        elif not cost_allowed:
            reason = "AUTONOMY_COST_CLASS_EXCEEDED"
        elif allowed:
            reason = "QUALIFICATION_CURRENT_AND_ALLOWED"
        return CapabilityQualificationSnapshot(
            capability_id=manifest.capability_id,
            capability_version=manifest.version,
            qualification_level=level,
            allowed_for_autonomy=allowed,
            evidence_version=manifest.qualification.evidence_version,
            evidence_fingerprint=manifest.qualification.evidence_fingerprint,
            scientific_contract_fingerprint=contract_fingerprint,
            validated_domains=list(manifest.qualification.validated_domains),
            known_limitations=list(manifest.qualification.known_limitations[:8]),
            reason_code=reason,
        )


__all__ = ["CapabilityAutonomyPolicy", "DEFAULT_AUTONOMY_POLICY"]
