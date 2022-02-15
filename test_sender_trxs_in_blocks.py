from rumpy import RumClient
from config import QuorumConfig
from officepy import JsonFile
import datetime
from time import sleep

c = client = RumClient(**QuorumConfig().as_dict("cli"))

gid = QuorumConfig.GROUP_ID["test_group_name"]

trxs_file = f"sender_trxs_G{gid}.json"
trxs_in_blocks_file = f"trxs_in_blocks_G{gid}.json"
blocks_file = f"blocks_G{gid}.json"


def test_sendnotes(notes, seconds=10):

    trxs = JsonFile(trxs_file).read({})

    for note in notes:
        resp = c.group.send_note(gid, content=note)
        if "trx_id" in resp:
            tid = resp["trx_id"]
            trxs[tid] = {"content": note, "send_at": str(datetime.datetime.now())}

        print(tid)
        JsonFile(trxs_file).write(trxs)
        sleep(seconds)


def trx_in_blocks(n=30):

    check_trxs = JsonFile(trxs_in_blocks_file).read({})

    blocks = JsonFile(blocks_file).read({})

    bid = c.group.info(gid).highest_block_id
    for i in range(n):
        block = c.group.block(gid, bid)
        blocks[block["BlockId"]] = block
        JsonFile(blocks_file).write(blocks)
        for trx in block.get("Trxs") or []:
            tid = trx["TrxId"]
            if tid not in check_trxs:
                check_trxs[tid] = [bid]
            elif bid not in check_trxs[tid]:
                check_trxs[tid].append(bid)
        bid = block["PrevBlockId"]
        JsonFile(trxs_in_blocks_file).write(check_trxs)


def check_trx_onchain():

    for log in logs:
        if log["action"] == "group.send_note":
            tid = log["resp"]["trx_id"]


def update_sender_trxs():
    check_trxs = JsonFile(trxs_in_blocks_file).read({})
    sender_trxs = JsonFile(trxs_file).read({})

    for tid in sender_trxs:
        if tid in check_trxs:
            sender_trxs[tid]["in_blocks"] = check_trxs[tid]
    JsonFile(trxs_file).write(sender_trxs)

    for tid in sender_trxs:
        if not sender_trxs[tid].get("in_blocks"):
            print(tid, "还没上链呢")


if __name__ == "__main__":

    notes = [
        "one line",
        "two line",
        "threr line",
    ]
    test_sendnotes(notes)
    for i in range(6):
        trx_in_blocks(200)
        update_sender_trxs()
        sleep(20)
