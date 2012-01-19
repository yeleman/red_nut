#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django import forms
from django.shortcuts import render
from django.core.urlresolvers import reverse
from nut.models import HealthCenter, ProgramIO, DataNut, Patient, \
                                                        ConsumptionReport
from nut.tools.utils import diagnose_patient, number_days, diff_weight, \
                                                            date_graphic


def details_health_center(request, *args, **kwargs):
    """ Details of a health center """

    def taux(v1, v2):
        ''' calcule le taux '''
        return (v1 * 100) / v2

    def count_reason(reason):
        ''' compte le nobre de fois d'une raison '''
        inp_out = ProgramIO.objects \
                           .filter(patient__health_center=health_center)
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
    health_center = HealthCenter.objects.get(id=num)
    patients = Patient.objects.filter(health_center=health_center)
    datanuts = DataNut.objects.filter(patient__health_center=health_center)
    consumption_reports = ConsumptionReport.objects \
                                           .filter(health_center=health_center)
    print consumption_reports

    output_programs = ProgramIO.objects \
                               .filter(patient__health_center=health_center, \
                                                    event=ProgramIO.SUPPORT)
    input_programs = ProgramIO.objects\
                              .filter(patient__health_center=health_center, \
                                                        event=ProgramIO.OUT)

    # graphic
    try:
        l_date = date_graphic(ProgramIO.objects \
                            .filter(patient__health_center=health_center) \
                            .order_by("date")[0].date)
    except:
        l_date = []
    total_ = []
    graph_date = []
    diagnose_mam = []
    diagnose_sam = []
    diagnose_ni = []
    if l_date:
        for da in l_date:
            input_in_prog = ProgramIO\
                     .objects.filter(patient__health_center=health_center,
                                             event=ProgramIO.SUPPORT,
                                             date__lte=da)
            out_in_prog = ProgramIO.objects \
                          .filter(patient__health_center=health_center,
                                  event="s", date__lte=da)
            input_out_in_prog = [p for p in  input_in_prog if p.patient.id \
                                 not in [i.patient.id for i in out_in_prog]]
            data = DataNut.objects.order_by('date').filter(date__lte=da)
            total_.append(input_in_prog.__len__() - out_in_prog.__len__())
            graph_date.append(da.strftime('%d/%m'))
            l_diagnose = [diagnose_patient(d.muac, d.oedema) for d in data \
                                        if d.patient.id in [(i.patient.id) \
                                                for i in input_out_in_prog]]
            if l_diagnose:
                diagnose_mam.append(l_diagnose.count('MAM'))
                diagnose_sam.append(l_diagnose.count('SAM'))
                diagnose_ni.append(l_diagnose.count('SAM+'))

        graph_data = [{'name': "Total", 'data': total_},
                       {'name': "MAM", 'data': diagnose_mam}, \
                  {'name': "MAS", 'data': diagnose_sam}, \
                  {'name': "MAS+", 'data': diagnose_ni}]
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
    dict_["health_center"] = health_center.name
    dict_["code"] = health_center.code
    dict_["abandon"] = count_reason('a')
    dict_["guerison"] = count_reason('h')
    dict_["deces"] = count_reason('d')
    dict_["non_repondant"] = count_reason('n')
    dict_["url"] = reverse("excel_export", args=[health_center.id])
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

    context.update({"category": category, 'dict_': dict_, \
                    'consumption_reports': consumption_reports})

    return render(request, 'details_health_center.html', context)
