#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render

from nut.tools.utils import diagnose_patient
from nut.models import Seat, InputOutputProgram, DataNut

def details_health_center(request, *args, **kwargs):
    num = kwargs["id"]
    seat = Seat.objects.get(id=num)
    dict_ = {}
    inp_out = InputOutputProgram.objects \
                                         .filter(patient__seat=seat)
    datanut = DataNut.objects \
                                         .filter(patient__seat=seat)
    li = []
    for d in datanut:
        li.append(diagnose_patient(d.muac, d.oedema))
    dict_["MAM_count"] = li.count('MAM')
    dict_["SAM_count"] = li.count('SAM')
    dict_["SAM_"] = li.count('SAM+')

    count_registered = inp_out.count()
    dict_["seat"] = seat.name
    dict_["abandon"] = inp_out.filter(reason='a').count()
    dict_["guerison"] = inp_out.filter(reason='h').count()
    dict_["deces"] = inp_out.filter(reason='d').count()
    dict_["non_repondant"] = inp_out.filter(reason='n').count()
    dict_["actif"] = inp_out.filter(event='e').count()
    try:
        dict_["taux_abandon"] = (dict_["abandon"]  * 100) / dict_["actif"]
        dict_["taux_guerison"] = (dict_["guerison"] * 100) / dict_["actif"]
        dict_["taux_deces"] = (dict_["deces"] * 100) / dict_["actif"]
        dict_["taux_non_repondant"] = (dict_["non_repondant"] * 100) / dict_["actif"]
    except ZeroDivisionError:
        dict_["taux_abandon"] = 0
        pass

    category = 'details_health_center'
    context = {}
    context.update({"category": category, 'dict_': dict_})

    return render(request, 'details_health_center.html', context)
