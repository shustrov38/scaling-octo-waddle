from confluent_kafka import KafkaError, KafkaException, TopicPartition
from confluent_kafka import Consumer
from typing import Optional, Callable, Any
import logging

class KafkaConsumer:
    def __init__(self, 
                 config: dict,
                 key_deserializer: Callable[[bytes], Any] = lambda x: x.decode('utf-8') if x else None,
                 value_deserializer: Callable[[bytes], Any] = lambda x: x.decode('utf-8') if x else None):

        required_keys = {'bootstrap.servers', 'group.id'}
        if not required_keys.issubset(config.keys()):
            raise ValueError(f"Config must contain {required_keys}")

        self._consumer = Consumer(config)
        self._key_deserializer = key_deserializer
        self._value_deserializer = value_deserializer
        self._logger = logging.getLogger(self.__class__.__name__)
        self._is_subscribed = False

    def subscribe(self, topics: list[str], on_assign: Optional[Callable] = None):
        if on_assign:
            self._consumer.subscribe(topics, on_assign=on_assign)
        else:
            self._consumer.subscribe(topics)
        self._is_subscribed = True
        self._logger.info(f"Subscribed to topics: {topics}")

    def _deserialize_message(self, msg) -> dict[str, Any] | None:
        if msg is None:
            return None
            
        key = self._key_deserializer(msg.key()) if msg.key() else None
        value = self._value_deserializer(msg.value()) if msg.value() else None
        return {
            'topic': msg.topic(),
            'partition': msg.partition(),
            'offset': msg.offset(),
            'key': key,
            'value': value,
            'headers': msg.headers(),
            'timestamp': msg.timestamp()
        }

    def consume(self, timeout: float = 1.0) -> Optional[dict]:
        if not self._is_subscribed:
            raise RuntimeError("Consumer is not subscribed to any topics")

        try:
            msg = self._consumer.poll(timeout)
            
            if msg is None:
                return None
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    self._logger.debug("Reached end of partition")
                else:
                    raise KafkaException(msg.error())
                return None

            return self._deserialize_message(msg)

        except KafkaException as e:
            self._logger.error(f"Kafka error: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error: {e}")
            raise

    def commit(self, message: Optional[dict] = None, asynchronous: bool = True):
        try:
            if message:
                topic_part = (message['topic'], message['partition'])
                offset_to_commit = message['offset'] + 1
                
                self._consumer.commit(
                    offsets=[TopicPartition(topic_part[0], topic_part[1], offset_to_commit)],
                    asynchronous=asynchronous
                )
                self._logger.debug(f"Committed offset {offset_to_commit} for {topic_part}")
            else:
                self._consumer.commit(asynchronous=asynchronous)
                self._logger.debug("Committed current offsets for all assigned partitions")

        except KafkaException as e:
            self._logger.error(f"Commit failed: {e}")
            raise

    def close(self):
        self._logger.info("Closing consumer")
        self._consumer.close()

    @property
    def assignment(self) -> list:
        return self._consumer.assignment()

    def unsubscribe(self):
        self._consumer.unsubscribe()
        self._is_subscribed = False
        self._logger.info("Unsubscribed from all topics")
