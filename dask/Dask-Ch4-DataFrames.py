#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dask
import numpy as np
import numpy.typing as npt
from typing import *
import pandas as pd
import dask.dataframe as dd


# In[ ]:


url = "https://gender-pay-gap.service.gov.uk/viewing/download-data/2021"
#tag::ex_load_1kb[]
many_chunks = dd.read_csv(url, blocksize="1kb")
many_chunks.index
#end::ex_load_1kb[]


# In[ ]:


#tag::ex_load_uk_gender_pay_gap_infered[]
df = dd.read_csv(
    "https://gender-pay-gap.service.gov.uk/viewing/download-data/2021")
#end::ex_load_uk_gender_pay_gap_infered[]


# In[ ]:


# The df.compute() is not needed for the load, but because Dask is lazy we need to trigger a compute
# for Dask to evaluate the DataFrame and notice the error.
try:
    df.compute() # Observe the failure
except Exception as e:
        print(e)
# - CompanyNumber
#  ValueError("invalid literal for int() with base 10: 'SC312912'")
#end::ex_load_uk_gender_pay_gap_infered


# In[ ]:


#tag::ex_load_uk_gender_pay_gap[]
df = dd.read_csv(
    "https://gender-pay-gap.service.gov.uk/viewing/download-data/2021",
    dtype={'CompanyNumber': 'str', 'DiffMeanHourlyPercent': 'float64'})
#end::ex_load_uk_gender_pay_gap[]


# In[ ]:


#tag::csv_gender_pay_gap_with_full_inference[]
df = dd.read_csv(
    "https://gender-pay-gap.service.gov.uk/viewing/download-data/2021",
    sample=256000000000000000000000000000000000000000000) # size in bytes to sample
# One day this should work, but for now it does not and we get the same error as if we had not sampled the entire CSV file
# df.compute()
#end::csv_gender_pay_gap_with_full_inference[]


# In[ ]:


from fsspec.registry import known_implementations
known_implementations


# In[ ]:


#tag::filna_ex[]
def fillna(df):
    return df.fillna(value={"PostCode": "UNKNOWN"}).fillna(value=0)
    
new_df = df.map_partitions(fillna)
# Since there could be an NA in the index clear the partition / division information
new_df.clear_divisions()
#end::filna_ex[]


# In[ ]:


new_df.compute()


# In[ ]:


narrow_df = new_df[["PostCode", "EmployerSize", "DiffMeanHourlyPercent"]]


# In[ ]:


grouped_df = narrow_df.groupby("PostCode")


# In[ ]:


alt_grouped_df = new_df.groupby(["PostCode", "SicCodes"])
alt_grouped_df.sum().head(2)


# In[ ]:


avg_by_postalcode = grouped_df.mean()


# In[ ]:


avg_by_postalcode.compute()


# In[ ]:


ops_by_postcalcode = narrow_df.set_index("PostCode", npartitions=10)
len(list(ops_by_postcalcode.partitions))


# In[ ]:


# Le sad, you can see this doesn't actually respect the partition size of one byte.
dask.visualize(narrow_df.set_index("PostCode", npartitions="auto", partition_size=1))


# In[ ]:


indexed = narrow_df.set_index("PostCode")
#tag::repartition[]
reparted = indexed.repartition(partition_size="20kb")
#end::repartition[]
dask.visualize(narrow_df.set_index("PostCode").repartition(partition_size="20kb"))


# In[ ]:


dask.visualize(ops_by_postcalcode)


# In[ ]:


fast_grouped_df = ops_by_postcalcode.groupby("PostCode")
fast_grouped_df.mean().compute()


# In[ ]:


# Kind of hacky string munging to get a median-ish to weight our values.
def update_empsize_to_median(df):
    def to_median(value):
        if " to " in value:
            f , t = value.replace(",", "").split(" to ")
            return (int(f) + int(t)) / 2.0
        elif "Less than" in value:
            return 100
        else:
            return 10000
    df["EmployerSize"] = df["EmployerSize"].apply(to_median)
    return df


df_with_median_emp_size = narrow_df.map_partitions(update_empsize_to_median)


# In[ ]:





# In[ ]:


df_with_median_emp_size.head(1)


# In[ ]:


def join_emp_with_diff(df):
    # In practice life would be easier if we multiplied these together but to illustrate
    # the custom aggregate we'll make this a tuple for now
    df["empsize_diff"] = list(df[["EmployerSize", "DiffMeanHourlyPercent"]].to_records(index=False))
    return df
df_diff_with_emp_size = df_with_median_emp_size.map_partitions(
    join_emp_with_diff)
