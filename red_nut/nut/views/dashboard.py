#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings

from nut.models import ProgramIO, Patient, DataNut
from nosmsd.models import Inbox, SentItems
from nut.tools.utils import diagnose_patient, number_days, diff_weight, \
                                        date_graphic, verification_delay


def dashboard(request):

    context = {"category": 'dashboard'}

    # Les ptients qui ne sont plus dans le programme
    out_program = ProgramIO.objects.filter(event=ProgramIO.OUT)

    def calculation_of_rates(nb, tnb):
        try:
            return (nb * 100) / tnb
        except ZeroDivisionError:
            return 0
    # le nombre total d'enfant
    nbr_total_patient = Patient.objects.all().count()
    # Taux guerison
    nbr_healing = out_program.filter(reason=ProgramIO.HEALING).count()
    healing_rates = calculation_of_rates(nbr_healing, nbr_total_patient)
    # Taux abandon
    nbr_abandonment = out_program \
                            .filter(reason=ProgramIO.ADBANDONMENT).count()
    abandonment_rates = calculation_of_rates(nbr_abandonment, \
                                                        nbr_total_patient)
    # Taux déces
    nbr_deaths = out_program.filter(reason=ProgramIO.DEATH).count()
    deaths_rates = calculation_of_rates(nbr_deaths, nbr_total_patient)
    # Taux non repondant
    nbr_non_response = out_program\
                            .filter(reason=ProgramIO.NON_RESPONDENT).count()
    non_response_rates = calculation_of_rates(nbr_non_response, \
                                                        nbr_total_patient)
    context.update({"nbr_total_patient": nbr_total_patient, \
                    "nbr_healing": nbr_healing, \
                    "healing_rates": healing_rates, \
                    "nbr_abandonment": nbr_abandonment, \
                    "abandonment_rates": abandonment_rates, \
                    "nbr_deaths": nbr_deaths, \
                    "deaths_rates": deaths_rates, \
                    "nbr_non_response": nbr_non_response,\
                    "non_response_rates": non_response_rates})
    # Durée moyenne dans le programme
    list_num_days = [(number_days(Patient.objects \
                                         .get(id=out.patient_id) \
                                         .create_date, out.date)) \
                                          for out in out_program]
    try:
        avg_days = sum(list_num_days) / list_num_days.__len__()
    except:
        avg_days = 0
    context.update({"avg_days": avg_days})

    # Les données nutritionnelles
    nutritional_data = DataNut.objects.all()
    # Gain de poids moyen
    patients = Patient.objects.all()
    list_weight = []
    for patient in patients:
        # les patients qui ont une donnée nutritionnelle
        datanut_patient = nutritional_data.filter(patient=patient) \
                                  .order_by('date')
        if datanut_patient:
            weight = diff_weight(datanut_patient[0].weight, \
                            datanut_patient[len(datanut_patient) - 1].weight)
            list_weight.append(weight)
    try:
        avg_weight = sum(list_weight) / list_weight.__len__()
    except:
        avg_weight = 0
    context.update({"avg_weight": "%.2f" % avg_weight})
    # graphic
    try:
        list_date = date_graphic(ProgramIO.objects.order_by("date")[0].date)
    except:
        list_date = []
    total_patient = []
    graph_date = []
    diagnose_mam = []
    diagnose_sam = []
    diagnose_ni = []
    if list_date:
        for dat in list_date:
            input_in_prog = ProgramIO.objects.filter(event=ProgramIO.SUPPORT,
                                                                date__lte=dat)
            out_in_prog = ProgramIO.objects.filter(event=ProgramIO.OUT,
                                                             date__lte=dat)
            input_out_in_prog = [p for p in  input_in_prog if p.patient \
                                 not in [i.patient for i in out_in_prog]]
            data = DataNut.objects.order_by('date').filter(date__lte=dat)
            total_patient.append(input_out_in_prog.__len__())
            graph_date.append(dat.strftime('%d/%m'))
            l_diagnose = [diagnose_patient(d.muac, d.oedema) for d in data \
                                        if d.patient.id in [(i.patient.id) \
                                                for i in input_out_in_prog]]
            if l_diagnose:
                diagnose_mam.append(l_diagnose.count('MAM'))
                diagnose_sam.append(l_diagnose.count('SAM'))
                diagnose_ni.append(l_diagnose.count('SAM+'))

    # Diagnose
    try:
        MAM_count = diagnose_mam[-1]
    except:
        MAM_count = 0

    try:
        SAM_count = diagnose_sam[-1]
    except:
        SAM_count = 0

    try:
        NI_count = diagnose_ni[-1]
    except:
        NI_count = 0

    # Nbre d'enfant dans le programme
    try:
        children_in_program = total_patient[-1]
    except:
        children_in_program = 0

    # Nbre d'enfant en retard de consultation
    patients_late = [patient for patient in patients \
                     if verification_delay(patient.delay_since_last_visit()) \
                        and patient.last_data_event().event == ProgramIO \
                        .SUPPORT].__len__()
    # message
    received = Inbox.objects.count()
    sent = SentItems.objects.count()
    # Graphic
    graph_data = [{'name': "Total", 'data': total_patient}, \
                  {'name': "MAM", 'data': diagnose_mam}, \
                  {'name': "MAS", 'data': diagnose_sam}, \
                  {'name': "MAS+", 'data': diagnose_ni}]

    context.update({"children_in_program": children_in_program, \
                    "sent": sent, "received": received, \
                    "MAM_count": MAM_count, "SAM_count": SAM_count, \
                    "patients_late": patients_late, "NI_count": NI_count,
                    "graph_date": graph_date, "graph_data": graph_data})


    return render(request, 'dashboard.html', context)
