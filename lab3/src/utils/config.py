class Config:
    BRONZE_PATH = "/app/data/bronze/"
    SILVER_PATH = "/app/data/silver/"
    GOLD_PATH = "/app/data/gold/"
    
    SPARK_MASTER = "spark://spark-master:7077"
    
    MLFLOW_TRACKING_URI = "http://mlflow:5000"
    MLFLOW_EXPERIMENT = "CustomerIncomePrediction"