import mlflow
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.regression import RandomForestRegressor
from .utils.spark_session import get_spark_session
from .utils.config import Config

class ModelTrainer:
    def __init__(self):
        self.spark = get_spark_session()
        mlflow.set_tracking_uri(Config.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(Config.MLFLOW_EXPERIMENT)
        
    def train(self):
        df = self.spark.read.format("delta").load(Config.GOLD_PATH)
        
        indexer = StringIndexer(inputCols=["city", "category"], 
                              outputCols=["city_idx", "category_idx"])
        assembler = VectorAssembler(
            inputCols=["city_idx", "category_idx", "total_customers"],
            outputCol="features"
        )
        
        rf = RandomForestRegressor(
            labelCol="average_income",
            numTrees=50,
            maxDepth=5,
            seed=42
        )
        
        pipeline = Pipeline(stages=[indexer, assembler, rf])
        
        with mlflow.start_run():
            model = pipeline.fit(df)
            
            predictions = model.transform(df)
            
            mlflow.log_params({
                "num_trees": 50,
                "max_depth": 5
            })
            
            mlflow.spark.log_model(model, "model")
            
            self._log_metrics(predictions)
            
    def _log_metrics(self, predictions):
        from pyspark.ml.evaluation import RegressionEvaluator
        evaluator = RegressionEvaluator(labelCol="average_income")
        
        metrics = {
            "rmse": evaluator.evaluate(predictions, {evaluator.metricName: "rmse"}),
            "r2": evaluator.evaluate(predictions, {evaluator.metricName: "r2"})
        }
        
        mlflow.log_metrics(metrics)
        print(f"Logged metrics: {metrics}")


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train()