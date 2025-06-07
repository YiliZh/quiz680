import nltk
import logging

logger = logging.getLogger(__name__)

def download_nltk_data():
    """Download all required NLTK data."""
    required_data = [
        'punkt',
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words'
    ]
    
    for data in required_data:
        try:
            logger.info(f"Checking NLTK data: {data}")
            nltk.data.find(f'tokenizers/{data}')
            logger.info(f"NLTK data {data} already exists")
        except LookupError:
            logger.info(f"Downloading NLTK data: {data}")
            nltk.download(data, quiet=True)
            logger.info(f"Successfully downloaded NLTK data: {data}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_nltk_data() 