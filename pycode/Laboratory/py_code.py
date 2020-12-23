from scipy.io import loadmat
import math
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


x = np.arange(43)
y = np.full((43), 0)
y= np.zeros(43)
bench = np.full((5, 45), 0)
for i in range(0,41):
    y[i] = tensor['dr'].item(i)
#print(x,y)

for h in range(1, 5):
    w = 5
    for t in range(1,len(tensor['dr'])-w+1):
        #print(x[t:t+w], y[t:t+w])
        poly = np.poly1d(np.polyfit(x[t:t+w], y[t:t+w], 2))
        bench[h,t+w+h-1] = max(y[t+w-1], poly(t+w+h-1))
        #print(poly[t+w+h-1])
        
print(bench[1,0:41])
print(bench[2, 0:41])
print(bench[3, 0:41])
print(bench[4, 0:41])

error_tensor = np.full((3, 5, 41), 0)
loss_function_tensor = np.full((4, 4, 5, 41), 0.0)
d_tensor = np.full((4, 4, 5, 41), 0.0)
figure, axes = plt.subplots(nrows=4, sharex=True,sharey=True)
plt.xticks(rotation=90)
plt.grid()
max_for=5 
back=5
model_number = 0
forecast_models = ['Columbia_', 'JHU_', 'LANL_']

     



#forecast_models = ['JHU_']
for model in forecast_models:
    for forecast_interval in range(1,max_for):
        model_used = model+str(forecast_interval)
        #print(model_used)
        start = TT[model_used].first_valid_index()
        end = TT[model_used].last_valid_index() - back 
        poly = np.poly1d(np.polyfit(np.arange(
           start, end), TT['dr'][start:end].to_numpy(), 2))
        


        
    
        #print(poly)


        axes[forecast_interval-1].plot(TT['time'][start:end], TT['dr'][start:end],
                                       'x', TT['time'][start:end], TT[model_used][start:end], '-', TT['time'][start:end], poly(np.arange(start, end)), '--')
        axes[forecast_interval-1].grid()

        for j in range(start, end+back+1):
            error_tensor[model_number, forecast_interval,j] = TT['dr'][j]-TT[model_used][j]
            loss_function_tensor[model_number,0, forecast_interval, j] = (TT['dr'][j]-TT[model_used][j])**2
            loss_function_tensor[3, 0, forecast_interval, j] = (TT['dr'][j]-bench[forecast_interval,j])**2
            d_tensor[model_number, 0, forecast_interval, j] = loss_function_tensor[3, 0, forecast_interval, j]-loss_function_tensor[model_number,0, forecast_interval, j]

            #print(TT['dr'][j]-bench[forecast_interval, j])
            #print(j,poly(j))
            

            #loss_function_tensor[model_number,1, forecast_interval, j] = float(abs(TT['dr'][j]-TT[model_used][j])/(TT['dr'][j]))
            #loss_function_tensor[model_number,2, forecast_interval, j] = abs(TT['dr'][j]-TT[model_used][j])
            #loss_function_tensor[model_number,3, forecast_interval, j] = np.exp(50*abs(TT['dr'][j]-TT[model_used][j])/(TT['dr'][j])) - abs(TT['dr'][j]-TT[model_used][j])/(TT['dr'][j])-1

         #   print(loss_function_tensor[model_number, 3, forecast_interval, j])
        


    model_number = model_number+1



#print(error_tensor[0, ])
print(loss_function_tensor[3, 0, ])
print(d_tensor[0, 0, ])
#print(loss_function_tensor[0, 0, ]-loss_function_tensor[3, 0, ])
       

    
#plt.grid()
#plt.tick_params(axis='y', which='minor', bottom=False)
#plt.show()

#poly = np.poly1d(np.polyfit(x[0, 0:37], y[0, 0:37], 2))
#_ = plt.plot(x[0, 0:37], y[0, 0: 37], '.', x[0, 0: 41], poly(x[0, 0: 41]), '-')

#print((x[0, 0: 41]))
#print(poly)
#
