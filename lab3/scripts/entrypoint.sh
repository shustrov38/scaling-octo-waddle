#!/bin/bash

# Step 1: Generate data
echo "Generating sample data..."
python -m src.data_generator

# Step 2: Run ETL pipeline
echo "Running ETL pipeline..."
python -m src.etl_pipeline

# Step 3: Train model
echo "Training ML model..."
python -m src.model_trainer

# Keep container running (optional)
tail -f /dev/null