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

ARG PYTHON_VERSION=3.8.6

# Reset to root to run installation tasks
USER 0

ENV PATH /opt/conda/bin:$PATH

RUN mkdir ${SPARK_HOME}/python

RUN apt-get update --fix-missing --yes && \
    apt-get install -yq graphviz git build-essential cmake telnet && \
    apt install -y bash tini libc6 libpam-modules krb5-user libnss3 procps ca-certificates p11-kit wget bzip2 git mercurial subversion sudo locales fonts-liberation && \
    wget http://mirrors.kernel.org/ubuntu/pool/main/r/run-one/run-one_1.17-0ubuntu1_all.deb && \
    dpkg --install run-one_1.17-0ubuntu1_all.deb && \
    rm *.deb && \
    rm /bin/sh && \
    ln -sv /bin/bash /bin/sh && \
    rm -rf /var/cache/apt/*

COPY bin/pysetup.sh /pysetup.sh
RUN chmod a+x /pysetup.sh && ./pysetup.sh

# s3a support
#tag::s3a[]
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.2.0/hadoop-aws-3.2.0.jar ${SPARK_HOME}/jars/
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.563/aws-java-sdk-bundle-1.11.563.jar ${SPARK_HOME}/jars/
#end::s3a[]

#tag::iceberg[]
ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark3-runtime/0.11.0/iceberg-spark3-runtime-0.11.0.jar ${SPARK_HOME}/jars/
ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark3-extensions/0.11.0/iceberg-spark3-extensions-0.11.0.jar ${SPARK_HOME}/jars/
ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark3/0.11.0/iceberg-spark3-0.11.0.jar ${SPARK_HOME}/jars/
#ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-parquet/0.11.0/iceberg-parquet-0.11.0.jar ${SPARK_HOME}/jars/
#ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-core/0.11.0/iceberg-core-0.11.0.jar ${SPARK_HOME}/jars/
#ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-arrow/0.11.0/iceberg-arrow-0.11.0.jar ${SPARK_HOME}/jars/
#ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-data/0.11.0/iceberg-data-0.11.0.jar ${SPARK_HOME}/jars/
#end::iceberg[]

#tag::perms[]
RUN chmod a+rx ${SPARK_HOME}/jars/*.jar
#end::perms[]


COPY licenses/ ${SPARK_HOME}/licenses
COPY python/ ${SPARK_HOME}/python

RUN cd ${SPARK_HOME}/python/; pip install -e .

WORKDIR /opt/spark/work-dir
ENTRYPOINT [ "/opt/entrypoint.sh" ]

# Specify the User that the actual main process will run as
ARG spark_uid=185
USER ${spark_uid}
