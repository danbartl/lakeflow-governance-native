# ADR 004: Small Components and Explicit Qualification Gates

Status: accepted for development, 2026-11-11.

Keep ingestion, monitoring and semantic publication independently understandable,
with co-located tests. Use native capabilities before adding DQX or a custom service.
The CLI is pinned across bundles and CI; Python dependencies are locked.

Monitoring is scoped to explicit workspace and pipeline identifiers. Missing events
are not a successful quality assessment. Semantic publication is a separate,
explicit operation with dry-run behavior; it is not a data-release approval.

Before cert/prod, qualify native tests, least-privilege identities, resource policies,
retention/recovery, release evidence and observability. Do not infer certification
from BCBS 239-oriented design intent. Preview acceptance does not waive these gates.
