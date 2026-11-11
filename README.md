# Lakeflow Governance Native

A small, Databricks-native qualification slice for governed data engineering.
This is a development baseline, not a production framework or a certification of
BCBS 239 compliance. Native runtime behavior still requires Databricks qualification.

## Included

- CSV Auto Loader Bronze ingestion with source-file provenance.
- Native Expectations, complementary quarantine, AUTO CDC SCD1 and SCD2.
- Synthetic fixtures, independent expected results and native pipeline tests.
- Scoped quality monitoring and an explicit semantic-page publishing utility.
- Direct-engine bundles with a pinned CLI, separate development and test targets.

There is no SDP-META dependency, local Spark substitute, generated pipeline compiler,
or parallel Polars implementation. Tests live with their respective components.

## Local Checks

```sh
uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

These commands check configuration and utilities, not AUTO CDC execution.
See [native development](pipelines/first_slice/README.md) for deployment and native tests.

## Documentation

- [Architecture](docs/architecture.md)
- [Decisions](docs/decisions/README.md)
- [Testing and handover](docs/testing.md)
- [Roadmap](docs/roadmap.md)
- [SDP-META evaluation](docs/research/sdp-meta.md)
- [Publication checklist](docs/publication.md)
- [Monitoring](monitoring/README.md) and [semantics](semantics/README.md)

This repository is a curated snapshot with new history. Historical prototypes and
unrelated documents are intentionally not part of this baseline.
