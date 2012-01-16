#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django import forms
from django.shortcuts import render

from nut.models import Seat, InputOutputProgram, DataNut, Patient, Stock
from nut.tools.utils import diagnose_patient, number_days, diff_weight, \
                                                            date_graphic


def details_health_center(request, *args, **kwargs):
    """ Details of a health center """

    def taux(v1, v2):
        ''' calcule le taux '''
        return (v1 * 100) / v2

    def count_reason(reason):
        ''' compte le nobre de fois d'une raison '''
        inp_out = InputOutputProgram.objects.filter(patient__seat=seat)
        return inp_out.filter(reason=reason).count()

    def avg_(list_):
        ''' calcule la moyenne de jours'''
        if list_ != []:
            return sum(list_) / len(list_)
        else:
            return None

    context = {}
    dict_ = {}
    list_mam_sam = []
    list_num_days = []
    list_weight = []
    num = kwargs["id"]
    category = 'details_health_center'
    seat = Seat.objects.get(id=num)
    patients = Patient.objects.filter(seat=seat)
    datanuts = DataNut.objects.filter(patient__seat=seat)
    stocks = Stock.objects.filter(seat=seat)

    output_programs = InputOutputProgram.objects.filter(patient__seat=seat, \
                                                        event='s')
    input_programs = InputOutputProgram.objects.filter(patient__seat=seat, \
                                                        event='e')

    # graphic
    try:
        l_date = date_graphic(InputOutputProgram.objects \
                                            .filter(patient__seat=seat) \
                                            .order_by("date")[0].date)
    except:
        l_date = []
    total_ = []
    graph_date = []
    if l_date:
        for da in l_date:
            input_in_prog = InputOutputProgram.objects \
                                    .filter(patient__seat=seat, event="e", \
                                     date__lte=da)
            out_in_prog = InputOutputProgram.objects \
                                    .filter(patient__seat=seat, event="s", \
                                     date__lte=da)

            total_.append(input_in_prog.__len__() - out_in_prog.__len__())
            graph_date.append(da.strftime('%d/%m'))

        graph_data = [{'name': "Total", 'data': total_}]
        context.update({"graph_date": graph_date, "graph_data": graph_data})

    for out in output_programs:
        begin = Patient.objects.get(id=out.patient_id).create_date
        list_num_days.append(number_days(begin, out.date))

    for patient in patients:
        datanut_patient = datanuts.filter(patient__id=patient.id) \
                                  .order_by('date')

        if datanut_patient:
            weight = diff_weight(datanut_patient[0].weight,
                            datanut_patient[len(datanut_patient) - 1].weight)
            list_weight.append(weight)
            list_mam_sam.append(diagnose_patient(datanut_patient[0].muac, \
                                datanut_patient[0].oedema))

    try:
        dict_["avg_days"] = "%.0f" % avg_(list_num_days)
    except:
        dict_["avg_days"] = 0
    try:
        dict_["avg_diff_weight"] = "%.2f" % avg_(list_weight)
    except:
        dict_["avg_diff_weight"] = 0
    dict_["MAM_count"] = list_mam_sam.count('MAM')
    dict_["SAM_count"] = list_mam_sam.count('SAM')
    dict_["SAM_"] = list_mam_sam.count('SAM+')
    dict_["actif"] = patients.count()
    dict_["seat"] = seat.name
    dict_["code"] = seat.code
    dict_["abandon"] = count_reason('a')
    dict_["guerison"] = count_reason('h')
    dict_["deces"] = count_reason('d')
    dict_["non_repondant"] = count_reason('n')

    try:
        dict_["taux_abandon"] = taux(dict_["abandon"], dict_["actif"])
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
        dict_["taux_non_repondant"] = taux(dict_["non_repondant"], \
                                           dict_["actif"])
    except ZeroDivisionError:
        dict_["taux_non_repondant"] = 0

    context.update({"category": category, 'dict_': dict_, 'stocks': stocks})

    return render(request, 'details_health_center.html', context)
