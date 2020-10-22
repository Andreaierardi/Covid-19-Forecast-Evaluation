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

data = pandas.read_csv('app//shampoo.csv')
data2 = pandas.read_csv('app//shampoo2.csv')

temperature = pandas.read_csv('app//daily-min-temperatures.csv')
values = list()
labels = list()

def getforebench(request, forecast, benchmark):
    print("OKKKKK")
    print(forecast)
    print(benchmark)
    data = pandas.read_csv('app//shampoo.csv')

    if  request.method == "GET":
        if forecast==1 and benchmark==0:

            values = list(data["Sales"])
            labels = list(data["Month"])
            color= '#2f7ed8'


        elif forecast==2 and benchmark==0:

            values = list(data2["Sales"])
            labels = list(data2["Month"])
            color= '#FF0000'

        elif forecast==0 and benchmark==4:
            values = list(temperature["Temp"])
            labels = list(temperature["Date"])
            color= '#2f7ed8'

        elif forecast==0 and benchmark==5:
            values = list(temperature["Temp"])
            labels = list(temperature["Date"])
            color= '#FF0000'
        else:
            data = pandas.read_csv('app//shampoo.csv')

            values = list(data["Sales"])
            labels = list(data["Month"])
            color= '#2f7ed8'

        print(values)
        context = {"values" : values, "index" : labels, "color": color}

        return JsonResponse(context)


#@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'index'

    values = list(data["Sales"])
    labels = list(data["Month"])

    context = {"values" : values, "index" : labels}

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
