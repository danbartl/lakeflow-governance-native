"""File ingestion shared by the integration pipeline and native Bronze tests."""

from pyspark import pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from settings import load_config, table_properties

spark = SparkSession.active()
config = load_config()
source_path = spark.conf.get("slice.source_path")
if not source_path.startswith("/Volumes/"):
    raise ValueError("A dedicated UC volume path is required")


@dp.table(
    name="accounts_bronze", table_properties=table_properties(config, spark.conf.get("slice.owner"))
)
def accounts_bronze():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("mode", "FAILFAST")
        .option("cloudFiles.schemaEvolutionMode", "none")
        .schema(config["schema"])
        .load(source_path)
        .select("*", F.col("_metadata.file_path").alias("source_file"))
        .withColumn("ingested_at", F.current_timestamp())
    )
