from scipy.io import loadmat
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import pandas as pd

tensor = loadmat('sample_data.mat')
TT=pd.read_excel('TT_vector.xlsx')
#print(tensor['date'])

#print(len(tensor['dr'])+1)


#print(tensor['h'].item(0))


x = np.arange(41)
#y = np.full((41), 0)
y= np.zeros(41)
bench= np.zeros(44)
for i in range(0,41):
    y[i] = tensor['dr'].item(i)
#print(x,y)

for h in range(0, tensor['h'].item(0)):
    w = tensor['w0'].item(0)
    for t in range(1,len(tensor['dr'])-w+1):
        #print(x[t:t+w], y[t:t+w])
        poly = np.poly1d(np.polyfit(x[t:t+w], y[t:t+w], 2))
        bench[t+w+h-1] = max(y[t+w-1], poly[t+w-1+h])
        #print(poly,bench,x,y)

figure, axes = plt.subplots(nrows=4, sharex=True,sharey=True)
plt.xticks(rotation=90)
plt.grid()
max_for=5
forecast_models = ['Columbia_', 'JHU_', 'LANL_']
#forecast_models = ['JHU_']
for model in forecast_models:
    for forecast_interval in range(1,max_for):
        model_used = model+str(forecast_interval)
        print(model_used)
        start = TT[model_used].first_valid_index()
        end = TT[model_used].last_valid_index()

        #poly = np.poly1d(np.polyfit(np.arange(
            #start, end-forecast_interval), TT['dr'][start:end-forecast_interval].to_numpy(), 2))
        poly = np.poly1d(np.polyfit(np.arange(
            start, end), TT['dr'][start:end].to_numpy(), 2))
        #print(poly)
        axes[forecast_interval-1].plot(TT['time'][start:end+forecast_interval], TT['dr'][start:end+forecast_interval],
                                       'x', TT['time'][start:end+forecast_interval], TT[model_used][start:end+forecast_interval], '-', TT['time'][start:end+forecast_interval], poly(np.arange(start, end+forecast_interval)), '--')
        axes[forecast_interval-1].grid()
        

    
plt.grid()
plt.tick_params(axis='y', which='minor', bottom=False)
plt.show()

#poly = np.poly1d(np.polyfit(x[0, 0:37], y[0, 0:37], 2))
#_ = plt.plot(x[0, 0:37], y[0, 0: 37], '.', x[0, 0: 41], poly(x[0, 0: 41]), '-')

#print((x[3, 0: 41]))
#print(poly)
#
