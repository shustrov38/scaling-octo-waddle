from common.kafka_producer import KafkaProducer

from common.configuration import (
    TOPIC_RAW_DATA,
    PRODUCER_CONFIG_1 as PRODUCER_CONFIG
)

from sklearn.model_selection import KFold

from pathlib import Path

import pandas as pd
import threading
import logging
import json
import time

class KafkaDatasetProducer:
    def __init__(self,
                 dataset_path: str | Path,
                 num_producers: int = 1,
                 send_interval: float = 1.0):

        self.dataset_path = Path(dataset_path)
        
        self.topic = TOPIC_RAW_DATA
        self.config = PRODUCER_CONFIG
        self.num_producers = num_producers
        self.send_interval = send_interval
        
        self.logger = logging.getLogger(self.__class__.__name__)

        self.threads = []
        self._load_data()

    def _load_data(self):
        try:
            self.data = pd.read_csv(self.dataset_path)
            self.X = self.data.drop(columns=['quality'])
            self.logger.info(f"Dataset loaded successfully. Rows: {len(self.data)}")
        except Exception as e:
            self.logger.error(f"Error loading dataset: {e}")
            raise

    def _create_producer(self) -> KafkaProducer:
        return KafkaProducer(self.config)

    def _producer_worker(self, producer_id: str, indexes: list):
        producer = self._create_producer()
        generator = self._PayloadGenerator(self.X, indexes)
        
        for payload in generator:
            try:
                producer.produce(
                    topic=self.topic,
                    value=json.dumps(payload),
                    key=producer_id
                )
                time.sleep(self.send_interval)
            except Exception as e:
                self.logger.error(f"Producer {producer_id} error: {e}")
        
        producer.flush()

    def start(self):
        kf = KFold(n_splits=self.num_producers, shuffle=True)
        
        for i, (indexes, _) in enumerate(kf.split(self.X)):
            thread = threading.Thread(
                target=self._producer_worker,
                args=(f'producer-{i}', indexes),
                name=f'KafkaProducerThread-{i}'
            )
            self.threads.append(thread)
            thread.start()
            self.logger.info(f"Started producer thread {i}")

    def wait_completion(self):
        for thread in self.threads:
            thread.join()
        self.logger.info("All producers completed work")

    class _PayloadGenerator:
        def __init__(self, data, indexes):
            self.data = data
            self.indexes = indexes

        def __iter__(self):
            for index in self.indexes:
                yield self.data.iloc[index].to_dict()
