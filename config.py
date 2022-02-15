class Config:
    pass


class QuorumConfig(Config):

    HOST = "127.0.0.1"
    PORT = 50415
    SERVER_CRT_FILEPATH = {
        "gui": r"C:\Users\75801\AppData\Local\Programs\prs-atm-app\resources\quorum_bin\certs\server.crt",
        "cli": r"D:\RUM2-DATA\certs\server.crt",
    }
    GROUP_ID = {
        "去中心微博": "3bb7a3be-d145-44af-94cf-e64b992ff8f0",
        "刘娟娟的朋友圈": "4e784292-6a65-471e-9f80-e91202e3358c",
        "test_group_name":"test_group_id",
    }

    def as_dict(self, env="gui"):
        return {
            "port": self.PORT,
            "host": self.HOST,
            "appid": "peer",
            "crtfile": self.SERVER_CRT_FILEPATH[env],
        }
