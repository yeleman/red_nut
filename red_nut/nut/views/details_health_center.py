#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou
# maintainer: fadiga

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from nut.models import (HealthCenter, ProgramIO, NutritionalData, Patient,
                                                        ConsumptionReport)
from nut.tools.utils import (diagnose_patient, number_days, diff_weight,
                            week_range, percentage_calculation, extract)


@login_required
def details_health_center(request, *args, **kwargs):
    """ Details of a health center """

    context = {"category": "health_center", "user":request.user}

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

    # Taux guerison
    nbr_healing = ProgramIO.healing.filter(patient__health_center=health_center).count()
    healing_rates = percentage_calculation(nbr_healing, patients.count())
    # Taux abandon
    nbr_abandonment = ProgramIO.abandon.filter(patient__health_center=health_center).count()
    abandonment_rates = percentage_calculation(nbr_abandonment, \
                                                        patients.count())
    # Taux déces
    nbr_deaths = ProgramIO.death.filter(patient__health_center=health_center).count()
    deaths_rates = percentage_calculation(nbr_deaths, patients.count())
    # Taux non repondant
    nbr_non_response = ProgramIO.nonresp.filter(patient__health_center=health_center).count()
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
        week_dates = week_range(programs_io.order_by("date")[0].date)
    except IndexError:
        week_dates = []

    total_patient = []
    graph_date = []
    diagnose_mam = []
    diagnose_sam = []
    diagnose_ni = []

    for dat in week_dates:

        active_patients = []
        for p in patients:
            try:
                if not p.programios.filter(date__lte=dat).latest().is_output:
                    active_patients.append(p)
            except ProgramIO.DoesNotExist:
                pass

        total_patient.append(len(active_patients))
        graph_date.append(dat.strftime('%d/%m'))

        l_diagnose = []
        for patient in active_patients:
            try:
                l_diagnose.append(patient.nutritional_data.latest().diagnosis)
            except NutritionalData.DoesNotExist:
                pass

        diagnose_mam.append(l_diagnose.count('MAM'))
        diagnose_sam.append(l_diagnose.count('SAM'))

        graph_data = [{'name': "Total", 'data': total_patient},
                      {'name': "MAM", 'data': diagnose_mam},
                      {'name': "MAS", 'data': diagnose_sam}]

        context.update({"graph_date": graph_date, "graph_data": graph_data})

    # Diagnose
    dict_["MAM_count"] = extract(diagnose_mam, -1, default=0)
    dict_["SAM_count"] = extract(diagnose_sam, -1, default=0)

    # Nbre d'enfants dans le programme
    dict_["actif"] = extract(total_patient, -1, default=0)
    # Nbre d'enfants enregistres
    dict_["total"] = patients.count() or 0

    try:
        dict_["avg_days"] = "%.0f" % ProgramIO.out\
                                .filter(patient__health_center=health_center)\
                                .avg_days()
    except:
        dict_["avg_days"] = 0

    dict_["avg_diff_weight"] = "%.2f" % Patient.avg_weight_delta(patients)

    context.update({'dict_': dict_, \
                    'consumption_reports': consumption_reports})

    return render(request, 'details_health_center.html', context)
