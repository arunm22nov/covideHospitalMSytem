'''
Created on 24-Feb-2021

@author: arun
'''
from django.urls import path
from . import views

urlpatterns=[
  
    path('home/',views.home),
    path('setBedCount/',views.setBedCount, name='setBedCount'),
    path('getAllPatientList/',views.getAllPatientList,name='getAllPatientList'),
    path('getBedStatus/',views.getBedStatus,name='getBedStatus')
    ]