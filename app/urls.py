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

    path('get/ajax/forecast_plot/<str:state>/<str:team>/<str:type>/<str:date>/<str:quantile>', views.getforecastplot, name='getforecastplot'),
    path('get/ajax/forecast_data/<str:state>/<str:team>/<str:type>/<str:date>/', views.getforecastdata, name='getforecastdata'),
    path('app/export/', views.exportFile, name='exportFile'),
    path('app/exportexcel/', views.exportExcell, name='exportExcell'),
    path('app/loadexcel/', views.loadExcel, name='loadExcel'),
    path('get/ajax/loadexcel/<str:state>/', views.loadExcel, name='loadExcel'),

    path('download/', views.download, name='download'),

    path('get/ajax/update_suggestions/<str:state>/<str:team>', views.get_suggestions, name='get_suggestions'),
    path('get/ajax/export/<str:state>/<str:team>/<str:type>/<str:date>/', views.exportFile, name='exportFile')



]
