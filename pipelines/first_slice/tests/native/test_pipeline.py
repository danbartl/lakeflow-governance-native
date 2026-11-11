"""Run only as a Test asset in the native-tests pipeline's web editor."""

from pyspark.pipelines import testing

test_spark = testing.test_spark


def run_outputs(session):
    pipeline = testing.TestPipeline.active()
    status = pipeline.run(
        session,
        {
            "accounts_valid",
            "accounts_quarantine",
            "accounts_current",
            "accounts_history",
        },
    )
    assert status.is_success, status.error_message
    return status


def seed(session, rows, mode="error"):
    session.createDataFrame(
        rows, "account_id STRING, amount BIGINT, sequence BIGINT, operation STRING"
    ).write.format("delta").mode(mode).saveAsTable("accounts_bronze")


def current(session):
    assert dict(session.table("accounts_current").dtypes) == {
        "account_id": "string",
        "amount": "bigint",
    }
    return [
        tuple(row)
        for row in session.table("accounts_current")
        .select("account_id", "amount")
        .orderBy("account_id")
        .collect()
    ]


def history(session):
    assert dict(session.table("accounts_history").dtypes) == {
        "account_id": "string",
        "amount": "bigint",
        "__START_AT": "bigint",
        "__END_AT": "bigint",
    }
    return [
        tuple(row)
        for row in session.table("accounts_history")
        .select("account_id", "amount", "__START_AT", "__END_AT")
        .orderBy("account_id", "__START_AT")
        .collect()
    ]


def test_updates_deletes_late_events_replay_and_restart(test_spark):
    seed(test_spark, [("A", 100, 10, "UPSERT"), ("B", 200, 10, "UPSERT")])
    run_outputs(test_spark)
    assert current(test_spark) == [("A", 100), ("B", 200)]
    seed(test_spark, [("A", 120, 30, "UPSERT"), ("B", None, 40, "DELETE")], "append")
    run_outputs(test_spark)
    seed(test_spark, [("A", 110, 20, "UPSERT")], "append")
    run_outputs(test_spark)
    expected = [("A", 100, 10, 20), ("A", 110, 20, 30), ("A", 120, 30, None), ("B", 200, 10, 40)]
    assert current(test_spark) == [("A", 120)]
    assert history(test_spark) == expected
    seed(test_spark, [("A", 120, 30, "UPSERT")], "append")
    run_outputs(test_spark)
    assert current(test_spark) == [("A", 120)]
    assert history(test_spark) == expected
    run_outputs(test_spark)
    assert current(test_spark) == [("A", 120)]
    assert history(test_spark) == expected


def test_expectations_and_quarantine(test_spark):
    seed(
        test_spark,
        [
            ("OK", 0, 1, "UPSERT"),
            ("NEG", -1, 1, "UPSERT"),
            ("NULL", None, 1, "UPSERT"),
            (None, 100, 1, "UPSERT"),
            (" ", 100, 1, "UPSERT"),
            ("SEQ", 100, None, "UPSERT"),
            ("OP", 100, 1, "UNKNOWN"),
            ("NO_OP", 100, 1, None),
        ],
    )
    status = run_outputs(test_spark)
    assert current(test_spark) == [("OK", 0)]
    assert test_spark.table("accounts_valid").count() == 1
    assert test_spark.table("accounts_quarantine").count() == 7
    columns = ["account_id", "amount", "sequence", "operation"]
    bronze = test_spark.table("accounts_bronze").select(*columns)
    valid = test_spark.table("accounts_valid").select(*columns)
    quarantine = test_spark.table("accounts_quarantine").select(*columns)
    partition = valid.unionByName(quarantine)
    assert partition.exceptAll(bronze).count() == 0
    assert bronze.exceptAll(partition).count() == 0
    assert valid.intersectAll(quarantine).count() == 0
    assert status.flow_info["accounts_valid"].records_written == 1
    assert status.flow_info["accounts_quarantine"].records_written == 7
