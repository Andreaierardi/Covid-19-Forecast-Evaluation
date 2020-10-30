import numpy as np
import pandas as pd
from datetime import date

## Real data ## 
state = ['US', 'California', 'Florida', 'New York', 'Texas']
w0 = 5
loss = ['MSE', 'MAE', 'MAPE', 'LINEX']

## True data: begins with "T"
# True Deaths: TD
TD = pd.read_csv("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Cumulative%20Deaths.csv")
Tstates = TD.location_name.unique()

# True Deaths Series getter
def getTDS(state, aggregateOn = 5):
     """Gets the true deaths series by state

    Parameters
    ----------
    state : str
        The state where deaths were recorded
    aggregateOn : int
        The weekday to aggregate the observations on.
        0 is Monday, 6 is Sunday.

    Returns
    -------
    pandas.Series : the series of true deaths of the specified state. Indexes are of class pandas.DatetimeIndex.
    """
     out = pd.Series(TD[TD['location_name'] == state].iloc[:,3].values,
                    index = pd.to_datetime(TD[TD['location_name'] == state].iloc[:,0].values, format="%Y-%m-%d"),
                    name = state + ": Cumulative deaths"
                   )
     if(aggregate):
          out = out[out.index.weekday == aggregateOn]
     return(out)

# # shift series to first non-zero occurence
# daily_s = daily_s[daily_s>0]
# # switch aggregation range to weekly (every Saturday)
# D = daily_s[daily_s.index.weekday == 5]


## Forecast data: begins with "F"
# Forecasted deaths: FD
FD = pd.read_csv('https://www.cdc.gov/coronavirus/2019-ncov/covid-data/files/2020-10-19-model-data.csv')
Fmodels = FD.model.unique()
Fstates = FD.location_name.unique()


# Forecast Deaths Series getter
def getFDS(model, state, Fdate):
     """Gets the forecasted deaths series by model, state and forecast date

    Parameters
    ----------
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
     out = FD[(FD.model == model) & (FD.location_name == state) & (FD.forecast_date == Fdate)]
     if( out.empty ):
          return None
     out = pd.DataFrame(out.iloc[:,5:10].values,
                    columns = out.columns[5:10],
                    index = pd.to_datetime(out.iloc[:,3], format="%Y-%m-%d")
                   )
     
     return out
     





# prova1 = pd.ExcelFile('Matlab to python/data_models-Florida.xlsx')

# prova1.sheet_names

# prova2 = prova1.parse('Ensamble')
# prova2