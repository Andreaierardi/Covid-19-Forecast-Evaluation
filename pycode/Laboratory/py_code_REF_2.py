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
from scipy import stats

TT=pd.read_excel('TT_vector.xlsx') 
size=len(TT['dr'])

forecast_range=4+1 #insert the nuber of  forecast interval plus 1 
number_of_models=9 #insert the number of models 
forecast_models = ['Ensamble_', 'Columbia_', 'JHU_',
                   'LANL_', 'MIT_', 'MOBS_', 'UCLA_', 'UMASS-MB_', 'YYG_'] #Insert the name of the model + _ at the end
number_of_loss_functions=4 #inster the number of loss functions that are going to be used *TO BE IMPLENTED*

def TD_Bartlett(Z,K):
    nlags=0
    T = K
    A = Z - Z.mean(axis=1, keepdims=True)
    sample_var = np.dot(A,A.T)/T
    omegahat = sample_var
    lag=forecast_range-1

    for ii in range(1,lag):
        gamma = ((np.dot(A[:, ii: T+1], A[:, 0:T-ii].T))+ np.dot(A[:, 0:T-ii], A[:, ii: T+1].T))/T
        weights= 1- (ii/(lag-1))
        omegahat = omegahat + np.dot(weights,gamma)
    return(omegahat)


x = np.arange(size+2)
y = np.full((size+2), 0)
y= np.zeros(size+2)
bench = np.full((forecast_range, size+forecast_range-1), 0)
for i in range(0,size):
    y[i] = TT['dr'][i]
#print(x,y)

for h in range(1, forecast_range):
    w = 5
    for t in range(1,len(TT['dr'])-w+1):
        poly = np.poly1d(np.polyfit(x[t:t+w], y[t:t+w], 2))
        bench[h,t+w+h-1] = max(y[t+w-1], poly(t+w+h-1))

        
error_tensor = np.full((number_of_models+2, forecast_range, size), 0)
loss_function_tensor = np.full(
    (number_of_models+2, number_of_loss_functions, forecast_range, size), 0.0)
d_tensor = np.full(
    (number_of_models+2, number_of_loss_functions, forecast_range, size), 0.0)
figure, axes = plt.subplots(nrows=forecast_range-1, sharex=True, sharey=True)
plt.xticks(rotation=90)
plt.grid()

back = forecast_range
model_number = 0



#Calculations of the error tensor, loss function tensor and d tensor 
     
for model in forecast_models:
    for forecast_interval in range(1, forecast_range):
        model_used = model+str(forecast_interval)
        #print(model_used)
        start = TT[model_used].first_valid_index()
        end = TT[model_used].last_valid_index() - back 
        poly = np.poly1d(np.polyfit(np.arange(
           start, end), TT['dr'][start:end].to_numpy(), 2))


        axes[forecast_interval-1].plot(TT['time'][start:end], TT['dr'][start:end],
                                       'x', TT['time'][start:end], TT[model_used][start:end], '-', TT['time'][start:end], poly(np.arange(start, end)), '--')
        axes[forecast_interval-1].grid()

        for j in range(start, end+back+1):
            error_tensor[model_number, forecast_interval,j] = TT['dr'][j]-TT[model_used][j]
            loss_function_tensor[model_number,0, forecast_interval, j] = (TT['dr'][j]-TT[model_used][j])**2
            loss_function_tensor[number_of_models+1, 0, forecast_interval, j] = (
                TT['dr'][j]-bench[forecast_interval, j])**2
            d_tensor[model_number, 0, forecast_interval, j] = loss_function_tensor[number_of_models+1, 0, forecast_interval, j]-loss_function_tensor[model_number,0, forecast_interval, j]

    model_number = model_number+1

model_number = 0


T = end+back-start+1

#The tensor that will contain the WPE and WCE values
test_tensor = np.full((2, number_of_models, forecast_range-1), 0.0)


#Calculation of WCE values 
for model in forecast_models:
    for forecast_interval in range(1, forecast_range):
        model_used = model+str(forecast_interval)
        start = TT[model_used].first_valid_index()
        end = TT[model_used].last_valid_index()
        num = np.sqrt(T)*np.mean(d_tensor[model_number, 0, forecast_interval,start:end+1])
        den = TD_Bartlett(
            d_tensor[0:number_of_models, 0, forecast_interval, start:end+1], T)
        test_tensor[0,model_number, forecast_interval-1] = num / math.sqrt(den[model_number, model_number])
        
    model_number = model_number+1

b = math.floor((T)**(1/2))/T

CV_WCE_b_97 = 1.9600 + 2.9694*b + 0.4160*b**2 - 0.5324*b**3
CV_WCE_b_95 = 1.6449 + 2.1859*b + 0.3142*b**2 - 0.3427*b**3
CV_WCE_b_90 = 1.2816 + 1.3040*b + 0.5135*b**2 - 0.3386*b**3

wpeband=math.floor((T)**(1/3))

M = dft(T)

d_tensor_F = np.full((forecast_range, number_of_models, T), 0.0) #Fourier transformed tensor

model_number = 0

#Calculation of WPE values

for model in forecast_models:
    for forecast_interval in range(1, forecast_range):
        model_used = model+str(forecast_interval)
        start = TT[model_used].first_valid_index()
        end = TT[model_used].last_valid_index()

        num = np.sqrt(
            T)*np.mean(d_tensor[model_number, 0, forecast_interval, start:end+1])
        d_tensor_F[forecast_interval, ] = np.absolute(fft(
            d_tensor[0:number_of_models, 0, forecast_interval, start:end+1]))**2/(2*math.pi*T)
        test_tensor[1, model_number, forecast_interval-1] = num / math.sqrt(sum(d_tensor_F[forecast_interval, model_number, 1:wpeband+1])/wpeband*2*math.pi)
    model_number = model_number+1

print("WCE",test_tensor[0,])
print("WPE", test_tensor[1,])

print("Critical values WCE ",CV_WCE_b_97, CV_WCE_b_95, CV_WCE_b_90)
print("Critical values WPE ",stats.t.ppf(0.90, 2*wpeband), stats.t.ppf(0.95, 2*wpeband), stats.t.ppf(0.975, 2*wpeband))

