from confluent_kafka import KafkaError, KafkaException
from confluent_kafka import Producer
from typing import Optional, Callable, Any
import logging


class KafkaProducer:
    def __init__(self,
                 config: dict, 
                 key_serializer: Callable[[str], bytes | None] = lambda x: x.encode('utf-8') if x else None,
                 value_serializer=lambda x: x.encode('utf-8') if x else None):

        if 'bootstrap.servers' not in config:
            raise ValueError("Config must include 'bootstrap.servers'")

        self._producer = Producer(config)
        self._key_serializer = key_serializer
        self._value_serializer = value_serializer
        self._logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def _default_delivery_callback(err: KafkaError, msg):
        if err:
            logging.error(f"Message delivery failed: {err}")
        else:
            logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}]")

    def produce(self, 
                topic: str, 
                value: Any, 
                key=None, 
                headers: dict = None, 
                callback: callable = None):

        if value is None:
            raise ValueError("Value cannot be None")

        try:
            key_bytes = self._key_serializer(key) if key is not None else None
            value_bytes = self._value_serializer(value)
            
            self._producer.produce(
                topic=topic,
                key=key_bytes,
                value=value_bytes,
                headers=headers,
                on_delivery=callback or self._default_delivery_callback
            )
            
            self._producer.poll(0)

        except BufferError as e:
            self._logger.error(f"Buffer error: {e}. Flushing producer...")
            self.flush()
            raise
        except KafkaException as e:
            self._logger.error(f"Kafka exception: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error: {e}")
            raise

    def flush(self, timeout: float = 10):
        self._logger.info("Flushing producer...")
        remaining = self._producer.flush(timeout)
        if remaining > 0:
            self._logger.warning(f"Failed to flush {remaining} messages")

    def close(self):
        self._logger.info("Closing producer...")
        self.flush()
