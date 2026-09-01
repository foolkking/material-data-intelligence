"""Typed Agent 2.0 domain failures."""


class Agent2DomainError(ValueError):
    """Base class for deterministic Agent 2.0 domain failures."""


class ScientificObjectNotFound(Agent2DomainError):
    pass


class ScientificObjectVersionNotFound(Agent2DomainError):
    pass


class ScientificObjectTypeNotRegistered(Agent2DomainError):
    pass


class InvalidScientificObjectVersion(Agent2DomainError):
    pass


class InvalidScientificObjectRelationship(Agent2DomainError):
    pass


class ResearchTurnNotFound(Agent2DomainError):
    pass


class InvalidResearchTurnTransition(Agent2DomainError):
    pass


class ConcurrentTurnModification(Agent2DomainError):
    pass


class ResearchResourceLimitExceeded(Agent2DomainError):
    def __init__(self, message: str, *, limit: int, active: int) -> None:
        super().__init__(message)
        self.limit = limit
        self.active = active


class ResearchSessionProjectMismatch(Agent2DomainError):
    pass


class UnauthorizedScientificObjectReference(Agent2DomainError):
    pass


class RegistryValidationError(Agent2DomainError):
    pass


class CapabilityNotRegistered(RegistryValidationError):
    pass


class RequirementNotRegistered(RegistryValidationError):
    pass


class ScientificResultSnapshotNotFound(Agent2DomainError):
    pass


class ResearchTurnDecisionNotFound(Agent2DomainError):
    pass


class InvalidResearchTurnDecision(Agent2DomainError):
    def __init__(self, message: str, *, code: str = "ORCHESTRATOR_INVALID_OUTPUT") -> None:
        super().__init__(message)
        self.code = code


class OrchestratorProviderUnavailable(Agent2DomainError):
    pass


class OrchestratorTimeout(Agent2DomainError):
    pass


class ContextAssemblyFailed(Agent2DomainError):
    pass


class CapabilityResolutionFailed(Agent2DomainError):
    pass


class CapabilityRequirementUnsatisfied(CapabilityResolutionFailed):
    pass


class CapabilityPlanInvalid(Agent2DomainError):
    def __init__(self, message: str, *, code: str = "CAPABILITY_PLAN_INVALID") -> None:
        super().__init__(message)
        self.code = code


class CapabilityBindingFailed(Agent2DomainError):
    def __init__(self, message: str, *, code: str = "CAPABILITY_BINDING_FAILED") -> None:
        super().__init__(message)
        self.code = code


class ScientificResultNotReady(Agent2DomainError):
    pass


class ScientificResultProjectionNotSupported(Agent2DomainError):
    pass


class ScientificResultProjectionFailed(Agent2DomainError):
    def __init__(self, message: str, *, code: str = "RESULT_PROJECTION_FAILED") -> None:
        super().__init__(message)
        self.code = code


class ScientificResultProjectionConflict(ScientificResultProjectionFailed):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="RESULT_PROJECTION_CONFLICT")


class ScientificResultSourceUnavailable(ScientificResultProjectionFailed):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="RESULT_SOURCE_UNAVAILABLE")


class InvalidScientificResultBundle(ScientificResultProjectionFailed):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="INVALID_SCIENTIFIC_RESULT_BUNDLE")


class InvalidScientificFactSource(ScientificResultProjectionFailed):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="INVALID_SCIENTIFIC_FACT_SOURCE")


class UnauthorizedScientificResultReference(ScientificResultProjectionFailed):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="UNAUTHORIZED_SCIENTIFIC_RESULT_REFERENCE")


class ResultProjectorNotRegistered(ScientificResultProjectionFailed):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="RESULT_PROJECTOR_NOT_REGISTERED")
