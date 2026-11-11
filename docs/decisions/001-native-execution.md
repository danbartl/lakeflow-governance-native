# ADR 001: Native Execution Without SDP-META

Status: accepted, 2026-11-11.

Use native Lakeflow Declarative Pipelines, Expectations and AUTO CDC directly.
Keep registration thin and dataset-specific. Do not implement a second CDC engine
in Polars, DuckDB, Narwhals or delta-rs. Do not add SDP-META as a dependency or vendor
its source. The [evaluation](../research/sdp-meta.md) records the rationale.

This reduces the number of semantics we must maintain. It does not eliminate native
testing, nor prove that our own quarantine or CDC behavior is correct.

Reconsider SDP-META only when repeated onboarding patterns outweigh adapter costs,
required routing/sequence behavior passes native qualification, release pinning is
defined, and ownership of upstream gaps is accepted. Labs status alone is not a veto.

Cost: more dataset-specific registration today. This is intentional and preferable
to a general compiler before native behavior is established.
