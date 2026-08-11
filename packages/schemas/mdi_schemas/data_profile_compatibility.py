from __future__ import annotations


SUPPORTED_DATAPROFILE_CONTRACT_VERSIONS = frozenset(
    {
        "2.0",
        "2.1",
        "2.2",
        "2.3",
        "2.4",
    }
)
CURRENT_DATAPROFILE_CONTRACT_VERSION = "2.4"


def is_supported_data_profile_contract_version(value: str | None) -> bool:
    """Return whether a profile contract is an explicitly supported version."""

    return value in SUPPORTED_DATAPROFILE_CONTRACT_VERSIONS
