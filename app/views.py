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
#import acquisition as acq
from getters import Fexists
from getters import getFS
from getters import corr_dict
from getters import getRS


#============= VARIABLE INITIALISATION  ====================

values = list()
labels = list()
states = list(gets.locations)
models = sorted(gets.models)
dates = []

quant = gets.quantiles
quantiles = []
for i in quant[len(quant)//2:len(quant)]:
            for j in quant[0:len(quant)//2+1]:
                print("===_", i,j)
                if float(i)+float(j) == 1:
                    if(float(i)> float(j)):
                        quantiles.append(str(i)+"-"+str(j))
                    else:
                        quantiles.append(str(j)+"-"+str(i))
quantiles = sorted(quantiles, reverse = True)
all_quant = quantiles
print(quantiles)
#quantiles = ["0.99-0.01",
#"0.975-0.025",
#"0.95-0.05",
#"0.9-0.1",
#"0.85-0.15",
#"0.8-0.2",
#"0.75-0.25",
#"0.7-0.3",
#"0.65-0.35",
#"0.6-0.4",
#"0.55-0.45",
#"0.5-0.5"
#]
#list(gets.quantiles)
print(quantiles)
all_dates = []
for d in gets.timezeros:
   dates.append(d.strftime("%Y-%m-%d"))
   all_dates.append(d.strftime("%Y-%m-%d"))

try:
    data = gets.getFS(timezero= dates[0])

except:
    import acquisition as acq

    limit = dates[0]
    print("LIMIT: ",limit)
    parquet_list = sorted(os.listdir("data"))
    parquet_list = parquet_list[0:len(parquet_list)-1]
    print("\nPARQUET LIST\n\n\n", parquet_list,"\n\n===========")
    last_parquet = parquet_list[len(parquet_list)-2].split(".parquet")[0]
    print("LAST PARQUET:" ,last_parquet)
    ind = dates.index(last_parquet)

    new_dates = dates[0:ind]
    print("NEW DATES:\n",new_dates)
    acq.retrieve_data(new_dates)
    data = gets.getFS(timezero= dates[0])


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
    if(Fexists(model = team, location = state)):

        models = sorted(gets.models)
        states = list(gets.locations)
        targs = []
        dates = []
        quant = []
        quantiles = []


        if(team == "all" or state == "all"):
            targs = all_targs
            quant = all_quant
            dates = all_dates
        if(team != "all" and state !="all"):
            sugg = corr_dict[(team,state)]
            for s in sugg:
                if(s is not None) and (type(s) is tuple):
                    print("FOUND:",s[0],s[1],s[2])
                    if s[0] not in dates:
                        dates.append(s[0])
                    if s[1] not in targs:
                        targs.append(s[1])
                    if s[2] not in quant and s[2] is not None:
                        quant.append(s[2])
            print(quant)
            dates = sorted(dates, reverse = True)

            for i in quant[len(quant)//2:len(quant)]:
                    for j in quant[0:len(quant)//2+1]:
                        if float(i)+float(j) == 1:
                            quantiles.append(str(i)+"-"+str(j))
            quantiles = sorted(quantiles, reverse = True)
        radio_activate = targs

        radio_filter = []
        for i in all_targs:
            if i not in radio_activate:
                radio_filter.append(i)


        err = "no"
        print("\n\n=========\n\n")
        print(radio_activate)
        print(radio_filter)
        print(dates)
        print(quantiles)
        context = { "quantiles":quantiles, "radio_filter": radio_filter, "radio_activate":radio_activate, "errors":err,"models":models, "states": states, "dates":dates}
        return JsonResponse(context)
    else:
        err = "Not Exists"
        print(err)
        return JsonResponse({"errors": err})

def getforecastplot(request, state, team,type,date,quantile):


    print("Parameter from Get request")
    print(state)
    print(team)
    print(type)
    print(date)
    print(quantile)
    if(Fexists(model = team, location = state)):

        if(Fexists(model = team, location = state, target = type, timezero = date )):
                data = getFS(type=type, model=team, state=state, timezero=date)
                if(data is None):
                    err = "NotFound"
                    print(err)
                    return JsonResponse({"errors": err})

                data_len =len(data)

                today = datetime.datetime.now()
                convert = datetime.datetime.strptime(date,"%Y-%m-%d")
                while(convert+datetime.timedelta(7*data_len)) > today:
                    data_len = data_len -1
                    print(data_len)
                real_data = getRS(timezero= date, type = type , state= state, window= data_len)

                if (real_data is None):
                        err = "Real data NotFound"
                        print(err)
                        return JsonResponse({"errors": err})
                data = data.sort_index()
                real_data = real_data.sort_index()

                color= '#ba2116'
                real_color = '#2f7ed8'
                colorq = "#ffcc66"


                name= state +"-"+ team +"-"+  type +"-"+  date
                real_name = "Real cases"
                print(name)

                print(quantile)
                quant1 , quant2 = quantile.split("-")
                print(quant1," and ", quant2)


                names1 = team
                names2= state
                namesq =  "Confidence Intervals:"+quantile
                index = data.index.strftime("%Y-%m-%d").tolist()
                err = "no"

                values = pd.to_numeric(data.point,downcast='integer').tolist()
                for i in range(len(values)):
                    values[i] = int(values[i])

                print(values)


                real_values = list(real_data.values)
                for i in range(len(real_values)):
                    real_values[i] = int(real_values[i])

                print(real_values)
                index = convert_dateTotime(index)
                series = list(zip(index,values))
                print(series)


                real_series = list(zip(index, real_values))
                quantiles = []

                if len(list(data.values[0])) > 5:
                    quant = list(data[('quantile')])
                    quant_list = []
                    for i in quant[len(quant)//2:len(quant)]:
                                for j in quant[0:len(quant)//2+1]:
                                    print("===_", i,j)
                                    if float(i)+float(j) == 1:
                                        if(float(i)> float(j)):
                                            quantiles.append(str(i)+"-"+str(j))
                                        else:
                                            quantiles.append(str(j)+"-"+str(i))
                                        quant_list.append(str(i))
                                        quant_list.append(str(j))

                    quantiles = sorted(quantiles, reverse =True)
                    print("PREE ======\n\n",quantiles)
                    print("\n\n\n\n\n\n---\n\n\n\n")
                    print("quant1:",quant1)
                    print("quant_list:",quant_list)
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

                print("======\n\n",quantiles)
                print("\n\n\n\n\n\n---\n\n\n\n")
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
            err = "No date"

            models=[]
            states=[]
            active = []
            name = ""
            return JsonResponse({"errors": err, "models": models, "states":states, "radio_activate": active, "radio_filter":all_targs, "name":name})



def getforecastdata(request, state, team,type,date):


    print("Parameter from Get request")
    print(state)
    print(team)
    print(type)
    print(date)
    name= state +"-"+ team +"-"+  type +"-"+  date

    data = getFS(type=type, model=team, state=state, timezero=date)
    
    if(data is None):
                err = "NotFound"
                print(err)
                return JsonResponse({"errors": err})

    err = "no"
    columns = list(data.columns)
    print(columns)
    js = data.to_json(orient='records')

    data = json.loads(js)
    print(data)
    context = {"columns": columns,"data":data,"name": name,"select_date": date, "errors":err}
    return JsonResponse(context, safe=False)

#@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'index'



    context = { "states": states, "models":models, "quantiles":quantiles,"dates":dates}

    return render(request, 'index.html',context)

def getFile(request):
    
    def stream():
            buffer_ = io.StringIO()
            writer = csv.writer(buffer_)
            for row in rows:
                writer.writerow(row)
                buffer_.seek(0)
                data = buffer_.read()
                buffer_.seek(0)
                buffer_.truncate()
                yield data

    response = StreamingHttpResponse(
        stream(), content_type='text/csv'
    )
    disposition = "attachment; filename=file.csv"
    response['Content-Disposition'] = disposition
    return response

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
