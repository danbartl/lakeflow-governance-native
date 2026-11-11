"""Run with the pipeline's catalog/schema selected in a Databricks notebook."""

import json
from pathlib import Path


def verify(spark, stage):
    expected = json.loads(
        Path(__file__).with_name("fixtures").joinpath("expected.json").read_text()
    )[stage]
    for table, key in (
        ("accounts_bronze", "bronze_count"),
        ("accounts_quarantine", "quarantine_count"),
    ):
        assert spark.table(table).count() == expected[key], table
    for table, key, columns, order in (
        ("accounts_current", "current", ["account_id", "amount"], ["account_id"]),
        (
            "accounts_history",
            "history",
            ["account_id", "amount", "__START_AT", "__END_AT"],
            ["account_id", "__START_AT"],
        ),
    ):
        actual = spark.table(table).select(*columns).orderBy(*order)
        assert [list(row) for row in actual.collect()] == expected[key], table
    assert (
        spark.sql(
            "SELECT count(*) FROM accounts_bronze "
            "WHERE source_file IS NULL OR source_file = '' OR ingested_at IS NULL"
        ).first()[0]
        == 0
    ), "Missing source provenance"
    return {"stage": stage, "status": "passed", "scope": "native_fixture_only"}
