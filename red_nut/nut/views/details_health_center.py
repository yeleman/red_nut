#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou
# maintainer: fadiga

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from nut.models import (HealthCenter, ProgramIO, NutritionalData, Patient, 
                                                        ConsumptionReport)
from nut.tools.utils import (diagnose_patient, number_days, diff_weight, 
                            week_range, percentage_calculation)


@login_required
def details_health_center(request, *args, **kwargs):
    """ Details of a health center """

    context = {"category": "details_health_center"}

    num = kwargs["id"]
    health_center = HealthCenter.objects.get(id=num)

    def avg_(list_):
        ''' calcule la moyenne de jours'''
        if list_ != []:
            return sum(list_) / len(list_)
        else:
            return None

    # Les patients de ce centre
    patients = Patient.objects.filter(health_center=health_center)
    datanuts = NutritionalData.objects.filter(patient__health_center=health_center)
    programs_io = ProgramIO.objects \
                         .filter(patient__health_center=health_center)
    consumption_reports = ConsumptionReport.objects \
                                           .filter(health_center=health_center)

    input_programs = programs_io.filter(event=ProgramIO.SUPPORT)
    output_programs = programs_io.filter(event=ProgramIO.OUT)

    # Taux guerison
    nbr_healing = output_programs.filter(reason=ProgramIO.HEALING).count()
    healing_rates = percentage_calculation(nbr_healing, patients.count())
    # Taux abandon
    nbr_abandonment = output_programs \
                            .filter(reason=ProgramIO.ADBANDONMENT).count()
    abandonment_rates = percentage_calculation(nbr_abandonment, \
                                                        patients.count())
    # Taux déces
    nbr_deaths = output_programs.filter(reason=ProgramIO.DEATH).count()
    deaths_rates = percentage_calculation(nbr_deaths, patients.count())
    # Taux non repondant
    nbr_non_response = output_programs\
                            .filter(reason=ProgramIO.NON_RESPONDENT).count()
    non_response_rates = percentage_calculation(nbr_non_response, \
                                                        patients.count())

    dict_ = {}

    dict_["health_center"] = health_center.name
    dict_["code"] = health_center.code
    dict_["abandon"] = nbr_abandonment
    dict_["taux_abandon"] = abandonment_rates
    dict_["guerison"] = nbr_healing
    dict_["taux_guerison"] = healing_rates
    dict_["deces"] = nbr_deaths
    dict_["taux_deces"] = deaths_rates
    dict_["non_repondant"] = nbr_non_response
    dict_["taux_non_repondant"] = non_response_rates

    # graphic
    try:
        l_date = week_range(programs_io.order_by("date")[0].date)
    except:
        l_date = []
    total_ = []
    graph_date = []
    diagnose_mam = []
    diagnose_sam = []
    diagnose_ni = []
    if l_date:
        for da in l_date:
            program_i_o = programs_io.filter(date__lte=da)
            input_in_prog = program_i_o.filter(event=ProgramIO.SUPPORT)
            out_in_prog = program_i_o.filter(event=ProgramIO.OUT)
            input_out_in_prog = [p for p in  input_in_prog if p.patient.id \
                                 not in [i.patient.id for i in out_in_prog]]
            data = datanuts.filter(date__lte=da).order_by('date')
            total_.append(input_out_in_prog.__len__())
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

    list_num_days = [number_days(Patient.objects.get(id=out.patient_id) \
                                                .create_date, out.date) \
                                                for out in output_programs]


    try:
        dict_["avg_days"] = "%.0f" % avg_(list_num_days)
    except:
        dict_["avg_days"] = 0
    
    dict_["avg_diff_weight"] = "%.2f" % Patient.avg_weight_delta(patients)

    try:
        dict_["MAM_count"] = diagnose_mam[-1]
    except:
        dict_["MAM_count"] = 0
    try:
        dict_["SAM_count"] = diagnose_sam[-1]
    except:
        dict_["SAM_count"] = 0
    try:
        dict_["SAM_"] = diagnose_ni[-1]
    except:
        dict_["SAM_"] = 0
    try:
        dict_["actif"] = total_[-1]
    except:
        dict_["actif"] = 0
    try:
        dict_["total"] = patients.__len__()
    except:
        dict_["total"] = 0

    context.update({'dict_': dict_, \
                    'consumption_reports': consumption_reports})

    return render(request, 'details_health_center.html', context)
