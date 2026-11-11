"""Shared configuration, with no pipeline registration or data access."""

import hashlib
import json
from pathlib import Path


def load_config(path=None):
    path = Path(path) if path is not None else Path(__file__).with_name("dataset.json")
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {"dataset", "domain", "source_system", "contract_version", "schema", "valid_sql"}
    if (
        not isinstance(config, dict)
        or set(config) != required
        or not all(isinstance(v, str) and v.strip() for v in config.values())
    ):
        raise ValueError("Dataset configuration requires exactly the mandatory nonempty strings")
    if config["dataset"] != "accounts":
        raise ValueError("This slice supports only accounts")
    return config


def contract_fingerprint(config):
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def table_properties(config, owner):
    if not isinstance(owner, str) or not owner.strip():
        raise ValueError("An accountable owner is required")
    return {
        f"governance.{key}": value
        for key, value in {
            "owner": owner,
            "domain": config["domain"],
            "source_system": config["source_system"],
            "contract_version": config["contract_version"],
            "contract_sha256": contract_fingerprint(config),
        }.items()
    }
