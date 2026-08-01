from scripts.finalize_phase10m1_evidence import EVIDENCE, MANIFEST, REQUIRED, verify_manifest


def test_phase10m1_evidence_manifest_is_complete_and_verifiable() -> None:
    assert EVIDENCE.is_dir()
    assert MANIFEST.is_file()
    assert REQUIRED.issubset(
        {path.relative_to(EVIDENCE).as_posix() for path in EVIDENCE.rglob("*") if path.is_file()}
    )
    verify_manifest()
