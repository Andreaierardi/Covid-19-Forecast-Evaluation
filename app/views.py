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
values = list()
labels = list()


def print_btn2(request):
    print(request.method == "GET")
    if  request.method == "GET":
        data = pandas.read_csv('app//shampoo.csv')

        values = list(data["Sales"])
        labels = list(data["Month"])

        print(values)
        context = {"values" : values, "index" : labels}

        return JsonResponse(context)


def print_btn(request):
    print(request.method == "GET")
    if  request.method == "GET":
        data2 = pandas.read_csv('app//shampoo2.csv')

        values2 = list(data2["Sales"])
        labels2 = list(data2["Month"])

        print(values2)
        context2 = {"values2" : values2, "index2" : labels2}

        return JsonResponse(context2)


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
