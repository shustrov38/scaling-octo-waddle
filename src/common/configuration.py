BOOTSTRAP_SERVERS = 'localhost:9095'

TOPIC_RAW_DATA = 'raw_wine_params'
TOPIC_DATA = 'model_input'
TOPIC_RESULT = 'wine_quality'

PRODUCER_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVERS
}

CONSUMER_CONFIG_RAW_DATA = {
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': 'my_consumers_raw_data',
    'auto.offset.reset': 'earliest'
}

CONSUMER_CONFIG_DATA = {
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': 'my_consumers_data',
    'auto.offset.reset': 'earliest'
}

CONSUMER_CONFIG_RESULT = {
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': 'my_consumers_result',
    'auto.offset.reset': 'earliest'
}