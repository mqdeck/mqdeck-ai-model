import re
from pathlib import Path

from pipeline.classify import filter_by_license
from pipeline.io import read_yaml
from pipeline.normalize import discover_custom

ROOT = Path(__file__).resolve().parents[1]


def test_default_build_is_public_and_remote_collection_is_disabled() -> None:
    policy = read_yaml(ROOT / "config" / "source_policy.yaml")["build"]
    assert policy["profile"] == "public"
    assert policy["remote_collection_enabled"] is False
    assert policy["allowed_license_ids"]["public"] == ["MIT"]
    assert set(policy["allowed_license_ids"]) == {"public"}


def test_bundled_corpus_passes_commercial_source_policy() -> None:
    documents = discover_custom(ROOT / "custom")
    included, decisions = filter_by_license(documents, {"public"}, {"MIT"})
    assert len(included) == len(documents)
    assert all(decision.included for decision in decisions)
    assert all(document.source_url is None for document in included)


def test_default_base_model_has_permissive_release_metadata() -> None:
    base = read_yaml(ROOT / "config" / "model.yaml")["base_model"]
    assert base["license_id"] == "Apache-2.0"
    assert len(base["revision"]) == 40
    assert base["revision"] != "main"
    assert base["commercial_use_confirmed"] is True
    assert base["redistribution_confirmed"] is True
    assert base["license_url"].startswith("https://huggingface.co/")
    assert base["revision"] in base["license_download_url"]
    assert re.fullmatch(r"[0-9a-f]{64}", base["license_sha256"])
