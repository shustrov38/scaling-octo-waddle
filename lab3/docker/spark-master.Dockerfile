FROM openjdk:11-jdk-slim

ARG SPARK_VERSION=3.5.0
ARG HADOOP_VERSION=3

RUN apt-get update && apt-get install -y curl procps

# Download and install Spark
RUN curl -L https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz | tar xz -C /opt \
    && ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

# Install Delta Lake
RUN curl -L --output /opt/spark/jars/delta-core_2.12-2.4.0.jar \
    https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar

WORKDIR /opt/spark
ENV SPARK_MASTER_PORT 7077
ENV SPARK_MASTER_WEBUI_PORT 8080

CMD ["/opt/spark/bin/spark-class", "org.apache.spark.deploy.master.Master"]