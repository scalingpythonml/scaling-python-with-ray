#!/bin/bash

set -ex
export arch=$(uname -m)
if [ "$arch" == "aarm64" ]; then
  arch="arm64";
fi
wget --quiet https://github.com/conda-forge/miniforge/releases/download/4.8.5-1/Miniforge3-4.8.5-1-Linux-${arch}.sh -O ~/miniforge.sh
chmod a+x ~/miniforge.sh
~/miniforge.sh -b -p /opt/conda
/opt/conda/bin/conda clean -tipsy
ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
echo "conda activate base" >> ~/.bashrc
echo ". /opt/conda/etc/profile.d/conda.sh" >> /etc/bash.bashrc
echo "conda activate base" >> /etc/bash.bashrc
source ~/.bashrc
find /opt/conda/ -follow -type f -name '*.a' -delete
find /opt/conda/ -follow -type f -name '*.js.map' -delete
/opt/conda/bin/conda clean -afy
/opt/conda/bin/conda install --yes nomkl cytoolz cmake tini
/opt/conda/bin/conda init bash
/opt/conda/bin/conda install --yes mamba
apt-get update
apt-get install -yq graphviz git build-essential cmake telnet && \
ln -s /lib /lib64 || echo "No need"
apt install -y bash tini libc6 libpam-modules krb5-user libnss3 procps ca-certificates p11-kit wget bzip2 git mercurial subversion dirmngr gnupg
mamba install --yes python==${PYTHON_VERSION}
pip install --upgrade pip setuptools
mamba install --yes numpy==1.19.2 pandas cytoolz numba lz4 scikit-build python-blosc=1.9.2
(mamba install --yes pyarrow ||  pip install -vvv pyarrow)
apt-get clean
rm -rf /var/cache/apt/*
rm -rf /var/lib/apt/lists/*
