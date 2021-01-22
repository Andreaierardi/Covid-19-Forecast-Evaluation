import pandas as pd
import pyarrow.parquet as pq
import datetime as dt

f = open('data/unique_lists/locations.pkl', 'rb')
locations = pickle.load(f)
f.close()
locations_inv = {v: k for k, v in locations.items()}

f = open('data/unique_lists/targets.pkl', 'rb')
targets = pickle.load(f)
f.close()

f = open('data/unique_lists/timezeros.pkl', 'rb')
timezeros = pickle.load(f)
f.close()

f = open('data/unique_lists/models.pkl', 'rb')
models = pickle.load(f)
f.close()

f = open('data/unique_lists/corr_dict.pkl', 'rb')
corr_dict = pickle.load(f)
f.close()

quantiles = (0.99, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.01, 0.975, 0.025)

models = list(pd.read_csv("data/unique_lists/models.csv")['models'])

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

    data = pd.read_parquet("data/"+str(timezero)+".parquet")
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
    deltadays = out['target'].str.extract('(\d+)')[0].astype(int).apply(dt.timedelta)*7
    out[('time','')] = pd.to_datetime(out['timezero'], format="%Y-%m-%d") + deltadays
    out.set_index('time', inplace=True)

    return out


# Example: getFS(type="inc case", model="all", state="all", timezero="2020-04-06")
# Example: getFS(type="cum death", model="LANL-GrowthRate", state="Texas", timezero="2020-04-06")



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