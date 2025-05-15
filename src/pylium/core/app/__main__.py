from . import *

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)    

if __name__ == "__main__":
    AppPackage.cli()