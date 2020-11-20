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



values = list()
labels = list()
states = acquisition.Fstates
models = acquisition.Fmodels
dates = acquisition.Fdates

def getforebench(request, forecast, benchmark,type,date):

    print("Parameter from Get request")
    print(forecast)
    print(benchmark)
    print(type)
    print(date)
    if(benchmark=="-1"):
            benchmark_name=""
    else:
        benchmark_name = benchmark+"-"
    if(type=="D"):
        type_name = "Deaths"
    if(type=="C"):
        type_name = "Cases"
    name= forecast +"-"+ benchmark_name +  type_name+"-"+  date


    if  request.method == "GET":
        if(type!=None):
            if(forecast!="-1" and benchmark!="-1"):
                if(date!="-1"):
                        data = acquisition.getRS(type,forecast)
                        data2 = acquisition.getFS(type, benchmark, forecast, date)
                        if(data2 is None):
                            err = "No models found for the selected state"
                            return JsonResponse({"errors": err})
                        if(data is None):
                            err = "NotFound"
                            return JsonResponse({"errors": err})

                        color= '#ba2116'
                        color2= '#2f7ed8'

                        names1 = benchmark
                        names2= forecast
                        lab = data2.index.strftime("%Y-%m-%d").tolist()
                        err = "no"
                        values = data2.values[:,0]
                        quantiles = data2.values[:,1:]

                        values2 =  data.values.tolist()
                        index2 = data.index.strftime("%Y-%m-%d").tolist()
                        print(index2)
                        context = {"names1": names1, "names2":names2,"name": name,"errors":err,"values2": values2, "index2":index2, "color2":color2,"quantiles":quantiles.tolist(), "values" : values.tolist(), "index" : lab, "color": color,"models":models, "states": states, "dates":dates}
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
