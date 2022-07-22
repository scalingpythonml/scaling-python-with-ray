import os

swarm_username = os.getenv("swarm_username")
swarm_password = os.getenv("swarm_password")
hiveBaseURL = os.getenv(
    "hivebaseurl", 'https://bumblebee.hive.swarm.space/hive')

swarm_login_params = {'username': swarm_username, 'password': swarm_password}

mail_server = os.getenv("mail_server")
mail_username = os.getenv("mail_username")
mail_password = os.getenv("mail_password")
max_retries = int(os.getenv("max_retries", "10"), 10)
