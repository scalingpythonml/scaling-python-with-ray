import os


class Settings(object):
    def __init__(self):
        self.swarm_username = os.getenv("swarm_username")
        self.swarm_password = os.getenv("swarm_password")
        self.hiveBaseURL = os.getenv(
            "hivebaseurl", 'https://bumblebee.hive.swarm.space/hive')

        self.swarm_login_params = {
            'username': self.swarm_username,
            'password': self.swarm_password}

        self.mail_server = os.getenv("mail_server")
        self.mail_username = os.getenv("mail_username")
        self.mail_password = os.getenv("mail_password")
        self.mail_port = int(os.getenv("mail_port", "25"), 10)
        self.max_retries = int(os.getenv("max_retries", "10"), 10)
        self.BW_USERNAME = os.getenv("BW_USERNAME", "")
        self.BW_PASSWORD = os.getenv("BW_PASSWORD", "")
        self.BW_MESSAGING_APPLICATION_ID = os.getenv("BW_MESSAGING_APPLICATION_ID", "")
        self.BW_ACCOUNT_ID = os.getenv("BW_ACCOUNT_ID", "")
