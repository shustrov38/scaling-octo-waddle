from argparse import ArgumentParser
from pyspark.sql import SparkSession
from pyspark import SparkContext
from pyspark.sql import functions as F
from pyspark.ml.feature import RobustScaler, VectorAssembler
from pyspark.sql.functions import udf
from pyspark.ml.linalg import VectorUDT
from pyspark.sql.types import DoubleType
from pyspark import StorageLevel
import psutil
import time
from typing import List


class DataProcessor:
    def __init__(self, data_path: str, optimized: bool = False):
        self.data_path = data_path
        self.optimized = optimized
        self.spark = self._initialize_spark()
        self.start_time = time.time()
        
    def _initialize_spark(self) -> SparkSession:
        """Initialize and configure Spark session."""
        if SparkContext._active_spark_context is not None:
            sc = SparkContext.getOrCreate()
            sc.stop()
            
        spark = SparkSession.builder \
            .appName("BigDataLab") \
            .getOrCreate()
            
        spark.sparkContext.setLogLevel("ERROR")
        return spark

    def _log_memory_usage(self, stage: str) -> None:
        """Log memory usage at different stages."""
        print(f"{stage} RAM usage: {psutil.virtual_memory().percent}%")

    def _log_timer(self, stage: str, start_time: float) -> float:
        """Helper method to log time taken for a stage."""
        elapsed = time.time() - start_time
        print(f"[Timer] {stage}: {elapsed:.3f} sec")
        return elapsed

    def _load_data(self) -> None:
        """Load and prepare the initial dataset."""
        load_start = time.time()
        self.df = self.spark.read.csv(self.data_path, header=True, inferSchema=True)
        self._log_timer("Data load", load_start)
        
        if self.optimized:
            self.df = self.df.repartition(self.spark.sparkContext.defaultParallelism)

    def _clean_data(self) -> None:
        """Remove unnecessary columns."""
        self.df = self.df.drop('nameOrig', 'nameDest')

    def _one_hot_encode(self) -> None:
        """Perform one-hot encoding on categorical columns."""
        encoding_start = time.time()
        
        # Get distinct categories
        categories = [row["type"] for row in self.df.select("type").distinct().collect()]
        
        # Create one-hot encoded columns
        for category in categories:
            self.df = self.df.withColumn(
                f"type_{category}", 
                F.when(F.col("type") == category, 1).otherwise(0)
            )
        
        self.df = self.df.drop('type')
        self._log_timer("Encoding", encoding_start)

    def _prepare_for_scaling(self) -> None:
        """Cache the dataframe if optimization is enabled."""
        self.scaled_df = self.df.persist(StorageLevel.MEMORY_AND_DISK) if self.optimized else self.df
        if self.optimized:
            self.scaled_df.count()  # Force persistence

    def _scale_features(self) -> None:
        """Scale numerical features using RobustScaler."""
        scaling_start = time.time()
        
        # UDF to convert vector to double
        vector_to_double_udf = udf(lambda v: float(v[0]), DoubleType())
        
        columns_to_scale = [
            'amount', 'oldbalanceOrg', 'newbalanceOrig', 
            'oldbalanceDest', 'newbalanceDest'
        ]
        
        for col_name in columns_to_scale:
            # Create vector column
            assembler = VectorAssembler(inputCols=[col_name], outputCol=f"{col_name}_vector")
            self.scaled_df = assembler.transform(self.scaled_df)
            
            # Scale the feature
            scaler = RobustScaler(inputCol=f"{col_name}_vector", outputCol=f"{col_name}_scaled")
            scaler_model = scaler.fit(self.scaled_df)
            self.scaled_df = scaler_model.transform(self.scaled_df)
            
            # Convert vector to double
            self.scaled_df = self.scaled_df.withColumn(
                f"{col_name}_scaled", 
                vector_to_double_udf(self.scaled_df[f"{col_name}_scaled"])
            )
            
            # Clean up intermediate columns
            self.scaled_df = self.scaled_df.drop(f"{col_name}_vector", col_name)
            
        self._log_timer("Scaling", scaling_start)

    def process(self) -> None:
        """Execute the full data processing pipeline."""
        self._log_memory_usage("Initial")
        self._load_data()
        self._clean_data()
        self._one_hot_encode()
        self._prepare_for_scaling()
        self._scale_features()
        
        total_time = time.time() - self.start_time
        print(f"[Timer] Total execution time: {total_time:.2f} sec")
        self._log_memory_usage("Final")
        
        self.spark.stop()


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('--data-path', '-d', required=True, help="Path to input data file")
    parser.add_argument('--optimized', '-o', action='store_true', help="Enable optimization features")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    processor = DataProcessor(args.data_path, args.optimized)
    processor.process()