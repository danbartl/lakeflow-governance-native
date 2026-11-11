"""Local checks validate configuration only, not a second execution engine."""

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("slice_settings", ROOT / "settings.py")
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)


def test_config_and_metadata():
    config = settings.load_config()
    assert settings.table_properties(config, "risk_team")["governance.owner"] == "risk_team"


def test_missing_owner_rejected():
    with pytest.raises(ValueError, match="owner"):
        settings.table_properties(settings.load_config(), " ")


def test_deployment_toolchain_is_consistent():
    repository = ROOT.parents[1]
    workflow = yaml.safe_load((repository / ".github/workflows/ci.yml").read_text())
    cli_steps = [
        step
        for job in workflow["jobs"].values()
        for step in job["steps"]
        if step.get("uses", "").startswith("databricks/setup-cli@")
    ]
    assert len(cli_steps) == 1
    version = cli_steps[0]["with"]["version"]
    for directory in (ROOT, repository / "monitoring"):
        bundle = yaml.safe_load((directory / "databricks.yml").read_text())["bundle"]
        assert bundle["engine"] == "direct"
        assert bundle["databricks_cli_version"] == f">= {version}, <= {version}"


def test_contract_fingerprint_is_stable_and_content_sensitive():
    config = settings.load_config()
    assert settings.contract_fingerprint(config) == settings.contract_fingerprint(
        dict(reversed(list(config.items())))
    )
    assert settings.contract_fingerprint(config) != settings.contract_fingerprint(
        config | {"valid_sql": "TRUE"}
    )


def test_bronze_target_uses_only_synthetic_fixture_path():
    bundle = yaml.safe_load((ROOT / "databricks.yml").read_text())
    pipeline = bundle["targets"]["bronze-tests"]["resources"]["pipelines"]["accounts"]
    assert pipeline["configuration"]["slice.source_path"].endswith("/native_test_inputs/accounts")
    assert pipeline["configuration"]["slice.fixture_path"] == "${workspace.file_path}/fixtures"
    assert pipeline["channel"] == "PREVIEW"
    for name in ("01.csv", "02.csv"):
        assert (ROOT / "fixtures/autoloader" / name).read_text() == (
            ROOT / "fixtures" / name
        ).read_text()
    assert {p.suffix for p in (ROOT / "fixtures/autoloader").iterdir()} == {".csv"}


def test_recovery_is_separate_from_default_and_unit_targets():
    bundle = yaml.safe_load((ROOT / "databricks.yml").read_text())
    recovery = bundle["targets"]["recovery"]["resources"]["pipelines"]["accounts"]
    assert recovery["configuration"]["pipelines.rewind.betaEnabled"] == "true"
    assert recovery["channel"] == "PREVIEW"
    assert (
        "pipelines.rewind.betaEnabled"
        not in bundle["resources"]["pipelines"]["accounts"]["configuration"]
    )


def test_native_target_excludes_file_ingestion():
    bundle = yaml.safe_load((ROOT / "databricks.yml").read_text())
    pattern = bundle["targets"]["native-tests"]["variables"]["pipeline_sources"]
    assert [path.name for path in ROOT.glob(pattern)] == ["pipeline.py"]
    libraries = bundle["resources"]["pipelines"]["accounts"]["libraries"]
    assert libraries == [{"glob": {"include": "${var.pipeline_sources}"}}]


@pytest.mark.parametrize("invalid", [None, [], "accounts", {"dataset": "accounts"}])
def test_malformed_config_rejected(tmp_path, invalid):
    path = tmp_path / "dataset.json"
    path.write_text(json.dumps(invalid))
    with pytest.raises(ValueError, match="mandatory"):
        settings.load_config(path)


@pytest.mark.parametrize("change", [{"domain": " "}, {"schema": 42}, {"unknown": "value"}])
def test_invalid_fields_rejected(tmp_path, change):
    path = tmp_path / "dataset.json"
    path.write_text(json.dumps(settings.load_config() | change))
    with pytest.raises(ValueError, match="mandatory"):
        settings.load_config(path)
