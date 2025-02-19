from common.kafka_producer import KafkaProducer
from common.kafka_consumer import KafkaConsumer

from common.configuration import (
    TOPIC_DATA,
    CONSUMER_CONFIG_DATA,
    PRODUCER_CONFIG_1 as PRODUCER_CONFIG,
    TOPIC_RESULT
)

from pathlib import Path
import numpy as np
import pickle
import json
import logging
import sys

class KafkaModelProcessor:
    def __init__(self, model_path: str | Path):
        
        self.model_path = Path(model_path)
        self.consumer_config = CONSUMER_CONFIG_DATA
        self.producer_config = PRODUCER_CONFIG
        self.input_topic = TOPIC_DATA
        self.output_topic = TOPIC_RESULT
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self._load_model()
        self._init_consumer()
        self._init_producer()

    def _load_model(self):
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.logger.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
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

    def _process_message(self, message: dict):
        try:
            value = message['value']
            data = np.array(value['data']).reshape(1, -1)
            
            self.logger.debug(f"Processing data: {data.tolist()}")
            prediction = self.model.predict(data).tolist()
            
            return {
                'quality': prediction[0],
                'raw': value['raw']
            }
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return None

    def _send_result(self, result):
        try:
            self.producer.produce(
                topic=self.output_topic,
                key='result',
                value=json.dumps(result),
            )
        except Exception as e:
            self.logger.error(f"Failed to send result: {e}")

    def run(self):
        try:
            while True:
                message =self.consumer.consume()
                result = self._process_message(message)
                if result:
                    self._send_result(result)

        except KeyboardInterrupt:
            self.logger.info("Shutting down by user request")
        finally:
            self.shutdown()

    def shutdown(self):
        self.logger.info("Closing resources...")
        self.consumer.close()
        self.producer.flush()
        self.logger.info("Resources closed")
