import logging

logger = logging.getLogger(__name__)


class CheckChain:
    def __init__(self, rum_fullnode_client):
        self.rum = rum_fullnode_client

    def check_appdb(self, group_id, warn_max=3):
        """
        检查 appdb 索引生成是否正常
        有两种检查方式：
        1、从 block 获取 trx_id，然后通过 /trx api 获取；
        2、持续获取 content，直到拿不到数据为止，检查最后一条 block 所在的区块高度（逆序检查)
        """
        self.rum.group_id = group_id
        group_name = self.rum.api.group_info().get("group_name")
        epoch = self.rum.api.group_info().get("currt_top_block")
        logger.info(
            "%s check_appdb %s start, currt_top_block %s", group_name, group_id, epoch
        )
        # 逆序检查
        warn_count = 0
        for i in range(epoch, 0, -1):
            block = self.rum.api.get_block(i)
            trxs = block.get("Trxs") or []
            if len(trxs) == 0:
                logger.warning("block %s is empty", i)
            for trx in trxs:
                tid = trx["TrxId"]
                # /trx
                if tid != self.rum.api.get_trx(tid).get("TrxId"):
                    warn_count += 1
                    logger.warning(
                        "block %s/%s trx_id: %s is not return from /trx api",
                        i,
                        epoch,
                        tid,
                    )
                # /content
                itrxs = self.rum.api.get_content(start_trx=tid)
                if len(itrxs) == 0:
                    if i != epoch:  # 最高区块不提醒
                        warn_count += 1
                        logger.warning(
                            "block %s/%s trx_id: %s return 0 trxs from /content api",
                            i,
                            epoch,
                            tid,
                        )

            if warn_count >= warn_max:
                logger.warning(
                    "check_appdb %s done, warn_count %s", group_id, warn_count
                )
                break

        logger.info("check_appdb %s done", group_id)

    def get_trx_from_block(self, trx_id, group_id):
        """从 group chain 的 block 中查找获取 trx"""
        self.rum.group_id = group_id
        epoch = self.rum.api.group_info().get("currt_top_block")
        group_name = self.rum.api.group_info(group_id).get("group_name")
        logging.info(
            "%s get_trx_from_block %s start, currt_top_block %s",
            group_name,
            group_id,
            epoch,
        )
        for i in range(1, epoch + 1):
            block = self.rum.api.get_block(i)
            trxs = block.get("Trxs") or []
            for trx in trxs:
                if trx["TrxId"] == trx_id:
                    logger.info("%s get trx_id: %s from block: %s", group_id, trx_id, i)
                    return trx
        logger.warning("%s can not get trx_id: %s from block", group_id, trx_id)
        return None

    def check_group_chain(self, group_id):
        """
        检查 group chain：
        block 是否为空（不为空才正常），
        是否重复打包同一个 trx_id（不重复打包才正常）
        """

        self.rum.group_id = group_id
        group_name = self.rum.api.group_info(group_id).get("group_name")
        epoch = self.rum.api.group_info().get("currt_top_block")
        logger.info(
            "%s check_group_chain %s start,  currt_top_block %s",
            group_name,
            group_id,
            epoch,
        )
        trxs_counts = {}
        for i in range(1, epoch + 1):
            block = self.rum.api.get_block(i)
            trxs = block.get("Trxs") or []
            if len(trxs) == 0:
                logger.warning("block %s is empty", i)
            for trx in trxs:
                tid = trx["TrxId"]
                if tid not in trxs_counts:
                    trxs_counts[tid] = {"num": 1, "block": [i]}
                else:
                    trxs_counts[tid]["num"] += 1
                    trxs_counts[tid]["block"].append(i)

        for k, v in trxs_counts.items():
            if v["num"] > 1:
                logger.warning(
                    "trx_id: %s is duplicate in blocks: %s %s", k, v["num"], v["block"]
                )
        logger.info("check_group_chain %s done.", group_id)
        return trxs_counts

    def check_groupchains_of_node(self):
        """检查整个节点的所有 groups 的 trxs 是否存在 trx_id 重复的情况。如果存在重复则异常，否则正常"""
        logger.info("node check_group_chain start")

        for group_id in self.rum.api.groups_id:
            self.check_group_chain(group_id)

        for group_id in self.rum.api.groups_id:
            self.check_appdb(group_id, warn_max=3)

        logger.info("node check_group_chain done")
