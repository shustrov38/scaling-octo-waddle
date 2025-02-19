BOOTSTRAP_SERVERS_1 = 'localhost:9095'
BOOTSTRAP_SERVERS_2 = 'localhost:9096'

TOPIC_RAW_DATA = 'raw_wine_params'
TOPIC_DATA = 'model_input'
TOPIC_RESULT = 'wine_quality'

PRODUCER_CONFIG_1 = {
    'bootstrap.servers': BOOTSTRAP_SERVERS_1
}

PRODUCER_CONFIG_2 = {
    'bootstrap.servers': BOOTSTRAP_SERVERS_2
}

CONSUMER_CONFIG_RAW_DATA = {
    'bootstrap.servers': BOOTSTRAP_SERVERS_1,
    'group.id': 'my_consumers_raw_data',
    'auto.offset.reset': 'earliest'
}

CONSUMER_CONFIG_DATA = {
    'bootstrap.servers': BOOTSTRAP_SERVERS_2,
    'group.id': 'my_consumers_data',
    'auto.offset.reset': 'earliest'
}

CONSUMER_CONFIG_RESULT = {
    'bootstrap.servers': BOOTSTRAP_SERVERS_1,
    'group.id': 'my_consumers_result',
    'auto.offset.reset': 'earliest'
}