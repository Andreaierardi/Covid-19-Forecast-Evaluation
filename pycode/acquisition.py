import numpy as np
import pandas as pd
from datetime import date

state = ['US', 'California', 'Florida', 'New York', 'Texas']
w0 = 5
loss = ['MSE', 'MAE', 'MAPE', 'LINEX']

raw_data = pd.read_csv("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Cumulative%20Deaths.csv")

raw_data.columns

i = 0

daily_s = pd.Series(raw_data[raw_data['location_name'] == state[i] ].iloc[:,3].values,
              index = pd.to_datetime(raw_data[raw_data['location_name'] == state[i] ].iloc[:,0].values, format="%Y-%m-%d")
                   )

# shift series to first non-zero occurence
daily_s = daily_s[daily_s>0]

# switch aggregation range to weekly (every Saturday)
s = daily_s[daily_s.index.weekday == 5]

prova1 = pd.ExcelFile('Matlab to python/data_models-Florida.xlsx')

prova1.sheet_names

prova2 = prova1.parse('Ensamble')
prova2