from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from sqlalchemy.engine import make_url

_spec = importlib.util.spec_from_file_location("mdi_local_setup", Path(__file__).resolve().parents[1] / "scripts/local_setup.py")
setup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(setup)


@pytest.fixture
def fresh_config(tmp_path, monkeypatch):
    root = tmp_path / "new project runtime"
    path = setup.initialize(root)
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            monkeypatch.setenv(key, value)
    monkeypatch.setenv("MDI_DATA_ROOT", str(root / "data"))
    monkeypatch.setenv("MDI_TEMP_ROOT", str(root / "tmp"))
    return path


def test_generated_config_is_valid_and_init_preserves_existing_secrets(fresh_config):
    before = fresh_config.read_bytes()
    values = dict(line.split("=", 1) for line in fresh_config.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#"))
    assert Path(values["MDI_LOCAL_ROOT"]).resolve() == fresh_config.parent.resolve()
    assert Path(values["MDI_DATA_ROOT"]).resolve() == fresh_config.parent.joinpath("data").resolve()
    assert Path(values["MDI_RUNTIME_ROOT"]).resolve() == fresh_config.parent.joinpath("run").resolve()
    assert Path(values["MDI_LOG_ROOT"]).resolve() == fresh_config.parent.joinpath("logs").resolve()
    assert Path(values["MDI_TEMP_ROOT"]).resolve() == fresh_config.parent.joinpath("tmp").resolve()
    assert Path(values["MDI_CACHE_ROOT"]).resolve() == fresh_config.parent.joinpath("cache").resolve()
    assert Path(values["MDI_NEXT_DIST_DIR"]).resolve() == fresh_config.parent.joinpath("cache", "next").resolve()
    assert Path(values["MDI_ARTIFACT_ROOT"]).resolve() == fresh_config.parent.joinpath("data", "artifacts").resolve()
    assert all(value != "CHANGE_ME" for value in values.values())
    settings = setup.checked_settings()
    assert settings.postgres_port == 55434
    assert settings.auth_required
    assert "CHANGE_ME" not in settings.postgres_password
    setup.initialize(fresh_config.parent)
    assert fresh_config.read_bytes() == before


def test_independent_installs_generate_distinct_credentials(tmp_path):
    first = setup.initialize(tmp_path / "a").read_text()
    second = setup.initialize(tmp_path / "b").read_text()
    assert first != second
    for text in (first, second):
        key = next(line.split("=", 1)[1] for line in text.splitlines() if line.startswith("MDI_PROVIDER_ENCRYPTION_KEY="))
        assert Fernet(key.encode()).decrypt(Fernet(key.encode()).encrypt(b"roundtrip")) == b"roundtrip"


def test_init_rejects_runtime_in_source_tree():
    with pytest.raises(ValueError, match="outside the repository"):
        setup.initialize(setup.REPO / "runtime")


def test_pytest_cache_is_external(request):
    cache = request.config.cache._cachedir.resolve()
    assert not cache.is_relative_to(setup.REPO)
    assert cache.name == "pytest-cache"


def test_database_password_is_escaped_without_changing_credentials(fresh_config, monkeypatch):
    password = "space @:/#%+密码"
    monkeypatch.setenv("POSTGRES_PASSWORD", password)
    settings = setup.checked_settings()
    assert make_url(settings.database_url).password == password


@pytest.mark.parametrize("key,value,message", [
    ("POSTGRES_PASSWORD", "CHANGE_ME", "POSTGRES_PASSWORD"),
    ("MDI_PROVIDER_ENCRYPTION_KEY", "invalid-private-value", "valid Fernet key"),
    ("MDI_LOCAL_USER_PASSWORD", "short", "12 characters"),
    ("MDI_AUTH_REQUIRED", "false", "MDI_AUTH_REQUIRED"),
    ("DATABASE_URL", "postgresql+psycopg://mdi:hidden@127.0.0.1:11111/mdi", "must agree"),
])
def test_invalid_config_has_actionable_redacted_errors(fresh_config, monkeypatch, key, value, message):
    monkeypatch.setenv(key, value)
    with pytest.raises(ValueError, match=message) as error:
        setup.checked_settings()
    assert value not in str(error.value)


def test_cluster_initialization_never_overwrites_unknown_data(fresh_config):
    data = fresh_config.parent / "data/postgres"
    data.mkdir(parents=True)
    sentinel = data / "keep-me"
    sentinel.write_bytes(b"user data")
    with pytest.raises(ValueError, match="leaving it untouched"):
        setup.initialize_cluster(Path("unused-binary-directory"))
    assert sentinel.read_bytes() == b"user data"
