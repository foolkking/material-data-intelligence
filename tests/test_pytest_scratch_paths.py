from pathlib import Path

import pytest

from tests.conftest import _pytest_scratch_paths


def test_default_scratch_is_external_and_preserves_pytest_retention(tmp_path):
    root = tmp_path / "repository"
    scratch, explicit = _pytest_scratch_paths(root, None, None)
    assert scratch == tmp_path / "repository.local" / "tmp" / "pytest"
    assert explicit is None


def test_configured_local_root_and_explicit_scratch_child(tmp_path):
    local = tmp_path / "runtime"
    scratch, explicit = _pytest_scratch_paths(tmp_path / "repo", str(local), "focused-run")
    assert scratch == local / "tmp" / "pytest"
    assert explicit == scratch / "focused-run"


@pytest.mark.parametrize("target", [".", "..", "../data", "../../postgresql"])
def test_explicit_basetemp_cannot_clear_scratch_root_or_data(tmp_path, target):
    with pytest.raises(pytest.UsageError, match="SCRATCH_CHILD"):
        _pytest_scratch_paths(tmp_path / "repo", str(tmp_path / "runtime"), target)


def test_rejects_repository_local_runtime_and_unrelated_absolute_directory(tmp_path):
    root = tmp_path / "repo"
    with pytest.raises(pytest.UsageError, match="OUTSIDE_REPOSITORY"):
        _pytest_scratch_paths(root, str(root / "local"), None)
    with pytest.raises(pytest.UsageError, match="SCRATCH_CHILD"):
        _pytest_scratch_paths(root, None, str(tmp_path / "user-data"))


def test_actual_tmp_path_is_in_dedicated_external_scratch(tmp_path):
    root = Path(__file__).resolve().parents[1]
    assert not tmp_path.resolve().is_relative_to(root)
    assert "pytest" in tmp_path.parts


def test_explicit_temporary_root_retains_dedicated_scratch_and_delete_boundary(tmp_path):
    root = tmp_path / "repo"
    temporary = tmp_path / "custom-temporary"
    scratch, explicit = _pytest_scratch_paths(root, None, "run-1", str(temporary))
    assert scratch == temporary / "pytest"
    assert explicit == scratch / "run-1"
    for target in (str(temporary), str(scratch), "../other-task"):
        with pytest.raises(pytest.UsageError, match="SCRATCH_CHILD"):
            _pytest_scratch_paths(root, None, target, str(temporary))
    with pytest.raises(pytest.UsageError, match="OUTSIDE_REPOSITORY"):
        _pytest_scratch_paths(root, None, None, str(root / "temp"))
