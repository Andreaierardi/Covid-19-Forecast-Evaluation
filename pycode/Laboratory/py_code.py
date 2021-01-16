from scipy.io import loadmat
import math
import statsmodels.api as sm
import numpy as np
import pylab 
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator)
import pandas as pd
from scipy.linalg import dft
from scipy.fft import fft

tensor = loadmat('sample_data.mat')
TT=pd.read_excel('TT_vector.xlsx')


def TD_Bartlett(Z):
    nlags=0
    #waceband=sqrt(41)
    T = 15
    A = Z - Z.mean(axis=1, keepdims=True)
    sample_var = np.dot(A,A.T)/T
    #print("sample_var",sample_var)
    omegahat = sample_var
    lag=4

    for ii in range(1,lag):
        gamma = ((np.dot(A[:, ii: T+1], A[:, 0:T-ii].T))+ np.dot(A[:, 0:T-ii], A[:, ii: T+1].T))/T
        weights= 1- (ii/(lag-1))
        omegahat = omegahat + np.dot(weights,gamma)
    return(omegahat)



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
        
#print(bench[1,0:41])
#print(bench[2, 0:41])
#print(bench[3, 0:41])
#print(bench[4, 0:41])

error_tensor = np.full((11, 5, 41), 0)
loss_function_tensor = np.full((11, 4, 5, 41), 0.0)
d_tensor = np.full((11, 4, 5, 41), 0.0)
figure, axes = plt.subplots(nrows=4, sharex=True,sharey=True)
plt.xticks(rotation=90)
plt.grid()
max_for=5 
back=5
model_number = 0
forecast_models = ['Ensamble_','Columbia_', 'JHU_', 'LANL_','MIT_','MOBS_','UCLA_','UMASS-MB_','YYG_']

     



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
            loss_function_tensor[10, 0, forecast_interval, j] = (TT['dr'][j]-bench[forecast_interval,j])**2
            d_tensor[model_number, 0, forecast_interval, j] = loss_function_tensor[10, 0, forecast_interval, j]-loss_function_tensor[model_number,0, forecast_interval, j]

        #num = np.sqrt(15)*np.mean(d_tensor[model_number, 0, forecast_interval,12+forecast_interval-1:27+forecast_interval-1])
        #WCEb = TD_Bartlett(d_tensor[0:9, 0, 1, 12:27])
        #print(np.sqrt(WCEb))
        #test_1 = num/np.sqrt(WCEb)
        #print(test_1)
        #print(model, forecast_interval, num, forecast_interval)

        #num = np.sqrt(15)*np.mean(d_tensor[model_number, 0, forecast_interval,12+forecast_interval-1:27+forecast_interval-1])



            #print(TT['dr'][j]-bench[forecast_interval, j])
            #print(j,poly(j))
            

            #loss_function_tensor[model_number,1, forecast_interval, j] = float(abs(TT['dr'][j]-TT[model_used][j])/(TT['dr'][j]))
            #loss_function_tensor[model_number,2, forecast_interval, j] = abs(TT['dr'][j]-TT[model_used][j])
            #loss_function_tensor[model_number,3, forecast_interval, j] = np.exp(50*abs(TT['dr'][j]-TT[model_used][j])/(TT['dr'][j])) - abs(TT['dr'][j]-TT[model_used][j])/(TT['dr'][j])-1

         #   print(loss_function_tensor[model_number, 3, forecast_interval, j])
        


    model_number = model_number+1

model_number = 0

#print(WCEb)

test_tensor = np.full((2,9,4), 0.0)

for model in forecast_models:
    for forecast_interval in range(1, max_for):
        model_used = model+str(forecast_interval)
        num = np.sqrt(15)*np.mean(d_tensor[model_number, 0, forecast_interval,12+forecast_interval-1:27+forecast_interval-1])
        den = TD_Bartlett(d_tensor[0:9, 0, forecast_interval, 12+forecast_interval-1:27+forecast_interval-1])
        #print(num)
        #print(den[model_number, model_number])
        test_tensor[0,model_number, forecast_interval-1] = num / math.sqrt(den[model_number, model_number])
        
    model_number = model_number+1

b = 3/15

CV_WCE_b_97 = 1.9600 + 2.9694*b + 0.4160*b**2 - 0.5324*b**3
CV_WCE_b_95 = 1.6449 + 2.1859*b + 0.3142*b**2 - 0.3427*b**3
CV_WCE_b_90 = 1.2816 + 1.3040*b + 0.5135*b**2 - 0.3386*b**3


#print(test_tensor_1)
#print(CV_WCE_b_97, CV_WCE_b_95, CV_WCE_b_90)
#print(TD_Bartlett(d_tensor[0:9, 0, 1, 12:27]))



wpeband=2

M = dft(15)
#print(M)


#d_tensor_F = M @ d_tensor[0:9, 0, 1,12:27]


d_tensor_F = np.full((5, 9, 15), 0.0)

model_number = 0

for model in forecast_models:
    for forecast_interval in range(1, max_for):
        model_used = model+str(forecast_interval)
        num = np.sqrt(15)*np.mean(d_tensor[model_number, 0, forecast_interval,12+forecast_interval-1:27+forecast_interval-1])
        d_tensor_F[forecast_interval, ] = np.absolute(fft(
            d_tensor[0:9, 0, forecast_interval, 12+forecast_interval-1:27+forecast_interval-1]))**2/(2*math.pi*15)
        test_tensor[1, model_number, forecast_interval-1] = num / math.sqrt(sum(d_tensor_F[forecast_interval, model_number, 1:wpeband+1])/wpeband*2*math.pi)
    model_number = model_number+1

print(test_tensor)

#print(d_tensor_F)
    #pdm = (np.absolute(d_tensor_F[forecast_interval, ])**2)/(2*3.1415*15)
#print("peppo", d_tensor_F)

#print("peppo",np.mean(d_tensor[0, 0, 1, ]))
#print(loss_function_tensor[0, 0, ]-loss_function_tensor[3, 0, ])
       

    
#plt.grid()
#plt.tick_params(axis='y', which='minor', bottom=False)
#plt.show()

#poly = np.poly1d(np.polyfit(x[0, 0:37], y[0, 0:37], 2))
#_ = plt.plot(x[0, 0:37], y[0, 0: 37], '.', x[0, 0: 41], poly(x[0, 0: 41]), '-')

#print((x[0, 0: 41]))
#print(poly)
#

