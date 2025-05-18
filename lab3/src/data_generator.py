import pandas as pd
import numpy as np
from .utils.config import Config
import time
import requests

class DataGenerator:
    def __init__(self, n_samples=100_000):
        self.n_samples = n_samples
        
    def generate(self):
        np.random.seed(42)
        data = {
            "user_id": np.arange(self.n_samples),
            "age": np.random.randint(18, 65, self.n_samples),
            "income": np.random.normal(50000, 15000, self.n_samples).round(2),
            "city": np.random.choice(["NY", "LA", "Chicago", "Houston", "Phoenix"], self.n_samples),
            "last_purchase": pd.date_range("2020-01-01", periods=self.n_samples, freq="h"),
            "product_category": np.random.choice(["Electronics", "Clothing", "Home", "Books", "Sports"], self.n_samples),
            "satisfaction_score": np.random.randint(1, 6, self.n_samples)
        }
        df = pd.DataFrame(data)
        df.to_parquet(f"{Config.BRONZE_PATH}/raw_data.parquet")


if __name__ == "__main__":
    generator = DataGenerator()
    generator.generate()