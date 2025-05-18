from pyspark.sql.functions import when, col, to_date, count, avg
from .utils.spark_session import get_spark_session
from .utils.config import Config

class ETLPipeline:
    def __init__(self):
        self.spark = get_spark_session()
        
    def run(self):
        self._bronze_layer()
        self._silver_layer()
        self._gold_layer()
        
    def _bronze_layer(self):
        df = self.spark.read.parquet(f"{Config.BRONZE_PATH}/raw_data.parquet")
        df.write.format("delta").mode("overwrite").save(Config.BRONZE_PATH)
        
    def _silver_layer(self):
        df = self.spark.read.format("delta").load(Config.BRONZE_PATH)
        
        silver_df = (df
            .withColumn("age", col("age").cast("integer"))
            .withColumn("income", when(col("income") < 0, 0).otherwise(col("income")))
            .withColumn("purchase_date", to_date("last_purchase"))
            .drop("last_purchase")
            .dropDuplicates(["user_id"])
            .fillna({"product_category": "Unknown", "satisfaction_score": 3})
        )
        
        silver_df.write.format("delta").mode("overwrite").save(Config.SILVER_PATH)
        
    def _gold_layer(self):
        silver_df = self.spark.read.format("delta").load(Config.SILVER_PATH)
        
        gold_df = (silver_df
            .groupBy("city", "product_category")
            .agg(
                count("user_id").alias("total_customers"),
                avg("income").alias("average_income"),
                avg("satisfaction_score").alias("avg_satisfaction")
            )
            .withColumnRenamed("product_category", "category")
        )
        
        gold_df.write.format("delta").mode("overwrite").save(Config.GOLD_PATH)
        self.spark.sql(f"OPTIMIZE delta.`{Config.GOLD_PATH}` ZORDER BY (city)")


if __name__ == "__main__":
    etl = ETLPipeline()
    etl.run()