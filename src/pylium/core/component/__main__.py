from . import Component

import fire
import os

import logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # fix using cat instead of nano/vi for fire output

    os.environ["PAGER"] = "cat"
    fire.Fire(Component.pylium().CLI)
