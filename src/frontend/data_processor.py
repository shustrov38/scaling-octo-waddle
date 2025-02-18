from common.kafka_producer import KafkaProducer
from common.kafka_consumer import KafkaConsumer

from common.configuration import (
    TOPIC_RAW_DATA,
    PRODUCER_CONFIG,
    CONSUMER_CONFIG_RAW_DATA,
    TOPIC_DATA,
)

from pathlib import Path
import pandas as pd
import logging
import pickle
import json


class DataPreprocessor:
    def __init__(self, preproc_model_path: str | Path):
        self.preproc_model_path = preproc_model_path

        self.consumer_config = CONSUMER_CONFIG_RAW_DATA
        self.producer_config = PRODUCER_CONFIG
        self.input_topic = TOPIC_RAW_DATA
        self.output_topic = TOPIC_DATA

        self.logger = logging.getLogger(self.__class__.__name__)
        
        self._load_preprocessor()
        self._init_consumer()
        self._init_producer()

    def _load_preprocessor(self):
        try:
            with open(self.preproc_model_path, 'rb') as f:
                self.preprocessor = pickle.load(f)
            self.logger.info(f"Preprocessor loaded from {self.preproc_model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load preprocessor: {e}")
            raise

    def _init_consumer(self):
        self.consumer = KafkaConsumer(
            self.consumer_config,
            value_deserializer=lambda x: json.loads(x)
        )
        self.consumer.subscribe([self.input_topic])
        self.logger.info(f"Subscribed to {self.input_topic}")

    def _init_producer(self):
        self.producer = KafkaProducer(self.producer_config)
        self.logger.info(f"Producer initialized for {self.output_topic}")

    def _process_message(self, message):
        try:
            value = message['value']
            data = pd.DataFrame.from_dict(value, orient='index').T
            processed = self.preprocessor.transform(data).tolist()
            return {'raw': value, 'data': processed}
        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return None

    def _send_processed_data(self, data):
        try:
            self.producer.produce(
                topic=self.output_topic,
                value=json.dumps(data),
                key='processed',
            )
        except Exception as e:
            self.logger.error(f"Failed to send data: {e}")

    def run(self):
        try:
            while True:
                message = self.consumer.consume()
                processed = self._process_message(message)
                if processed:
                    self._send_processed_data(processed)

        except KeyboardInterrupt:
            self.logger.info("Shutting down preprocessor")
        finally:
            self.shutdown()

    def shutdown(self):
        self.logger.info("Closing resources")
        self.consumer.close()
        self.producer.flush()
