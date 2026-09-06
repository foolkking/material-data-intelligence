from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
LOCK = ROOT / ".github" / "workflows" / "provenance.lock.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def _walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "uses":
                yield "action", item
            elif key == "image":
                yield "image", item
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def test_all_third_party_actions_and_service_images_are_immutable() -> None:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    references = list(_walk(workflow))
    actions = [value for kind, value in references if kind == "action"]
    images = [value for kind, value in references if kind == "image"]

    assert actions
    assert images
    for action in actions:
        repository, commit = str(action).rsplit("@", 1)
        assert "/" in repository
        assert FULL_SHA.fullmatch(commit)
    for image in images:
        _, digest = str(image).rsplit("@", 1)
        assert DIGEST.fullmatch(digest)


def test_provenance_lock_matches_every_workflow_reference() -> None:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    workflow_source = WORKFLOW.read_text(encoding="utf-8")

    assert lock["schemaVersion"] == "mdi-ci-provenance/1.0"
    for action in lock["actions"]:
        assert FULL_SHA.fullmatch(action["commit"])
        assert (
            f"{action['repository']}@{action['commit']}"
            in workflow_source
        )
    for image in lock["images"]:
        assert DIGEST.fullmatch(image["digest"])
        assert (
            f"{image['image']}:{image['tag']}@{image['digest']}"
            in workflow_source
        )


def test_workflow_has_no_floating_action_or_service_image_reference() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")

    assert not re.search(r"^\s*uses:\s*[^@\s]+@v\d", source, re.MULTILINE)
    assert not re.search(
        r"^\s*image:\s*[^\s@]+:(?:latest|[^@\s]+)\s*$",
        source,
        re.MULTILINE,
    )
