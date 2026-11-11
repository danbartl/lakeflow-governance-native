"""Sandbox vertical slice. No compiler, framework runtime, or custom CDC engine."""

from pyspark import pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from settings import load_config, table_properties

spark = SparkSession.active()
config = load_config()
properties = table_properties(config, spark.conf.get("slice.owner"))


@dp.table(name="accounts_quarantine", table_properties=properties)
def accounts_quarantine():
    return spark.readStream.table("accounts_bronze").where(
        ~F.coalesce(F.expr(config["valid_sql"]), F.lit(False))
    )


@dp.table(name="accounts_valid", table_properties=properties)
@dp.expect_all_or_drop({"valid_account_event": config["valid_sql"]})
def accounts_valid():
    return spark.readStream.table("accounts_bronze")


# Both targets consume exactly the same validated event stream.
for target, scd_type in (("accounts_current", 1), ("accounts_history", 2)):
    dp.create_streaming_table(name=target, table_properties=properties, cluster_by_auto=True)
    dp.create_auto_cdc_flow(
        name=f"{target}_cdc",
        target=target,
        source="accounts_valid",
        keys=["account_id"],
        sequence_by=F.col("sequence"),
        apply_as_deletes=F.expr("operation = 'DELETE'"),
        column_list=["account_id", "amount"],
        stored_as_scd_type=scd_type,
    )
