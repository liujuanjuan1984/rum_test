import logging

from rum_test.chain import CheckChain

__version__ = "0.0.1"
__author__ = "liujuanjuan1984"


logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.basicConfig(
    format="%(name)s %(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
