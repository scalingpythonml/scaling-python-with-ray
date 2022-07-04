import os

swarm_username = os.getenv("swarm_username")
swarm_password = os.getenv("swarm_password")
hiveBaseURL = os.getenv("hivebaseurl", 'https://bumblebee.hive.swarm.space/hive')

swarm_login_params = {'username': swarm_username, 'password': swarm_password}
