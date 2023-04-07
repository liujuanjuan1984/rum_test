import logging
import sys

from quorum_fullnode_py import FullNode

from rum_test import CheckChain

logging.basicConfig(level=logging.INFO)

args = sys.argv[1:]
if args:
    port = int(args[0])  # "62716"
else:
    raise ValueError("`python do_check_chain.py <port>`")

rum = FullNode(port=port)
bot = CheckChain(rum)
bot.check_groupchains_of_node()
