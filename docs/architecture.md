# Architecture

## Implemented Flow

```text
immutable CSV deliveries in a Unity Catalog volume
  -> Auto Loader -> accounts_bronze (source_file, ingested_at)
  -> valid events / complementary quarantine
  -> native AUTO CDC -> accounts_current (SCD1), accounts_history (SCD2)
```

`pipelines/first_slice` owns configuration, registration, fixtures and tests.
`monitoring` owns scoped event-log queries and dashboard generation.
`semantics` owns explicit semantic-page publication. Neither utility is a prerequisite
for data ingestion. There is no shared orchestration framework between them.

The JSON configuration is deliberately specific to this slice. Schema, validity
predicate and responsibility metadata are versioned together in Git. A canonical
SHA-256 fingerprint is published as a table property. This property is mutable:
it identifies configuration but is not an immutable execution audit record.

Native Lakeflow owns state, checkpointing and CDC semantics. Our code owns business
configuration, routing policy, expected results and operational guardrails.
Schema evolution is disabled for the first slice. Invalid business events go to
quarantine; malformed source parsing is a separate ingestion failure scenario.

## Boundaries

Only development/sandbox targets exist. There are no production deployment gates,
complete bank-wide data contracts, column-level CDE classification, correction app,
or end-to-end immutable evidence store yet. Table properties are not Unity Catalog
governed tags, access control or proof of regulatory compliance.

Source data retention, Delta retention and checkpoint retention must be designed
together before replay or rewind becomes an operational promise. SCD2 sequence
history is not automatically bitemporal history.

The existing serverless pipeline design supersedes the earlier blanket requirement
for cert/prod job clusters for this slice. Pipeline compute and Jobs compute are
different resources. Cert/prod policy, isolation and cost controls still require
an explicit deployment decision before those targets are introduced.

## Design Review Outcome

The small native slice is internally coherent and easier to qualify than two mirrored
engines. Its largest remaining risk is unverified runtime behavior, not a shortage
of abstractions. Do not generalize registration or add a metadata execution engine
until a second real dataset demonstrates a repeated need.
