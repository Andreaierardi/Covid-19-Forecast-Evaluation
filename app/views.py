# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.http import JsonResponse

from django.http import StreamingHttpResponse

import pandas as pd
import numpy as np
import json
import re
import datetime
import time
import os
import csv
#import pycode.acquisition as acquisition
import getters as gets

#============= VARIABLE INITIALISATION  ====================
global lock_job
lock_job = True

values = list()
labels = list()
states = list(gets.locations)
models = sorted(gets.models)
dates = []

quant = gets.quantiles
quantiles = []
for i in quant[len(quant)//2:len(quant)]:
            for j in quant[0:len(quant)//2+1]:
                #print("===_", i,j)
                if float(i)+float(j) == 1:
                    if(float(i)> float(j)):
                        quantiles.append(str(i)+"-"+str(j))
                    else:
                        quantiles.append(str(j)+"-"+str(i))
quantiles = sorted(quantiles, reverse = True)
all_quant = quantiles
all_dates = []
for d in gets.timezeros:
   dates.append(d.strftime("%Y-%m-%d"))
   all_dates.append(d.strftime("%Y-%m-%d"))


today = datetime.datetime.today()
last_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1) -  datetime.timedelta(7)
#try: 
#    last_date = datetime.datetime.strptime(gets.real_data.date[0] ,"%Y-%m-%d")
#    print("LAST monday", last_monday.date())
#    print("LAST monday of real data", last_date.date())
#    if(last_date.date() < last_monday.date()):
#        import acquisition
#    else:
#        print("Real data is already up-to-date")
#except Exception as e:
#            print(e)
#            print("ERROR IN FINDING new real data")
#try:
#    data = gets.getFS(timezero= dates[0])
#
#except:
#   
#    import acquisition as acq
#
#    limit = dates[0]
#    print("LIMIT: ",limit)
#    parquet_list = sorted(os.listdir("data"))
#    parquet_list = parquet_list[0:len(parquet_list)-1]
#    print("\nPARQUET LIST\n\n\n", parquet_list,"\n\n===========")
#    last_parquet = parquet_list[len(parquet_list)-2].split(".parquet")[0]
#    print("LAST PARQUET:" ,last_parquet)
#    ind = dates.index(last_parquet)
#
#    new_dates = dates[0:ind]
#    print("NEW DATES:\n",new_dates)
#    acq.retrieve_data(new_dates)
#    data = gets.getFS(timezero= dates[0])

targs = gets.targets

all_targs = []

for i in gets.targets:
     x = i.split(" ")
     string = x[-2]+" "+x[-1]
     if not string in all_targs:
             all_targs.append(string)
all_targs.append("cum case")
locations_inv = {v: k for k, v in gets.locations.items()}



#============= UTILITY FUNCTIONS ====================

"""
Gets the radio buttons avaiable for the selected state to pass to the JS client

    Parameters
    ----------
    filter_FC : pandas.DataFrame
        The dataframe for the cases filtered by State
    filter_FD : pansad.dataframe
        The dataframe for the deaths filtered by State

    Returns
    -------
    list
        a list containing two list:
            - list of strings of radio buttons to activate
            - list of stirngs of radio buttons to deactivate
"""
def radio_filtering(filter_FC):
    radio_filter = []

    for i in ["cum case","inc case"]:
        if not filter_FC[filter_FC.target.apply(str.endswith, args=(i, 0)) == True].model.unique().tolist():
            radio_filter.append(i)

    radio_activate = []
    for i in ["cum case","inc case","cum death","inc death"]:
        if i not in radio_filter:
            radio_activate.append(i)
    return (radio_filter, radio_activate)




""" Convert a list of date string to a list of time passed from the Unix Epoch (00:00:00 UTC on 1 January 1970) to pass in a correct form to the JS client

    Parameters
    ----------
    lis : list
        The list containing the dates in string format


    Returns
    -------
    list
        a list of string containing the converted date to Unix Epoch time

"""
def convert_dateTotime(lis):
    first_date = datetime.datetime(1970, 1, 1)
    return [ int( (datetime.datetime.strptime(d, "%Y-%m-%d") - first_date).total_seconds())*1000 for d in lis ]


#============= DJANGO SERVER FUNCTIONS  ====================

"""
Get the forecast data for the selected state, team and type to then plot in the JS client

Parameters
----------
request : django.http.HttpResponse
    The request Object from the JS client
state: str
    the string for the selected state
team: str
    the string for the selected team
type: str
    the string for the selected type
date: str
    the string for the selected date

Returns
-------
django.http.JsonResponse:
    the response to the client in JSON format

"""




def get_suggestions(request, state, team):


    if(team == "all" or state == "all"):
            targs = all_targs
            quantiles = all_quant
            dates = all_dates
            radio_activate = targs
            err = "no"

            radio_filter = []
            for i in all_targs:
                if i not in radio_activate:
                    radio_filter.append(i)

            context = { "quantiles":quantiles, "radio_filter": radio_filter, "radio_activate":radio_activate, "errors":err,"models":models, "states": states, "dates":dates}
            return JsonResponse(context)
    
    else:
        sug = gets.suggestion(state=state, model = team)
        print(sug)
        if sug is not None:
            print("\n\n\n\n ============================= \n\n\n")
            dates = sug[0]
            tmp_targs = sug[1]
            quantiles = all_quant

            targs = []
            for tar in tmp_targs:
                sp = tar.split(" ")
                targs.append(sp[-2]+" "+sp[-1])
            targs = list(dict.fromkeys(targs))
        else:
            err = "No information found for the selected location and forecast team"
            print(err)
            return JsonResponse({"errors": err})

        dates = sorted(dates, reverse = True)
        quantiles = sorted(quantiles, reverse = True)

        print(dates)
        print(targs)
        print(quantiles)
        radio_activate = targs

        radio_filter = []
        for i in all_targs:
            if i not in radio_activate:
                radio_filter.append(i)

        print("\n\n\n\n\n\n========= \n\n")
        print(radio_filter)
        print("\n\nACT\n")
        print(radio_activate)

        err = "no"
        context = { "quantiles":quantiles, "radio_filter": radio_filter, "radio_activate":radio_activate, "errors":err,"models":models, "states": states, "dates":dates}
        return JsonResponse(context)
    

def getforecastplot(request, state, team,type,date,quantile):


    print("Parameter from Get request")
    print(state)
    print(team)
    print(type)
    print(date)
    print(quantile)
    if(gets.Fexists(model = team, location = state)):

        if(gets.Fexists(model = team, location = state, target = type, timezero = date )):
                data = gets.getFS(type=type, model=team, state=state, timezero=date)
                if(data is None):
                    err = "NotFound"
                    print(err)
                    return JsonResponse({"errors": err})
              
                data_len =len(data)
                real_data = gets.getRS(timezero= date, type = type , state= state, window= data_len)

                if (real_data is None):
                        err = "Real data NotFound"
                        print(err)
                        return JsonResponse({"errors": err})
                data = data.sort_index()
                real_data = real_data.sort_index()

                color= '#ba2116'
                real_color = '#2f7ed8'
                colorq = "#ffcc66"


                name= state +" \n"+ team +" \n"+  type +" \n"+  date
                real_name = "Real cases"
                print(name)

                #print(quantile)
                quant1 , quant2 = quantile.split("-")
                #print(quant1," and ", quant2)


                names1 = team
                names2= state
                namesq =  "Confidence Intervals:"+quantile
                index = data.index.strftime("%Y-%m-%d").tolist()
                err = "no"

                values = pd.to_numeric(data.point,downcast='integer').tolist()
                for i in range(len(values)):
                    values[i] = int(values[i])

                #print(values)


                real_values = list(real_data.values)
                for i in range(len(real_values)):
                    real_values[i] = int(real_values[i])

                #print(real_values)
                index = convert_dateTotime(index)
                series = list(zip(index,values))

                print("SERIES OBTAINED")
                print(series)


                real_series = list(zip(index, real_values))
                quantiles = []

                if len(list(data.values[0])) > 5:
                    quant = list(data[('quantile')])
                    quant_list = []
                    for i in quant[len(quant)//2:len(quant)]:
                                for j in quant[0:len(quant)//2+1]:
                                    #print("===_", i,j)
                                    if float(i)+float(j) == 1:
                                        if(float(i)> float(j)):
                                            quantiles.append(str(i)+"-"+str(j))
                                        else:
                                            quantiles.append(str(j)+"-"+str(i))
                                        quant_list.append(str(i))
                                        quant_list.append(str(j))

                    quantiles = sorted(quantiles, reverse =True)
                  #  print("PREE ======\n\n",quantiles)
                   # print("\n\n\n\n\n\n---\n\n\n\n")
                   # print("quant1:",quant1)
                   # print("quant_list:",quant_list)
                    if (quant1 is not None) and (not quant1 == ""):
                        if quant1 in quant_list:
                            qs = data[("quantile"),(quant1)]
                            qs2 = data[("quantile"),(quant2)]
                            for i in range(len(qs)):
                                qs[i] = int(float(qs[i]))
                                qs2[i] = int(float(qs2[i]))
                                seriesqs = list(zip(index,qs,qs2))
                                print(seriesqs)
                        else:
                            print("QUANT does not exist - auto selection")
                            quant1 = quant_list[0]
                            quant2 = quant_list[1]
                            qs = data[("quantile"),(quant1)]
                            qs2 = data[("quantile"),(quant2)]
                            for i in range(len(qs)):
                                qs[i] = int(float(qs[i]))
                                qs2[i] = int(float(qs2[i]))
                                seriesqs = list(zip(index,qs,qs2))
                                print(seriesqs)
                    else:
                        print("QUANT NONE")
                        quant1 = quant_list[0]
                        quant2 = quant_list[1]
                        qs = data[("quantile"),(quant1)]
                        qs2 = data[("quantile"),(quant2)]
                        for i in range(len(qs)):
                            qs[i] = int(float(qs[i]))
                            qs2[i] = int(float(qs2[i]))
                            seriesqs = list(zip(index,qs,qs2))
                            print(seriesqs)
                else:
                        seriesqs = []
                        quantiles = [-1]

                #print("======\n\n",quantiles)
                #print("\n\n\n\n\n\n---\n\n\n\n")
                if type.startswith("inc"):
                    type_serie = "column"
                    type_error = "errorbar"
                    #or histogram
                else:
                    type_serie = "spline"
                    type_error = "arearange"

                context = {"type_error":type_error,"type_serie":type_serie, "real_color": real_color,"real_name":real_name,"real_series":real_series,"namesq":namesq, "colorq":colorq,"seriesqs":seriesqs, "quantiles": quantiles, "names1": names1, "names2": names2, "name": name,"select_date": date, "errors":err,"values":values,"series":series, "color": color}
                return JsonResponse(context)
        else:
                    err = "No date"

                    models=[]
                    states=[]
                    active = []
                    name = ""
                    return JsonResponse({"errors": err, "models": models, "states":states, "radio_activate": active, "radio_filter":all_targs, "name":name})


    else:
            err = "No forecast date found for selected location and forecast team"

            models=[]
            states=[]
            active = []
            name = ""
            return JsonResponse({"errors": err, "models": models, "states":states, "radio_activate": active, "radio_filter":all_targs, "name":name})

def exportFile(request, state, team,type,date):

    
    data = gets.getFS(type=type, model=team, state=state, timezero=date)
    data = gets.reshape_for_download(data)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=export.csv'
    data.to_csv(path_or_buf=response)  # with other applicable parameters
    return response
    #resp = HttpResponse(content_type='text/csv')
    #resp['Content-Disposition'] = 'attachment; filename=myFile.csv'

   # data.to_csv(path_or_buf=resp, index=False)
    #res = json.loads(pd.DataFrame(data))
    #return JsonResponse({"data": res}, safe = False)

def download(request):
    
        data = pd.read_csv("core/templates/download.csv")
        data.to_csv("core/templates/download.csv")
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename=download.csv'

        data.to_csv(path_or_buf=resp, sep=',', index=False)
        return resp
    
def loadExcel(request, state):
    global lock_job
    lock_job = True
    print("SEt lock_job at T:", lock_job)
    print("ok")
    path="core/templates/download.xlsx"
    print(state)
    get_download(state=state,path= path)
    print('Done!')
    if lock_job==False:
        return JsonResponse({"results": "error"})
    return JsonResponse({"results": "done"})


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
    global lock_job
    if timezero == "all" and model == "all" and type == "all" and type == "all":
        for curr_mod in models:
            if lock_job:
                print(f'writing {curr_mod}...')
                print("LOCK:", lock_job)
                data = pd.DataFrame()
                for curr_date in gets.timezeros:
                    curr_date_s = str(curr_date)
                    if gets.Fexists(model=curr_mod, location=state, timezero=curr_date_s, target='all', quantile='all'):
                        data_new = gets.getFS(timezero=curr_date_s, type='all', model=curr_mod, state=state)
                        data_new = reshape_for_download(data_new)
                        data = data.append(data_new)
                if(len(data) != 0):
                    data.to_excel(excel_writer=writer, sheet_name=curr_mod, index=False) 
                
                # Retrieve only first models...:
                #i = i+1
                #if i >= 3:
                #    break
            else:
                break
            
    
    else:
        #data = getFS(timezero=timezero, type=type, model=model, state=state)
        #data = reshape_for_download(data)
        #data.to_excel(excel_writer=path, sheet_name=model, index=False)
        return None
    
    writer.save()
    print('Done!')



def exportExcell(request):     
       path="core/templates/download.xlsx"
       if os.path.exists(path):
            with open(path, "rb") as excel:
                data = excel.read()

            response = HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=download.xlsx'
            return response

def getforecastdata(request, state, team,type,date):


    print("Parameter from Get request")
    print(state)
    print(team)
    print(type)
    print(date)
    name= state +"-"+ team +"-"+  type +"-"+  date
    global lock_job

    lock_job = False
    print("SEt lock_job:", lock_job)
    print("OK")
    data = gets.getFS(type=type, model=team, state=state, timezero=date)

    exp = gets.reshape_for_download(data)
    data = gets.reshape_for_download(data)
    exp.to_csv("core/templates/download.csv")
    resp1 = HttpResponse(content_type='text/csv')
    resp1['Content-Disposition'] = 'attachment; filename=myFile.csv'
    exp.to_csv(path_or_buf=resp1, sep=',', index=False) 

    if(data is None):
                err = "No data avaiable"
                print(err)
                return JsonResponse({"errors": err})

    err = "no"
    columns = list(data.columns)
    #print(columns)
    js = data.to_json(orient='records')

    data = json.loads(js)
    #print(data)
    context = {"columns": columns,"data":data,"name": name,"select_date": date, "errors":err}
    
   
    return JsonResponse(context, safe=False)

#@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'index'



    context = { "states": states, "models":models, "quantiles":quantiles,"dates":dates}

    return render(request, 'index.html',context)

#@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        context = {}
        context['segment'] = 'data'



        context = { "states": states, "models":models, "quantiles":quantiles,"dates":dates}

        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))
