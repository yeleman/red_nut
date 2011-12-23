#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render

from nut.tools.utils import diagnose_patient, number_days
from nut.models import Seat, InputOutputProgram, DataNut,Patient

def details_health_center(request, *args, **kwargs):
    """ Details of a health center """

    def taux(v1, v2):
        ''' calcule le taux '''
        return (v1  * 100) / v2

    def count_reason(reason):
        ''' compte le nobre de fois d'une raison '''
        inp_out = InputOutputProgram.objects.filter(patient__seat=seat)
        return inp_out.filter(reason=reason).count()

    def avg_days(list_):
        ''' calcule la moyenne de jours'''
        sum_ = 0
        if list_ != []:
            for li in list_:
                sum_ = sum_ + li
            return sum_ / len(list_)
        else:
            return None

    context = {}
    dict_ = {}
    list_mam_sam = []
    num = kwargs["id"]
    seat = Seat.objects.get(id=num)
    datanuts = DataNut.objects.filter(patient__seat=seat)

    output_programs = InputOutputProgram.objects.filter(patient__seat=seat, \
                                                        event='s')

    list_num_days = []
    for out in output_programs:
        begin = Patient.objects.get(id=out.patient_id).create_date
        list_num_days.append(number_days(begin, out.date))

    dict_["avg_days"] = avg_days(list_num_days)

    for datanut in datanuts:
        list_mam_sam.append(diagnose_patient(datanut.muac, datanut.oedema))

    dict_["MAM_count"] = list_mam_sam.count('MAM')
    dict_["SAM_count"] = list_mam_sam.count('SAM')
    dict_["SAM_"] = list_mam_sam.count('SAM+')
    dict_["actif"] = Patient.objects.filter(seat=seat).count()
    dict_["seat"] = seat.name
    dict_["abandon"] = count_reason('a')
    dict_["guerison"] = count_reason('h')
    dict_["deces"] = count_reason('d')
    dict_["non_repondant"] = count_reason('n')

    try:
        dict_["taux_abandon"] = taux(dict_["abandon"] , dict_["actif"])
    except ZeroDivisionError:
        dict_["taux_abandon"] = 0

    try:
        dict_["taux_guerison"] = taux(dict_["guerison"], dict_["actif"])
    except ZeroDivisionError:
        dict_["taux_guerison"] = 0

    try:
        dict_["taux_deces"] = taux(dict_["deces"], dict_["actif"])
    except ZeroDivisionError:
        dict_["taux_deces"] = 0

    try:
        dict_["taux_non_repondant"] = taux(dict_["non_repondant"], dict_["actif"])
    except ZeroDivisionError:
        dict_["taux_non_repondant"] = 0

    category = 'details_health_center'

    context.update({"category": category, 'dict_': dict_})

    return render(request, 'details_health_center.html', context)


