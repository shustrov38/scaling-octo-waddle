FROM python:3.10-slim

# Install supervisor and other system dependencies
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire project into the container
COPY . /app

# install dependencies if available
RUN pip install --no-cache-dir -r /app/requirements.txt || echo "No requirements.txt provided"

RUN mkdir /app/logs
RUN touch /app/logs/application.err.log
RUN touch /app/logs/application.out.log
RUN touch /app/logs/data_collector.err.log
RUN touch /app/logs/data_collector.out.log
RUN touch /app/logs/model_processor.err.log
RUN touch /app/logs/model_processor.out.log

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD [ "supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
