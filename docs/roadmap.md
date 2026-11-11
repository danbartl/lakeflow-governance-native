# Next Increments

## First: Prove the Existing Slice

- Execute native tests and record real failures before further abstraction.
- Qualify retention and rewind, parser failures and schema mismatch handling.
- Add native cases for conflicting equal sequences, composite sequence types,
  null keys, deletes followed by reinsertion and changed replay payloads.
- Decide delivery identity and fail-closed handling of conflicting source events.

## Then: Governed Production Baseline

- Per-update release evidence and immutable input manifests.
- Explicit dev/cert/prod identities, approvals, isolation and compute policies.
- Bank contracts, CDE ownership and governed tags down to columns.
- Access controls, audit retention, failure alerts and recovery objectives.
- ZIP/Excel ingestion adapters only with agreed parser and provenance contracts.

## Later: Extend Only for Concrete Requirements

- Bitemporality with separate business/system time and independent native tests.
- Correction/release-selection app that submits governed inputs and approvals.
- DQX where native Expectations demonstrably do not cover required checks.
- Business lineage, metric semantics and richer semantic publication workflows.
- Metadata-driven onboarding, including reconsideration of SDP-META if justified.

No item in this roadmap should be read as already implemented.
