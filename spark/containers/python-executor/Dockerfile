#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

ARG base_img

FROM $base_img
WORKDIR /

# Reset to root to run installation tasks
USER 0

ENV PATH /opt/conda/bin:$PATH

RUN mkdir ${SPARK_HOME}/python

RUN apt-get update --fix-missing && \
    apt-get install -yq graphviz git build-essential cmake telnet && \
    apt install -y bash tini libc6 libpam-modules krb5-user libnss3 procps ca-certificates p11-kit wget bzip2 git mercurial subversion && \
    rm /bin/sh && \
    ln -sv /bin/bash /bin/sh

COPY bin/pysetup.sh /pysetup.sh 
RUN chmod a+x /pysetup.sh && ./pysetup.sh
RUN conda install -c conda-forge --yes mamba && \
    mamba install --yes python==3.8.6 && \
    pip install --upgrade pip setuptools && \
    mamba install --yes numpy==1.19.2 pandas cytoolz numba lz4 scikit-build python-blosc=1.9.2 && \
    (mamba install --yes pyarrow ||  pip install -vvv pyarrow)


COPY python/pyspark ${SPARK_HOME}/python/pyspark
COPY python/lib ${SPARK_HOME}/python/lib

WORKDIR /opt/spark/work-dir
ENTRYPOINT [ "/opt/entrypoint.sh" ]

# Specify the User that the actual main process will run as
ARG spark_uid=185
USER ${spark_uid}
