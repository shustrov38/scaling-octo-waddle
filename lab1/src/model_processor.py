from backend.model_processor import KafkaModelProcessor

from pathlib import Path
import logging
import sys


ROOT_PATH = Path(__file__).parent.parent
MODELS_PATH = ROOT_PATH / 'models'

MODEL_PATH = MODELS_PATH / 'model.checkpoint'


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        processor = KafkaModelProcessor(
            model_path=MODEL_PATH
        )

        processor.run()

    except Exception as e:
        logging.error(f"Critical error: {e}")
        sys.exit(1)
