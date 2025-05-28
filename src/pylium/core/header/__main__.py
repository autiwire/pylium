from . import Header, __manifest__


import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print(f"__manifest__.__dict__: {__manifest__.__dict__}")