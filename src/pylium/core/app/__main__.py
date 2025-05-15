from ._h import AppPackage

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)    

if __name__ == "__main__":
    logger.info("Starting Pylium Core")
    AppPackage.cli()