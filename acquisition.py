### Imports and function definition
import os
#%env Z_USERNAME = fabiocaironi
#%env Z_PASSWORD = p19Q@eKyo95w

os.environ["Z_USERNAME"] = "fabiocaironi"
os.environ["Z_PASSWORD"] = "p19Q@eKyo95w"

host = os.environ.get('Z_HOST')
username = os.environ.get('Z_USERNAME')
password = os.environ.get('Z_PASSWORD')

import json
from zoltpy import util
import zoltpy

import pandas as pd
import pyarrow.parquet as pq
import pickle
import time
from zoltpy.connection import QueryType


# Locations dictionary {name: unit}
locations = pd.read_csv("https://raw.githubusercontent.com/reichlab/zoltpy/master/zoltpy/locations.csv")
locations = dict(locations.dropna()[['location_name', 'location']].to_dict('split')['data'])
locations_inv = {v: k for k, v in locations.items()}
with open('data/unique_lists/locations.pkl', 'wb') as f:
    pickle.dump(locations, f)
f.close()




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
  loc =   list(locations.values())[1:len(locations.values())]
  missing = []

  print("Number of dates:" ,len(project.timezeros))
  num_date = 1


  for item in dates:
    
    date = str(item)
    print("\n\n ===== NEW DATE:",num_date," ===== \n")
    num_date = num_date+1
    print(date)

    query = {'timezeros': [str(date)],'targets': targs, 'units':loc}
    print(query)


    try:
      job =  project.submit_query(QueryType.FORECASTS,query)
      busy_poll_job2(job)  # does refresh()
      rows = job.download_data()
      print(f"- got {len(rows)} forecast rows as a dataframe.")
      data = util.dataframe_from_rows(rows)
      data.to_parquet("data/"+date+".parquet")

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


# Timezeros list 
timezeros = get_dates()
with open('data/unique_lists/timezeros.pkl', 'wb') as f:
    pickle.dump(timezeros, f)
f.close()

# Targets list
targets = get_targets()
with open('data/unique_lists/targets.pkl', 'wb') as f:
    pickle.dump(targets, f)
f.close()


#### CORRESPONDENCE dictionary ####

corr_dict = {}

for date in timezeros:
    try:
        currd = pd.read_parquet("data/"+str(date)+".parquet")
    except:
        print('File not found')
        continue
    
    print(str(date))
    
    for row in currd.values:
        try:
            modloc = (row[0], locations_inv[row[3]]) # MODEL AND LOCATION NAME
        except:
            continue
        if modloc in corr_dict.keys():
            corr_dict[modloc].add((row[1], # TIMEZERO
                                   row[4].split('ahead ',1)[1], #TARGET
                                   row[10])) # QUANTILE (None for point estimates)
        else:
            corr_dict[modloc] = {row[1], # TIMEZERO
                                 row[4].split('ahead ',1)[1], #TARGET
                                 row[10]} # QUANTILE (None for point estimates) 
            
            
def Fexists(model, location, timezero='any', target='any', quantile='any'):
    if (model, location) not in corr_dict.keys():
        return False
    
    flagTZ, flagTA, flagQU = False, False, False
    
    if timezero is not 'any':
        for tup in list(corr_dict[(model, location)]):
            try:
                if timezero == tup[0]:
                    flagTZ = True
                    break
            except:
                continue
    else:
        flagTZ = True
    
    if flagTZ == False:
        return False
        
    if target is not 'any':
        for tup in list(corr_dict[(model, location)]):
            try:
                if target == tup[1]:
                    flagTA = True
                    break
            except:
                continue
    else:
        flagTA = True
        
    if flagTA == False:
        return False
        
    if quantile is not 'any':
        for tup in list(corr_dict[(model, location)]):
            try:
                if quantile == tup[2]:
                    flagQU = True
                    break
            except:
                continue
    else:
        flagQU = True
    
    if flagQU == False:
        return False
        
    return True
        

# Examples of usage of Fexists:
# Fexists(model='UT-Mobility', location='Connecticut')
# Fexists('UT-Mobility', 'Connecticut', timezero='2020-06-08')
# Fexists('UT-Mobility', 'Connecticut', timezero='2020-06-08', target='inc hospitalized')
# Fexists('UT-Mobility', 'Connecticut', timezero='2020-06-08', quantile = '0.1')
# Fexists('UT-Mobility', 'Connecticut', quantile = '0.2')
# Fexists('UT-Mobility', 'Connecticut', timezero='2020-06-08', target='inc death', quantile='0.95')





