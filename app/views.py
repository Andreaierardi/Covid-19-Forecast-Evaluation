# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
import pandas
import numpy as np
import json
import re
from django.http import JsonResponse

import pycode.acquisition as acquisition
import datetime
import time

values = list()
labels = list()
states = acquisition.Fstates
models = acquisition.Fmodels
dates = acquisition.Fdates

FC = acquisition.FC
FD = acquisition.FD
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

def convert_dateTotime(lis):
    first_date = datetime.datetime(1970, 1, 1)
    return [ int( (datetime.datetime.strptime(d, "%Y-%m-%d") - first_date).total_seconds())*1000 for d in lis ]


def getforebench(request, state, team,type,date):

    print("Parameter from Get request")
    print(state)
    print(team)
    print(type)
    print(date)

    models = acquisition.Fmodels

    tmpC = filter_FC = FC[FC.location_name == state]
    filter_FC = filter_FC[filter_FC.model == team]

    tmpD = filter_FD = FD[FD.location_name == state]
    filter_FD = filter_FD[filter_FD.model == team]


    radio_filter, radio_activate = radio_filtering(FC, FD)

    models = update_models(tmpC, tmpD, type)

    name= state +"-"+ team +"-"+  namedict[type] +"-"+  date



    if  request.method == "GET":

        if(type!=None):
            if(state!="-1" and team!="-1"):
                if(date!="-1"):
                        data = acquisition.getRS(dict_case[type],state)
                        data2 = acquisition.getFS(type, team, state, date)
                        if(data2 is None):
                            err = "No models found for the selected state"
                            return JsonResponse({"errors": err, "models": models})
                        if(data is None):
                            err = "NotFound"
                            return JsonResponse({"errors": err, "models": models})

                        color= '#ba2116'
                        color2= '#2f7ed8'

                        names1 = team
                        names2= state
                        index = data2.index.strftime("%Y-%m-%d").tolist()
                        err = "no"
                        values = data2.values[:,0].tolist()
                        quantiles = data2.values[:,1:]
                        check_quantiles =np.isnan(np.sum(quantiles))
                        if(check_quantiles):
                            quantiles = [-1]

                        else:
                            quantiles = quantiles.tolist()

                        values2 =  data.values.tolist()
                        index2 = data.index.strftime("%Y-%m-%d").tolist()

                        index = convert_dateTotime(index)
                        index2 = convert_dateTotime(index2)
                        series = list(zip(index,values))
                        series2 = list(zip(index2,values2))

                        context = { "radio_activate":radio_activate,"radio_filter": radio_filter, "names1": names1, "names2":names2,"name": name,"errors":err,"series":series, "series2":series2, "color2":color2,"quantiles":quantiles,  "color": color,"models":models, "states": states, "dates":dates}
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
