from common.kafka_consumer import KafkaConsumer

from common.configuration import (
    TOPIC_RESULT,
    CONSUMER_CONFIG_RESULT
)

from collections import defaultdict
import streamlit as st
import pandas as pd
import logging
import json


class ResultVisualizer:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.consumer_config = CONSUMER_CONFIG_RESULT
        self.input_topic = TOPIC_RESULT
        
        self._init_ui()
        self._init_consumer()

    def _init_ui(self):
        st.set_page_config(page_title='Статистика по винным складам', layout='wide')
        st.title('Количество по типам')
        self.chart_placeholder = st.empty()
        
        if 'histogram' not in st.session_state:
            st.session_state.histogram = defaultdict(int)
        
        if 'good_wine' not in st.session_state:
            st.session_state.good_wine = None

    def _init_consumer(self):
        self.consumer = KafkaConsumer(
            self.consumer_config,
            value_deserializer=lambda x: json.loads(x)
        )
        self.consumer.subscribe([self.input_topic])
        self.logger.info(f"Subscribed to {self.input_topic}")

    def _update_visualization(self, quality, raw_data):
        st.session_state.histogram[quality] += 1
        self._update_chart()
        
        if quality >= 6:
            self._update_good_wine_table(raw_data, quality)

    def _update_chart(self):
        df = pd.DataFrame.from_dict(st.session_state.histogram, orient='index')
        self.chart_placeholder.bar_chart(df)

    def _update_good_wine_table(self, raw_data, quality):
        new_row = pd.DataFrame([{**raw_data, 'quality': quality}])
        
        if st.session_state.good_wine is None:
            st.session_state.good_wine = st.dataframe(new_row)
        else:
            st.session_state.good_wine.add_rows(new_row)

    def _process_message(self, message):
        try:
            value = message['value']
            self._update_visualization(value['quality'], value['raw'])
        except Exception as e:
            self.logger.error(f"Processing error: {e}")

    def run(self):
        try:
            while True:
                message = self.consumer.consume()               
                self._process_message(message)

        except KeyboardInterrupt:
            self.logger.info("Shutting down visualizer")
        finally:
            self.shutdown()

    def shutdown(self):
        self.consumer.close()
        self.logger.info("Visualizer resources closed")