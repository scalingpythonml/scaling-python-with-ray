#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from typing import List
import dask
import numpy as np
import dask.array as da
import dask.bag as bag
from dask.distributed import Client


# In[ ]:


# Note: if we were on a cluster we'd have to do more magic to install it on all the nodes in the cluster.
get_ipython().system('pip install PyPDF2')


# In[ ]:


import fsspec


# In[ ]:


client = Client()
client


# In[ ]:


#tag::custom_load[]
def discover_files(path: str):
    (fs, fspath) = fsspec.core.url_to_fs(path)
    return (fs, fs.expand_path(fspath, recursive="true"))
def load_file(fs, file):
    """Load (and initially process) the data."""
    from PyPDF2 import PdfReader
    try:
        file_contents = fs.open(file)
        pdf = PdfReader(file_contents)
        return (file, pdf.pages[0].extract_text())
    except Exception as e:
        return (file, e)
def load_data(path: str):
    (fs, files) = discover_files(path)
    bag_filenames = bag.from_sequence(files)
    contents = bag_filenames.map(lambda f:load_file(fs, f))
    return contents
#end::custom_load[]


# In[ ]:


#tag::preprocess_json[]
def make_url(idx):
    page_size = 100
    start = idx * page_size
    return f"https://api.fda.gov/food/enforcement.json?limit={page_size}&skip={start}"
urls = list(map(make_url, range(0, 10)))
# Since they are multi-line json we can't use the default \n line delim
raw_json = bag.read_text(urls, linedelimiter="NODELIM")
def clean_records(raw_records):
    import json
    # We don't need the meta field just the results field
    return json.loads(raw_records)["results"]
cleaned_records = raw_json.map(clean_records).flatten()
# And now we can convert it to a DataFrame
df = bag.Bag.to_dataframe(cleaned_records)
#end::preprocess_json[]


# In[ ]:


df.head()


# In[ ]:


files = []
files = discover_files("file:///tmp/a0")
list(files)


# In[ ]:


load_data("file:///tmp/pdfs").compute()


# In[ ]:


#tag::parallel_list[]
def parallel_recursive_list(path: str, fs = None) -> List[str]:
    print(f"Listing {path}")
    if fs is None:
        (fs, path) = fsspec.core.url_to_fs(path)
    info = []
    infos = fs.ls(path, detail=True)
    # Above could throw PermissionError, but if we can't list the dir it's probably wrong so let it bubble up
    files = []
    dirs = []
    for i in infos:
        if i["type"] == "directory":
            # You can speed this up by using futures, covered in "Advanced Scheduling"
            dir_list = dask.delayed(parallel_recursive_list)(i["name"], fs=fs)
            dirs += dir_list
        else:
            files.append(i["name"])
    for sub_files in dask.compute(dirs):
        files.extend(sub_files)
    return files
#end::parallel_list[]


# In[ ]:


files = []
files = parallel_recursive_list("file:///tmp/a0")


# In[ ]:


files


# In[ ]:


#tag::parallel_list_large[]
def parallel_list_directories_recursive(path: str, fs = None) -> List[str]:
    """
    Recursively find all the sub directories.
    """
    if fs is None:
        (fs, path) = fsspec.core.url_to_fs(path)
    info = []
    # Ideally we could filter for directories here, but fsspec lacks that (for now)
    infos = fs.ls(path, detail=True)
    # Above could throw PermissionError, but if we can't list the dir it's probably wrong so let it bubble up
    dirs = []
    result = []
    for i in infos:
        if i["type"] == "directory":
            # You can speed this up by using futures, covered in "Advanced Scheduling"
            result.append(i["name"])
            dir_list = dask.delayed(parallel_list_directories_recursive)(i["name"], fs=fs)
            dirs += dir_list
    for sub_dirs in dask.compute(dirs):
        result.extend(sub_dirs)
    return result

def list_files(path: str, fs = None) -> List[str]:
    """List files at a given depth with no recursion."""
    if fs is None:
        (fs, path) = fsspec.core.url_to_fs(path)
    info = []
    # Ideally we could filter for directories here, but fsspec lacks that (for now)
    return map(lambda i: i["name"], filter(lambda i: i["type"] == "directory", fs.ls(path, detail=True)))
    

def parallel_list_large(path: str, npartitions = None, fs = None) -> bag:
    """
    Find all of the files (potentially too large to fit on the head node).
    """
    directories = parallel_list_directories_recursive(path, fs = fs)
    dir_bag = dask.bag.from_sequence(directories, npartitions = npartitions)
    return dir_bag.map(lambda dir: list_files(dir, fs = fs)).flatten()
#end::parallel_list_large[]


# In[ ]:


parallel_list_large("/tmp/a0").compute()


# In[ ]:


#tag::custom_load_nonfs[]
def special_load_function(x):
    ## Do your special loading logic in this function, like reading a database
    return ["Timbit", "Is", "Awesome"][0: x % 4]

partitions = bag.from_sequence(range(20), npartitions=5)
raw_data = partitions.map(special_load_function).flatten()
#end::custom_load_nonfs[]


# In[ ]:


raw_data.take(5)


# In[ ]:


bag.from_sequence(range(0,1000)).map(lambda x: (x, x)).foldby(lambda x, y: x + y, lambda x, y: x + y)


# In[ ]:





# In[ ]:




