### Imports and function definition
import os
%env Z_USERNAME = fabiocaironi
%env Z_PASSWORD = p19Q@eKyo95w
import json
from zoltpy import util
import zoltpy

import pandas as pd
import pyarrow.parquet as pq
import pickle
import time
from zoltpy.connection import QueryType

def get_project():
  conn = util.authenticate()
  print('\n* projects')
  project_name = 'COVID-19 Forecasts'
  project = [project for project in conn.projects if project.name == project_name][0]
  return project

def busy_poll_job2(job):
    """
    A simple utility that polls job's status every second until either success or failure.
    """
    print(f"\n* polling for status change. job: {job}")
    while True:
        status = job.status_as_str
        failure_message = job.json["failure_message"]
        if (status == "FAILED") or (status == "TIMEOUT"):
            print(f"- {status}")

            print(f"x {status}")
            print("\n", failure_message)
            raise RuntimeError(f"job failed: job={job}, failure_message={failure_message!r}")
        if status == "SUCCESS":
            break

        time.sleep(1)
        job.refresh()

def get_dates():
  dates =[]

  for item in project.timezeros:
    dates.append(item.timezero_date)
  return dates

def get_targets():
  targs =[]
  for target in project.targets:
    name = target.name
    if "wk" in name:
      targs.append(target.name)
  return targs

def retrieve_data():
  dates = get_dates()
  targs = get_targets()
  
  missing = []

  print("Number of dates:" ,len(project.timezeros))
  num_date = 1


  for item in dates:
    
    date = str(item)
    print("\n\n ===== NEW DATE:",num_date," ===== \n")
    num_date = num_date+1
    print(date)

    query = {'timezeros': [str(date)],'targets': targs}
    print(query)


    try:
      job =  project.submit_query(QueryType.FORECASTS,query)
      busy_poll_job2(job)  # does refresh()
      rows = job.download_data()
      print(f"- got {len(rows)} forecast rows as a dataframe.")
      data = util.dataframe_from_rows(rows)
      data.to_parquet(date+".parquet")

    except:
      print("Something went wrong for ",date)
      missing.append(date)

      continue 
  
### Acquisition
## Data
project = get_project()
retrieve_data()

## Unique lists

# --- Note: use the following lines to read unique lists from pickle: ---
# f = open('data/unique_lists/<file_name>.pkl', 'rb')
# <var_name> = pickle.load(f)
# f.close()

# Models list
models = [m.abbreviation for m in project.models]
with open('data/unique_lists/models.pkl', 'wb') as f:
    pickle.dump(models, f)
f.close()

# Locations dictionary {name: unit}
locations = pd.read_csv("https://raw.githubusercontent.com/reichlab/zoltpy/master/zoltpy/locations.csv")
locations = dict(locations.dropna()[['location_name', 'location']].to_dict('split')['data'])
with open('data/unique_lists/locations.pkl', 'wb') as f:
    pickle.dump(locations, f)
f.close()


## Correspondence lists









