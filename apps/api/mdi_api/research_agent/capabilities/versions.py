from __future__ import annotations

from mdi_api.agent2_errors import RegistryValidationError


def version_satisfies(version: str, constraint: str) -> bool:
    def parts(value: str) -> tuple[int, ...]:
        try:
            return tuple(int(item) for item in value.strip().split("."))
        except ValueError as exc:
            raise RegistryValidationError(f"Invalid semantic version: {value}") from exc
    actual = parts(version)
    for clause in (item.strip() for item in constraint.split(",") if item.strip()):
        operator = next((item for item in (">=", "<=", "==", ">", "<") if clause.startswith(item)), "==")
        expected = parts(clause[len(operator):] if clause.startswith(operator) else clause)
        if not {">=": actual >= expected, "<=": actual <= expected, "==": actual == expected, ">": actual > expected, "<": actual < expected}[operator]:
            return False
    return True
