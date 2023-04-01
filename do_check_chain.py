import logging

from quorum_fullnode_py import FullNode

from rum_test import CheckChain

logging.basicConfig(level=logging.INFO)

rum = FullNode(port=11002)
bot = CheckChain(rum)

bot.check_groupchains_of_node()
