# SDP-META Evaluation and Decision

Reviewed 2026-11-11 against upstream v0.1.1, commit
`2d652f610f725a5f9c70d113ddbe83ba6fd40267`.
The decision is to continue without SDP-META, not to rule it out permanently.

## Fit

Metadata-driven onboarding is attractive for many similar sources and standard
Bronze/Silver patterns. It could reduce repeated registration code. It does not
replace governance ownership, manual correction approvals or immutable release evidence.

## Findings

- In `write_layer_with_dqe`, a quarantine-only positive predicate was applied as a
  quarantine drop predicate, while the main writer lacked the complementary drop
  rule. An isolated registration inspection confirmed this wiring, not Spark output.
- AUTO CDC registration uses `where` and `flow_name`; compatibility with the current
  native API requires runtime verification, not assumptions from similar names.
- Composite sequencing and generated start/end field types require explicit tests.
- Runtime selection of latest specifications and onboarding MERGE behavior do not
  by themselves provide immutable, pinned release specifications.
- Required advanced CDC arguments and combined patterns need capability checks.

These are version-specific observations, not claims about all future releases.
No Databricks execution was available, so static inspection is not runtime proof.
Our direct implementation must pass the same behavioral checks.

## Sources

- [Pinned pipeline implementation](https://github.com/databrickslabs/sdp-meta/blob/2d652f610f725a5f9c70d113ddbe83ba6fd40267/src/databricks/labs/sdp_meta/dataflow_pipeline.py)
- [Upstream project](https://github.com/databrickslabs/sdp-meta)
- [Native AUTO CDC Python API](https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-apply-changes)

Keep adapters out of the runtime until a concrete onboarding benefit, passing native
tests and maintenance ownership justify the additional dependency.
