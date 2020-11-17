import numpy as np
import pandas as pd
from datetime import date

### NOTE ON LOCATION NAMES ###
# - Location names are contained in the column named 'location_name' of each dataset
# - Datasets FC, RC, RD initially contained series of all states and all counties. 
# - forecast data's string for national location is 'National'. 
# - Real data's string for national location is 'US'.
# - Previously selected locations (and therefore to be used) are contained in the list named 'states'.

# Define the areas of interest 
states = ['US', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
              'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
              'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
              'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
              'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
              'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
              'West Virginia', 'Wisconsin', 'Wyoming', 'District of Columbia', 'Puerto Rico', 'Guam', 'Virgin Islands',
              'Northern Mariana Islands', 'American Samoa']

## Forecast data: begins with "F"
# Forecasted cases: FC
FC = pd.read_csv("https://www.cdc.gov/coronavirus/2019-ncov/downloads/cases-updates/2020-10-19-all-forecasted-cases-model-data.csv")[lambda x: x.location_name.isin(states+['National'])]
# Forecasted deaths: FD
FD = pd.read_csv('https://www.cdc.gov/coronavirus/2019-ncov/covid-data/files/2020-10-19-model-data.csv')[lambda x: x.location_name.isin(states+['National'])]

# Define unique lists
Fmodels = list(np.unique(np.concatenate((FC.model.values, FD.model.values))))
Fstates = list(np.unique(np.concatenate((FC.location_name.values, FD.location_name.values))))
Fdates = list(np.unique(np.concatenate((FC.forecast_date.values, FD.forecast_date.values))))
# [i in states for i in Fstates]

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
    if(state == 'US'):
        state = 'National'
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
     
# Example: getFS('C', Fmodels[40], Fstates[0], Fdates[0])
# Example: getFS('D', Fmodels[0], Fstates[0], Fdates[0]) is None










#=================================================================================================================#
## Real data: begins with "R"
# Retrieve only the States (raw data also contains counties)

# Real Deaths: RD
RD = pd.read_csv("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Cumulative%20Deaths.csv")[lambda x: x.location_name.isin(states)]
# Real Cases: RC
RC = pd.read_csv("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Cumulative%20Cases.csv")[lambda x: x.location_name.isin(states)]

# Name of all
Rstates = list(np.unique(np.concatenate((RC.location_name.values, RD.location_name.values))))


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

# Example: getRS('D',states[0])

# Example: aa = getRS('D',states[0])
#          bb = getFS('D', Fmodels[0], states[0], Fdates[0])
#          bb.index.isin(aa.index)