df_diff_with_emp_size.head(1)


# In[ ]:


#tag::custom_agg[]
# Write a custom weighted mean, we get either a DataFrameGroupBy with multiple columns or SeriesGroupBy for each chunk
def process_chunk(chunk):
    def weighted_func(df):
        return (df["EmployerSize"] * df["DiffMeanHourlyPercent"]).sum()
    return (chunk.apply(weighted_func), chunk.sum()["EmployerSize"])
        
def agg(total, weights):
    return (total.sum(), weights.sum())

def finalize(total, weights):
    return total / weights
    
weighted_mean = dd.Aggregation(
    name='weighted_mean',
    chunk=process_chunk,
    agg=agg,
    finalize=finalize)

aggregated = df_diff_with_emp_size.groupby("PostCode")["EmployerSize", "DiffMeanHourlyPercent"].agg(weighted_mean)
#end::custom_agg[]
j = aggregated.head(4)
j


# In[ ]:


#tag::custom_agg_hyperloglog[]
# Wrap Dask's hyperloglog in dd.Aggregation

from dask.dataframe import hyperloglog

approx_unique = dd.Aggregation(
    name='aprox_unique',
    chunk=hyperloglog.compute_hll_array,
    agg=hyperloglog.reduce_state,
    finalize=hyperloglog.estimate_count)

aggregated = df_diff_with_emp_size.groupby("PostCode")["EmployerSize", "DiffMeanHourlyPercent"].agg(weighted_mean)
#end::custom_agg_hyperloglog[]
j = aggregated.head(4)
j


# In[ ]:


aggregated = new_df.groupby("PostCode")["EmployerId"].apply(lambda g: list(g))
aggregated.head(4)


# In[ ]:


# For loading data example the note here is that whatever params we pass through read_x
# if not consumed by dask (e.g. blocksize is used by Dask), 
# More generally all of Dask's DataFrame functions follow this pattern.
sf_covid_df = dd.read_csv("https://data.sfgov.org/api/views/gqw3-444p/rows.csv?accessType=DOWNLOAD", blocksize=None, dtype={
    'pct_tot_new_cases': 'float64',
    'pct_tot_new_cases_7_day_avg': 'float64',
    'new_case_rate': 'float64',
    'new_case_rate_7_day_avg': 'float64',
    'new_cases_7_day_avg': 'float64'}, parse_dates=['specimen_collection_date'], infer_datetime_format=True)


# In[ ]:


sf_covid_df.columns


# In[ ]:


sf_covid_df.head(10)


# In[ ]:


#tag::compute_entire_max_mean[]
dask.compute(
    sf_covid_df[["new_cases"]].max(),
    sf_covid_df[["new_cases"]].mean()
)
#end::compute_entire_max_mean[]


# In[ ]:


#tag::agg_entire[]
raw_grouped = sf_covid_df.groupby(lambda x: 0)
#end::agg_entire[]

#tag::max_mean[]
dask.compute(
    raw_grouped[["new_cases"]].max(),
    raw_grouped[["new_cases"]].mean())
#end::max_mean[]


# In[ ]:


# Drop columns & rows we don't care about before repartitioning
#tag::index_covid_data[]
mini_sf_covid_df = sf_covid_df[sf_covid_df['vaccination_status'] == 'All'][['specimen_collection_date', 'new_cases']]
#end::index_covid_data[]


# In[ ]:


mini_sf_covid_df.index


# In[ ]:


indexed_df = mini_sf_covid_df.set_index('specimen_collection_date', npartitions=5)
indexed_df.head(1)


# In[ ]:


from datetime import datetime

#tag::set_index_with_rolling_window[]
divisions = pd.date_range(start="2021-01-01", end=datetime.today(), freq='7D').tolist()
partitioned_df_as_part_of_set_index = mini_sf_covid_df.set_index(
    'specimen_collection_date', divisions=divisions)
#end::set_index_with_rolling_window[]


# In[ ]:


partitioned_df_as_part_of_set_index.divisions


# In[ ]:


len(list(indexed_df.partitions))


# In[ ]:


# Repartition on 14 day window
partitioned_df = indexed_df.repartition(freq='14D', force=True)


# In[ ]:


indexed_df.divisions


# In[ ]:


partitioned_df.divisions


# In[ ]:


# Rolling average with time delta
#tag::rolling_date_ex[]
rolling_avg = partitioned_df.map_overlap(lambda df: df.rolling('5D').mean(), pd.Timedelta('5D'), 0)
#end::rolling_date_ex[]


# In[ ]:


rolling_avg.compute()


# In[ ]:




