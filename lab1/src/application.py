from frontend.data_processor import DataPreprocessor
from frontend.result_visualizer import ResultVisualizer

from pathlib import Path
import threading
import logging
import sys


ROOT_PATH = Path(__file__).parent.parent
MODELS_PATH = ROOT_PATH / 'models'

MODEL_PATH = MODELS_PATH / 'preproc.checkpoint'


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        processor = DataPreprocessor(
            preproc_model_path=MODEL_PATH
        )

        preprocessor_thread = threading.Thread(target=processor.run)
        preprocessor_thread.start()

        ResultVisualizer().run()
            
        preprocessor_thread.join()

    except Exception as e:
        logging.error(f"Critical error: {e}")
        sys.exit(1)
