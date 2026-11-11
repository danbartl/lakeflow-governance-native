# ADR 002: Versioned Configuration, Explicit Evidence Gaps

Status: accepted, 2026-11-11.

Keep configuration and independent expected results in Git. Publish a deterministic
configuration fingerprint with table metadata. Never resolve a production release
through an unpinned 'latest' metadata row.

A future release record must bind Git commit, contract fingerprint, dependency lock,
pipeline/update identifiers, runtime/channel, input identities and result evidence.
Record that association per execution; mutable table properties are insufficient.
The fingerprint covers configuration, not source code or delivered file content.

Require immutable delivery identities before accepting replacement files, controlled
reprocessing or manual corrections. Corrections must become governed new inputs,
not arbitrary edits to current or history tables. Approval, segregation of duties,
retention and access controls are pending work, not existing capabilities.
