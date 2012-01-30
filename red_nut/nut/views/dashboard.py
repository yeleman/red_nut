#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings

from nut.models import ProgramIO, Patient, NutritionalData
from nosmsd.models import Inbox, SentItems
from nut.tools.utils import (diagnose_patient, diff_weight, 
                            week_range, verification_delay, 
                            percentage_calculation)


def dashboard(request):

    context = {"category": 'dashboard'}

    # le nombre total d'enfant
    nbr_total_patient = Patient.objects.all().count()

    # Taux guerison
    nbr_healing = ProgramIO.healing.count()
    healing_rates = percentage_calculation(nbr_healing, nbr_total_patient)

    # Taux abandon
    nbr_abandonment = ProgramIO.abandon.count()
    abandonment_rates = percentage_calculation(nbr_abandonment, 
                                               nbr_total_patient)

    # Taux déces
    nbr_deaths = ProgramIO.death.count()
    deaths_rates = percentage_calculation(nbr_deaths, nbr_total_patient)

    # Taux non repondant
    nbr_non_response = ProgramIO.nonresp.count()

    non_response_rates = percentage_calculation(nbr_non_response, 
                                                nbr_total_patient)

    context.update({"nbr_total_patient": nbr_total_patient, 
                    "nbr_healing": nbr_healing, 
                    "healing_rates": healing_rates, 
                    "nbr_abandonment": nbr_abandonment, 
                    "abandonment_rates": abandonment_rates, 
                    "nbr_deaths": nbr_deaths, 
                    "deaths_rates": deaths_rates, 
                    "nbr_non_response": nbr_non_response,
                    "non_response_rates": non_response_rates})

    # Durées de tous les programmes puis moyenne
    context.update({"avg_days": ProgramIO.out.avg_days()})

    # Gain de poids moyen
    context.update({"avg_weight": "%.2f" % Patient.avg_weight_delta()})

    # graphic
    total_patient = []
    graph_date = []
    diagnose_mam = []
    diagnose_sam = []
    diagnose_ni = []

    week_dates = week_range(ProgramIO.objects.all()[0].date)
    for dat in week_dates:

        # for patient in Patient.objects.all():
        #     if patient.programios.filter(date__lte=dat).latest().event != ProgramIO.OUT:

        input_in_prog = ProgramIO.objects.filter(event=ProgramIO.SUPPORT,
                                                            date__lte=dat)

        out_in_prog = ProgramIO.objects.filter(event=ProgramIO.OUT,
                                                         date__lte=dat)

        input_out_in_prog = [p for p in  input_in_prog if p.patient \
                             not in [i.patient for i in out_in_prog]]

        data = NutritionalData.objects.order_by('date').filter(date__lte=dat)

        total_patient.append(input_out_in_prog.__len__())

        graph_date.append(dat.strftime('%d/%m'))
        
        l_diagnose = [diagnose_patient(d.muac, d.oedema) for d in data \
                                    if d.patient.id in [(i.patient.id) \
                                            for i in input_out_in_prog]]
        if l_diagnose:
            diagnose_mam.append(l_diagnose.count('MAM'))
            diagnose_sam.append(l_diagnose.count('SAM'))
            diagnose_ni.append(l_diagnose.count('SAM+'))

        # Graphic
        graph_data = [{'name': "Total", 'data': total_patient}, \
                      {'name': "MAM", 'data': diagnose_mam}, \
                      {'name': "MAS", 'data': diagnose_sam}, \
                      {'name': "MAS+", 'data': diagnose_ni}]

        context.update({"graph_date": graph_date, "graph_data": graph_data})
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

    context.update({"children_in_program": children_in_program, \
                    "sent": sent, "received": received, \
                    "MAM_count": MAM_count, "SAM_count": SAM_count, \
                    "patients_late": patients_late, "NI_count": NI_count})

    return render(request, 'dashboard.html', context)
