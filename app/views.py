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


import pandas 
import numpy as np
import json
import re
import datetime
import time
import os

#import pycode.acquisition as acquisition
import getters as gets





#project_name = 'COVID-19 Forecasts'
#model_abbr = 'BPagano-RtDriven'
#timezero_date = '2020-11-22'

#project = [project for project in conn.projects if project.name == project_name][0]
#json_io_dict = util.download_forecast(conn, project_name,model_abbr , timezero_date)
#df2 = util.dataframe_from_json_io_dict(json_io_dict)

#print(df2)

#============= VARIABLE INITIALISATION  ====================

values = list()
labels = list()
states = list(gets.locations)[1:len(gets.locations)]
models = gets.models
dates = []
for d in gets.timezeros:
    dates.append(d.strftime("%Y-%m-%d"))

targs = gets.targets

all_targs = []

for i in gets.targets:
     x = i.split(" ")
     string = x[-2]+" "+x[-1]
     if not string in all_targs:
             all_targs.append(string)

locations_inv = {v: k for k, v in gets.locations.items()}


#FC = acquisition.FC
#FD = acquisition.FD



# Useful dictionaries for the abbrevations
namedict = {
  "cc": "cum case",
  "cd": "cum death",
  "ic": "inc case",
  "id": "inc death"
}

namedict_inv = {
  "cum case":"cc",
  "cum death": "cd",
  "inc case": "ic",
  "inc death": "id"
}
dict_case = {
  "cc": "C",
  "cd": "D",
  "ic": "C",
  "id": "D"
}


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
def radio_filtering(filter_FC, filter_FD):
    radio_filter = []
    for i in ["cum death","inc death"]:
        if not filter_FD[filter_FD.target.apply(str.endswith, args=(i, 0)) == True].model.unique().tolist():
            radio_filter.append(namedict_inv[i])

    for i in ["cum case","inc case"]:
        if not filter_FC[filter_FC.target.apply(str.endswith, args=(i, 0)) == True].model.unique().tolist():
            radio_filter.append(namedict_inv[i])

    radio_activate = []
    for i in ["cum case","inc case","cum death","inc death"]:
        if namedict_inv[i] not in radio_filter:
            radio_activate.append(namedict_inv[i])
    return (radio_filter, radio_activate)



"""
Gets the list of the model avaiable for the selected state and type of data to pass to the JS client

    Parameters
    ----------
    tmpC : pandas.DataFrame
        The dataframe for the cases filtered by State
    tmpD : pansad.dataframe
        The dataframe for the deaths filtered by State
    type : str
        The string of the type for the selected dataset

    Returns
    -------
    list
        a list of string containing the models avaiable for the type and state selected:

"""

def update_models(tmpC, tmpD, type):
    if(type=="cc" ):
        filter_state= tmpC[tmpC.target.apply(str.endswith, args=(namedict[type], 0)) == True ]
        model = filter_state.model.unique().tolist()
    if (type=="ic"):
        filter_state= tmpC[tmpC.target.apply(str.endswith, args=(namedict[type], 0)) == True ]
        model = filter_state.model.unique().tolist()
    if(type=="cd"):
        filter_state= tmpD[tmpD.target.apply(str.endswith, args=(namedict[type], 0)) == True ]
        model = filter_state.model.unique().tolist()
    if(type=="id"):
        filter_state= tmpD[tmpD.target.apply(str.endswith, args=(namedict[type], 0)) == True ]
        model = filter_state.model.unique().tolist()
    return model



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
def getforecastplot(request, state, team,type,date):
    print("Parameter from Get request")
    print(state)
    print(team)
    print(type)
    print(date)

#    states = gets.locations
#    dates = acquisition.Fdates
#    targs = gets.targets

#    models = gets.models

#    tmpC = filter_FC = FC[FC.location_name == state]
#    filter_FC = filter_FC[filter_FC.model == team]

#    tmpD = filter_FD = FD[FD.location_name == state]
#    filter_FD = filter_FD[filter_FD.model == team]


#    radio_filter, radio_activate = radio_filtering(FC, FD)

#    models = update_models(tmpC, tmpD, type)

    name= state +"-"+ team +"-"+  type +"-"+  date



    if  request.method == "GET":
        print(name)
        if(type!=None):
            if(state!="-1" and team!="-1"):
                if(date!="-1"):
                       
                        new_loc = []
                        new_model=[]
                        new_targ = []
                        suggestions = gets.getFS(timezero=date, state = state)
                        suggestions2 = gets.getFS(timezero=date, state = state,model=team)

                        targ_list = list(suggestions2.target.unique())

                        for i in targ_list:
                            x = i.split(" ")
                            string = x[-2]+" "+x[-1]
                            if not string in new_targ:
                                    new_targ.append(string)

                        new_model = list(suggestions.model.unique())
                        new_targ = list()
                        print(new_loc)
                        data = gets.getFS(type=type, model=team, state=state, timezero=date)
                        print(data)
                        models = new_model

                        radio_filtering = []
                        radio_activate = new_targ

                        for t in all_targs:
                            if not t in new_targ:
                                radio_filtering.append(t)
                        if(data is None):
                            err = "NotFound"
                            return JsonResponse({"errors": err, "models": models})

                        color= '#ba2116'

                        names1 = team
                        names2= state
                        index = data.index.strftime("%Y-%m-%d").tolist()
                        err = "no"

                        values = pandas.to_numeric(data.point,downcast='integer').tolist()
                        for i in range(len(values)):
                            values[i] = int(values[i])
                        print(values)
                        index = convert_dateTotime(index)
                        series = list(zip(index,values))
                       
                        context = {  "radio_filter": radio_filtering, "radio_activate":radio_activate, "names1": names1, "names2": names2, "name": name,"errors":err,"values":values,"series":series, "color": color,"models":models, "states": states, "dates":dates}
                        return JsonResponse(context)



                else:
                    err = "Select a Forecast date"
                    return JsonResponse({"errors": err})
            else:
                err = "Select a Location"
                return JsonResponse({"errors": err})




#@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'index'



    context = { "states": states, "models":models, "dates":dates}

    return render(request, 'index.html',context)



#@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))
