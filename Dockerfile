FROM holdenk/rayray:nightly
# Setup the dependencies in advance
COPY requirements.txt /tmp/req.txt
# On ARM we _sometimes_ need to build the PostGres connector from source (depending on version).
RUN sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install -y libpq-dev
# See https://github.com/python/typing/issues/573
RUN pip uninstall -y typing
RUN pip install -U -r /tmp/req.txt
RUN sudo mkdir -p /apps/messaging; sudo chown -R ray /apps
COPY ./messaging /apps/messaging
RUN pip install -r /apps/messaging/web/src/requirements/local.txt
# idk -- weird bug
RUN pip install -U "aioredis < 2"
COPY ./setup.py /apps
COPY ./proto /apps
RUN cd /apps; pip install -e .; cd -
