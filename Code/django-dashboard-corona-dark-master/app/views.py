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

#@login_required(login_url="/login/")
def index(request):

    context = {}
    context['segment'] = 'index'

    #raw_data = open('app//shampoo.csv', 'rb').read()
    #rows  = re.split('\n', raw_data)
    #for idx, row in enumerate(rows):
        #cells = row.split(',')


    data = pandas.read_csv('app//shampoo.csv')
    values = list(data["Sales"])
    labels = list(data["Month"])

    #data_json = json.dumps(data)
    context = {"values" : values, "index" : labels}

    return render(request, 'index.html',context)

    #return HttpResponse(html_template.render(context, request), {"data": js_data})


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