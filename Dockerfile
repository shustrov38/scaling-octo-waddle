FROM python:3.9-slim

# Install supervisor and other system dependencies
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file and install dependencies if available
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt provided"

# Copy the entire project into the container
COPY . /app

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD [ "supervisord", "-n" ]
