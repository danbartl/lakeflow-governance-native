# Testing and Handover

## Local

Run the README commands. These cover configuration validation and fingerprinting,
bundle consistency, monitoring generation and semantic publication request behavior.
They do not execute Spark, AUTO CDC or the remote publication API.

## Databricks Qualification

1. Use a dedicated sandbox catalog/schema and synthetic source volume.
2. Follow the [slice setup](../pipelines/first_slice/README.md).
3. Run [native Silver tests](../pipelines/first_slice/tests/native/README.md):
   exact SCD1/SCD2 outputs, late events, deletes, replay, quality partition.
4. Run native Bronze tests with mocked cloud paths, including malformed input.
5. Follow [recovery](../pipelines/first_slice/recovery.md) separately.
6. Render the monitoring dashboard and verify its scope and no-events behavior.
7. Exercise semantic publication in an isolated domain; check create/update guards.

Record commit, lockfile, CLI, workspace capabilities, pipeline/update IDs, test
results and any deviations. No Databricks credentials were available during snapshot
preparation: all native/runtime/dashboard-rendering checks remain unqualified.

Do not point test assets at existing production datasets. Check bundle identity and
deployment state before using an existing workspace: a new Git repository does not
automatically create isolated Databricks resources.
