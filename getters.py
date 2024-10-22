import pandas as pd
import datetime as dt
import bz2
import pickle
import _pickle as cPickle
import time

from zoltpy import util
import zoltpy
from zoltpy.connection import QueryType

import os

host = os.environ.get('Z_HOST')
username = os.environ.get('Z_USERNAME')
password = os.environ.get('Z_PASSWORD')

f = open('data/unique_lists/locations.pkl', 'rb')
locations = pickle.load(f)
f.close()
locations_inv = {v: k for k, v in locations.items()}
f = open('data/unique_lists/locations_abbr.pkl', 'rb')
locations_abbr = pickle.load(f)
f.close()

f = open('data/unique_lists/targets.pkl', 'rb')
targets = pickle.load(f)
f.close()

f = open('data/unique_lists/timezeros.pkl', 'rb')
timezeros = pickle.load(f)
f.close()

f = open('data/unique_lists/models.pkl', 'rb')
models = pickle.load(f)
f.close()

def decompress_pickle(file):
 data = bz2.BZ2File(file, 'rb')
 data = cPickle.load(data)
 return data
def get_project():
  conn = util.authenticate()
  print('\n* projects')
  project_name = 'COVID-19 Forecasts'
  project = [project for project in conn.projects if project.name == project_name][0]
  return project

#corr_dict = decompress_pickle('data/unique_lists/corr_dict.pkl')

quantiles = (0.99, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.01, 0.975, 0.025)

models = list(pd.read_csv("data/unique_lists/models.csv")['models'])

real_data = pd.read_parquet("data/real_data.parquet")

project = get_project()

