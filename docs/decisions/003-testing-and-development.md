# ADR 003: Native Behavioral Qualification

Status: accepted, 2026-11-11.

Local pytest tests configuration and pure utilities without Spark startup. Native
pipeline Test assets exercise ingestion, Expectations and AUTO CDC. Native tests
are excluded from local collection explicitly, not counted as passing via mocks.

Silver tests use synthetic input with independently specified expected histories.
Quality tests assert completeness and disjointness of valid/quarantine partitions,
including SQL NULL behavior. Bronze tests exercise actual ingestion separately.
Replay and rewind are distinct checks; a successful retry is not proof of recovery.

Use bundle deployment to establish a sandbox, then bundle sync for source iterations
and the native editor to execute Test assets. Changes to resources or configuration
still require deployment. Databricks Connect is not a substitute for the managed
pipeline engine. No local speed claim is made for native execution.

Preview features are acceptable, but capability availability and actual results
must be recorded. Native failures must not be hidden by compatibility mocks.
