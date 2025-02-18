from backend.data_collector import KafkaDatasetProducer

from pathlib import Path
import logging
import sys


ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH / 'data'

DATASET_PATH = DATA_PATH / 'wine_data.csv'


if __name__ == '__main__':    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    producer = KafkaDatasetProducer(
        dataset_path=DATASET_PATH,
        num_producers=2,
        send_interval=0.5
    )
    
    try:
        producer.start()
        producer.wait_completion()
        logging.info('Done')

    except KeyboardInterrupt:
        logging.error('Interrupted by user')
        sys.exit(1)
