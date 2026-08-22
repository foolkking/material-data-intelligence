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
