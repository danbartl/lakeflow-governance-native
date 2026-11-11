"""Run only in the bronze-tests target's editor, on DBR 18.3+ without Connect."""

from pyspark.pipelines import testing
from verify import verify

test_spark = testing.test_spark


def mock_files(session, folder):
    source = session.conf.get("slice.source_path")
    assert source.endswith("/native_test_inputs/accounts"), "Use the bronze-tests target"
    fixture_root = session.conf.get("slice.fixture_path")
    assert fixture_root.startswith("/Workspace/")
    # Never fall back to the real source when the API/runtime is unavailable.
    testing.mock_cloud_path(session, source, f"{fixture_root}/{folder}")


def test_files_to_silver_and_restart(test_spark):
    mock_files(test_spark, "autoloader")
    pipeline = testing.TestPipeline.active()
    for _ in range(2):
        status = pipeline.run(
            test_spark, {"accounts_current", "accounts_history", "accounts_quarantine"}
        )
        assert status.is_success, status.error_message
        verify(test_spark, "after_02")
        files = {
            row.source_file.rsplit("/", 1)[-1]
            for row in test_spark.table("accounts_bronze")
            .select("source_file")
            .distinct()
            .collect()
        }
        assert files == {"01.csv", "02.csv"}
        assert dict(test_spark.table("accounts_bronze").dtypes)["amount"] == "bigint"


def test_malformed_csv_fails_instead_of_disappearing(test_spark):
    mock_files(test_spark, "malformed")
    status = testing.TestPipeline.active().run(test_spark, {"accounts_bronze"})
    assert not status.is_success, "FAILFAST must reject the invalid BIGINT"
    diagnostic = f"{status.error_class} {status.error_message}".upper()
    assert any(code in diagnostic for code in ("MALFORMED", "CAST_INVALID_INPUT")), diagnostic
