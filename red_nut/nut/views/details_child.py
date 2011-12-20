#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings

from nut.models import Patient, DataNut

def details_child(request, *args, **kwargs):
    num = kwargs["id"]
    category = 'details_child'
    context = {}
    try:
        patient = Patient.objects.filter(id = num)[0]
        datanut = DataNut.objects.filter(patient__id=num)[0]
        datanuts = DataNut.objects.filter(patient__id=num)
        context.update({'category': category,
                    'patient': patient,
                    'datanut': datanut,
                    'datanuts': datanuts})
    except:
        context.update({'error': 'aucun details'})


    return render(request, 'details_child.html', context)
