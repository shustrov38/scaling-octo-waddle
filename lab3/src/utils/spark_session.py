from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession
from .config import Config

def get_spark_session():
    builder = (
        SparkSession.builder
        .master(Config.SPARK_MASTER)
        .appName("LakehousePipeline")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.executor.memory", "2g")
        .config("spark.driver.memory", "2g")
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()