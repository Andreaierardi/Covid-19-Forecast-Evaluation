# -*- encoding: utf-8 -*-
"""
MIT License
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^.*\.html', views.pages, name='pages'),
    # The home page
    path('', views.index, name='home'),

    path('get/ajax/forecast_plot/<str:state>/<str:team>/<str:type>/<str:date>', views.getforecastplot, name='getforecastplot'),
    path('get/ajax/date_change/<str:state>/<str:team>/<str:type>/<str:date>', views.datechange, name='datechanges')

]
