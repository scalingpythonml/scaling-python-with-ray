#!/bin/bash
#tag::install[]
conda create -n dask python=3.8.6  mamba -y
conda activate dask
mamba install --yes python==3.8.6 cytoolz dask==2021.7.0 numpy pandas==1.3.0 beautifulsoup4 requests
#end::install[]
#tag::install_some_fun_stuff[]
mamba install --yes  cytoolz  lz4 scikit-build python-blosc pyzmq \
      s3fs requests dropbox paramiko pyarrow bokeh aiohttp numba fastparquet
#end::install_some_fun_stuff[]