# Forecast Series getter
def getFS(timezero, type="all", model="all", state="all"):
    """Gets the weekly forecasted series by model, state and forecast date

    Parameters
    ----------
    timezero : str or datetime
        The date when the forecast was performed. If a string, provide the format '%Y-%m-%d'. This argument is compulsory.
    type : str
        'cum case' for cumulative cases.
        'cum death' for cumulative deaths.
        'inc case' for incidental cases.
        'inc death' for incidental deaths.
        'hosp' for hospitalized.
        'all' for all types
    model : str
        The model of the forecast. Choose 'all' for returning every model.
    state : str
        The target state of the forecast (full name). Choose 'all' for returning every state.

    Returns
    -------
    pandas.DataFrame
        a data frame indexed by target date, including series:
           - point series
           - quantile series
        Columns are multi-indexed. To access a column use ('column_name', '') or ('quantile', '<perc>').
    """
    
    timezero_dt = pd.to_datetime(timezero, format="%Y-%m-%d")
    try:
        data = pd.read_parquet("data/"+str(timezero)+".parquet")
    except:
        return None
    n = len(data)
    c1 = data['target'].apply(str.endswith, args=(type, 0)) if type != "all" else pd.Series([True]*n)
    c2 = data['model'] == model if model != "all" else pd.Series([True]*n)
    c3 = data['unit'] == locations[state] if state != "all" else pd.Series([True]*n)

    data = data[c1 & c2 & c3]

    if (data.empty):
        return None

    # renaming duplicated columns
    data.rename(columns={"quantile": "q"}, inplace=True)
    # reshaping q column
    data.loc[data['q'].isna(),'q'] = ''
    # pivoting the orginal table
    out=data.pivot_table(index=["model","timezero","unit","target"], columns=["class","q"], values="value", aggfunc= 'first').reset_index()
    # adding the target date
    def next_weekday(d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return d + dt.timedelta(days_ahead)
    if(timezero_dt.weekday() > 0):
        out.insert(loc=3, column='forecast_date',
                   value = pd.to_datetime(out['timezero'], format="%Y-%m-%d").apply(lambda x: next_weekday(x, 0)))
    else:
        out.insert(loc=3, column='forecast_date',
                   value = pd.to_datetime(out['timezero'], format="%Y-%m-%d"))
                   
    start_saturday = out['forecast_date'].apply(lambda x: next_weekday(x, 5)) - dt.timedelta(7)
    deltadays = out['target'].str.extract('(\d+)')[0].astype(int).apply(dt.timedelta)*7
    out[('time','')] = start_saturday + deltadays
    
    out.set_index('time', inplace=True)

    return out


# Example: getFS(type="inc case", model="all", state="all", timezero="2020-04-06")
# Example: getFS(type="cum death", model="LANL-GrowthRate", state="Texas", timezero="2020-04-06")



def Fexists(model, location, timezero='all', target='all', quantile='all'):
    return True
    if model == "all" or location== "all":
        return True
    if (model, location) not in corr_dict.keys():
        return False

    flagTZ, flagTA, flagQU = False, False, False

    if timezero is not 'all':
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

    if target is not 'all':
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

    if quantile is not 'all':
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


def reshape_for_download(dataset):
    new = pd.DataFrame({
        'model': dataset['model'],
        'forecast_date': pd.to_datetime(dataset['timezero']).dt.strftime('%d/%m/%Y'),
        'target': dataset['target'],
        'target_week_end_date': dataset.index.strftime('%d/%m/%Y'),
        'location_name': dataset['unit'].replace(locations_inv),
        'point': dataset['point'],
    })
    
    for q in quantiles:
        qs = str(q)
        if ('quantile', qs) in dataset.columns:
            new[f'quantile_{qs}'] = dataset[('quantile', qs)]
        else:
            new[f'quantile_{qs}'] = None
    
    new.reset_index(drop=True, inplace=True)
    
    return new



def get_download(state, path, timezero="all", type="all", model="all"):
    """Gets the weekly forecasted series by model, state and forecast date

    Parameters
    ----------
    state : str
        The target state of the forecast (full name). This argument must be a single location.
    path : str
        Path where to write the xlsx file.
    timezero : str or datetime
        The date when the forecast was performed. If a string, provide the format '%Y-%m-%d'.
        'all' for all timezeros.
    type : str
        'cum case' for cumulative cases.
        'cum death' for cumulative deaths.
        'inc case' for incidental cases.
        'inc death' for incidental deaths.
        'hosp' for hospitalized.
        'all' for all types
    model : str
        The model of the forecast. Choose 'all' for returning every model.

    Returns
    -------
    pandas.DataFrame
        a data frame indexed by target date, including series:
           - point series
           - quantile series
    """
    
    writer = pd.ExcelWriter(path, engine='xlsxwriter')
    
    i = 0
    
    if timezero == "all" and model == "all" and type == "all" and type == "all":
        for curr_mod in models:
            print(f'writing {curr_mod}...')
            data = pd.DataFrame()
            for curr_date in timezeros:
                curr_date_s = str(curr_date)
                if Fexists(model=curr_mod, location=state, timezero=curr_date_s, target='all', quantile='all'):
                    try:
                        data_new = getFS(timezero=curr_date_s, type='all', model=curr_mod, state=state)
                        if data_new is not None:
                            data_new = reshape_for_download(data_new)
                            data = data.append(data_new)
                    except:
                        continue
            if(len(data) != 0):
                data.to_excel(excel_writer=writer, sheet_name=curr_mod, index=False) 
            
            # Retrieve only first models...:
            #i = i+1
            #if i >= 3:
            #    break
            
    
    else:
        #data = getFS(timezero=timezero, type=type, model=model, state=state)
        #data = reshape_for_download(data)
        #data.to_excel(excel_writer=path, sheet_name=model, index=False)
        return None
    
    writer.save()
    print('Done!')




def getRS(timezero, type, state, window):
    """Gets the real cases, deaths or hospitalized series by state

    Parameters
    ----------
    timezero : str or datetime
        The start date for weekly aggregation. If a string, provide the format '%Y-%m-%d'.
    type : str
        'cum case' for cumulative cases.
        'cum death' for cumulative deaths.
        'inc case' for incidental cases.
        'inc death' for incidental deaths.
        'curr hospitalized' for currently hospitalized.
        'all' for all types
    state : str
        The desired state for COVID statistics (full name). Choose 'all' for returning every state.
    window : int
        The length of the time window of data to be retrieved in weeks.

    Returns
    -------
    pandas.Series : the series of real cases, deaths or hospitalized of the specified state.
                    For cumulative or current type, data is taken every week for a total of <window> weeks.
                    For incidental type, data is aggregated every week starting from timezero+1 for a total of <window> weeks.
    """

    data = pd.read_parquet("data/real_data.parquet")
    if(isinstance(timezero, str)):
        try:
            timezero = dt.datetime.strptime(str(timezero), "%Y-%m-%d")
        except Exception as e:
            print(e)
            return None

    last_date = dt.datetime.strptime(data.date[0],"%Y-%m-%d")

    while(timezero+dt.timedelta(7*window)) > last_date:
             window = window -1
                    #print(data_len)

    # state filter
    data = data[data['state'] == locations_abbr[state]]

    # date filter
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)

    try:
        if('cum' in type or 'curr' in type):
            datelist = [timezero + dt.timedelta(7)*(1+i) for i in range(window)]
            out = data.loc[datelist,type]
        else:
            datelist = [timezero + dt.timedelta(1+i) for i in range(7*window)]
            out = data.loc[datelist,type]
            # aggregate by week, starting on timezero+1
            out = out.groupby(lambda x: timezero + dt.timedelta(((x-timezero).days-1) // 7 + 1)*7).sum()
    except Exception as e:
        print(e)
        return None

    return out


# Example: out = getRS('2020-05-20', type='inc case', state='Alabama', window=4)

def suggestion(state, model):
    query = {'units': [locations[state]],'models': [model],'targets':targets}
    print(query)

    try:
      job =  project.submit_query(QueryType.FORECASTS,query)
      busy_poll_job2(job)  # does refresh()
      rows = job.download_data()
      print(f"- got {len(rows)} forecast rows as a dataframe.")
      data = util.dataframe_from_rows(rows)
      if len(data ) > 0:
        #print(data)
        tm = data.timezero.unique()
        tr = data.target.unique()

        print(tm)
        print(tr)
        return (list(tm),list(tr))
      else:
        return None    

    except:
      print("Something went wrong for ",state)
      return None
     # missing.append(date)


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

        time.sleep(0.5)
        job.refresh()

