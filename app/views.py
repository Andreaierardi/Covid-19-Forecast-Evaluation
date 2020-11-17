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
import json
import re
from django.http import JsonResponse

import pycode.acquisition as acquisition

data = pandas.read_csv('app//shampoo.csv')
data2 = pandas.read_csv('app//shampoo2.csv')

temperature = pandas.read_csv('app//daily-min-temperatures.csv')
values = list()
labels = list()
states = acquisition.Fstates

models = acquisition.Fmodels

def getforebench(request, forecast, benchmark,type):
    print("OKKKKK")
    print(forecast)
    print(benchmark)

    if  request.method == "GET":

        if(forecast!="-1"):
            if(benchmark!="-1"):
                data = acquisition. getFS(type, benchmark, forecast, acquisition.FD.forecast_date[1])
                color= '#2f7ed8'

                context = {"values" : data.values.tolist(), "index" : data.index.tolist(), "color": color,"models":models.tolist(), "states": states.tolist()}

            else:
                data = acquisition.getRS(type,forecast)

                color= '#2f7ed8'

                context = {"values" : data.values.tolist(), "index" : data.index.tolist(), "color": color,"models":models.tolist(), "states": states.tolist()}

            return JsonResponse(context)


#@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'index'



    context = { "states": states, "models":models.tolist()}

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
