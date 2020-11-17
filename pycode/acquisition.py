import numpy as np
import pandas as pd
from datetime import date

## Real data: begins with "R"
# Real Deaths: RD
RD = pd.read_csv("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Cumulative%20Deaths.csv",  low_memory=False)
# Real Cases: RC
RC = pd.read_csv("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Cumulative%20Cases.csv", low_memory=False)

Rstates = RD.location_name.unique()

# Real Series getter
def getRS(type, state, aggregateOn = 5):
    """Gets the real cases or deaths series by state

    Parameters
    ----------
    type : str
        'C' for cumulative cases. 
        'D' for cumulative deaths.
    state : str
        The state where deaths were recorded
    aggregateOn : int or bool
        The weekday to aggregate the observations on.
        0 is Monday, 6 is Sunday.
        Set to false to prevent aggregation.

    Returns
    -------
    pandas.Series : the series of real cases or deaths of the specified state. Indexes are of class pandas.DatetimeIndex.
    """
    if(type == 'C'):
        out = pd.Series(RC[RC['location_name'] == state].iloc[:,3].values,
          index = pd.to_datetime(RC[RC['location_name'] == state].iloc[:,0].values, format="%Y-%m-%d"),
          name = state + ": Cumulative cases")
    elif(type == 'D'):
        out = pd.Series(RD[RD['location_name'] == state].iloc[:,3].values,
                    index = pd.to_datetime(RD[RD['location_name'] == state].iloc[:,0].values, format="%Y-%m-%d"),
                    name = state + ": Cumulative deaths"
        )
        if(aggregateOn is not False):
            out = out[out.index.weekday == aggregateOn]

    return(out)

# Example: getRS('D',Rstates[1])

# # shift series to first non-zero occurence
# daily_s = daily_s[daily_s>0]
# # switch aggregation range to weekly (every Saturday)
# D = daily_s[daily_s.index.weekday == 5]


## Forecast data: begins with "F"
# Forecasted cases: FC
FC = pd.read_csv("https://www.cdc.gov/coronavirus/2019-ncov/downloads/cases-updates/2020-10-19-all-forecasted-cases-model-data.csv")
# Forecasted deaths: FD
FD = pd.read_csv('https://www.cdc.gov/coronavirus/2019-ncov/covid-data/files/2020-10-19-model-data.csv')

Fmodels = FD.model.unique()
Fstates = FD.location_name.unique()

# Forecast Series getter
def getFS(type, model, state, Fdate):
    """Gets the forecasted deaths series by model, state and forecast date

    Parameters
    ----------
    type : str
        'C' for cumulative cases. 
        'D' for cumulative deaths.
    model : str
        The model of the forecast
    state : str
        The target state of the forecast
    Fdate : str or datetime
        The date when the forecast was performed. If a string, provide the format '%Y-%m-%d'.

    Returns
    -------
    pandas.DataFrame
        a data frame containing 5 series:
           - point series
           - 2.5% quantile
           - 25% quantile
           - 75% quantile
           - 97.5% quantile
        Indexes are of class pandas.DatetimeIndex.
    """
    if(type == 'C'):
        out = FC[(FC.model == model) & (FC.location_name == state) & (FC.forecast_date == Fdate)] 
    elif(type == 'D'):
        out = FD[(FD.model == model) & (FD.location_name == state) & (FD.forecast_date == Fdate) & FD.target.apply(str.endswith, args=('cum death',0))]
    else:
        return None
    if( out.empty ):
        return None
    out = pd.DataFrame(out.iloc[:,-5:].values,
                columns = out.columns[-5:],
                index = pd.to_datetime(out.iloc[:,3], format="%Y-%m-%d")
                   )
     
    return out
     
# Example: getFS('C', Fmodels[1], Fstates[1], FD.forecast_date[1])




# prova1 = pd.ExcelFile('Matlab to python/data_models-Florida.xlsx')

# prova1.sheet_names

# prova2 = prova1.parse('Ensamble')
# prova2
