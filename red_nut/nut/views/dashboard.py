#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
#~ from django.contrib import messages
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings

from nut.models import Seat, InputOutputProgram, Patient, DataNut
from nosmsd.models import Inbox, SentItems
from nut.tools.utils import diagnose_patient, number_days, diff_weight


def dashboard(request):
    """  """
    category = 'dashboard'
    context = {}
    context.update({"category": category})

    inp_out = InputOutputProgram.objects.all()
    datanuts = DataNut.objects.all()
    # Diagnose
    li_diagnose = [(diagnose_patient(d.muac, d.oedema)) for d in datanuts]
    MAM_count = li_diagnose.count('MAM')
    SAM_count = li_diagnose.count('SAM')
    NI_count = li_diagnose.count('SAM+')
    context.update({"MAM_count": MAM_count, "SAM_count": SAM_count, \
                                                    "NI_count": NI_count})
    # Nbre enfant dans le programme
    children_in_program = inp_out.filter(event="e").count()
    # Taux guerison
    nbr_healing = inp_out.filter(event="s", reason="h").count()
    healing_rates = calculation_of_rates(nbr_healing)
    # Taux abandon
    nbr_of_abandonment = inp_out.filter(event="s", reason="a").count()
    abandonment_rates = calculation_of_rates(nbr_of_abandonment)
    # Taux déces
    nbr_deaths = inp_out.filter(event="s", reason="d").count()
    deaths_rates = calculation_of_rates(nbr_deaths)
    # Taux non repondant
    nbr_non_response = inp_out.filter(event="s", reason="n").count()
    non_response_rates = calculation_of_rates(nbr_non_response)
    # Durée moyenne dans le programme
    list_num_days = [(number_days(Patient.objects.get(id=out.patient_id) \
                                         .create_date, out.date)) \
                                         for out in InputOutputProgram.objects\
                                         .filter(event='s')]
    try:
        avg_days = sum(list_num_days) / list_num_days.__len__()
    except:
        avg_days = 0
    context.update({"avg_days": avg_days})
    # Gain de poids moyen
    patients = Patient.objects.all()
    list_weight = []
    for patient in patients:
        datanut_patient = datanuts.filter(patient__id=patient.id) \
                                  .order_by('date')
        if datanut_patient:
            weight = diff_weight(datanut_patient[0].weight, \
                            datanut_patient[len(datanut_patient) - 1].weight)
            list_weight.append(weight)
    avg_weight = sum(list_weight) / list_weight.__len__()
    context.update({"avg_weight": avg_weight})
    # graph

     # message
    received = Inbox.objects.count()
    sent = SentItems.objects.count()

    context.update({"children_in_program": children_in_program, \
                    "healing_rates": healing_rates, \
                    "abandonment_rates": abandonment_rates, \
                    "deaths_rates": deaths_rates, \
                    "non_response_rates": non_response_rates, \
                    "sent": sent, \
                    "received": received})

    return render(request, 'dashboard.html', context)


def calculation_of_rates(nb):
    """ """
    tnb = Patient.objects.all().count()
    return (nb * 100) / tnb
