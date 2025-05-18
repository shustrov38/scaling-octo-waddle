FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=node:node --chmod=600 src/ /app/src/
COPY scripts/ /app/scripts/

RUN mkdir /app/data/
RUN mkdir /app/data/bronze/
RUN mkdir /app/data/silver/
RUN mkdir /app/data/gold/

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Make entrypoint script executable
RUN chmod +x /app/scripts/entrypoint.sh

ENTRYPOINT ["/app/scripts/entrypoint.sh"]