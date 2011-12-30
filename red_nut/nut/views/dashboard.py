#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.contrib import messages
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings

from nut.models import Seat, InputOutputProgram, Patient, DataNut, Period
from nosms.models import Message
from nut.tools.utils import diagnose_patient, number_days, diff_weight, \
                                                            date_graphic


def dashboard(request):
    """  """
    category = 'dashboard'
    context = {}
    context.update({"category": category})

    inp_out = InputOutputProgram.objects.all()
    datanuts = DataNut.objects.all()

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
    try:
        avg_weight = sum(list_weight) / list_weight.__len__()
    except:
        avg_weight = 0
    context.update({"avg_weight": avg_weight})
    # graphic
    l_date = date_graphic(InputOutputProgram.objects.order_by("date")[0].date)
    total_ = []
    graph_date = []
    diagnose_mam = []
    diagnose_sam = []
    diagnose_ni = []
    for da in l_date:
        input_in_prog = InputOutputProgram.objects.filter(event="e", \
                                                            date__lte=da)
        out_in_prog = InputOutputProgram.objects.filter(event="s", \
                                                            date__lte=da)
        input_out_in_prog = [p for p in  input_in_prog if p.patient.id \
                             not in [i.patient.id for i in out_in_prog]]
        data = DataNut.objects.order_by('date').filter(date__lte=da)
        total_.append(input_in_prog.__len__() - out_in_prog.__len__())
        graph_date.append(da.strftime('%d/%m'))
        l_diagnose = []
        for d in data:
            if d.patient.id in [(i.patient.id) for i in input_out_in_prog]:
                l_diagnose.append(diagnose_patient(d.muac, d.oedema))
        if l_diagnose:
            diagnose_mam.append(l_diagnose.count('MAM'))
            diagnose_sam.append(l_diagnose.count('SAM'))
            diagnose_ni.append(l_diagnose.count('SAM+'))

    graph_data = [{'name': "Total", 'data': total_}, \
                  {'name': "MAM", 'data': diagnose_mam}, \
                  {'name': "SAM", 'data': diagnose_sam}, \
                  {'name': "SAM+", 'data': diagnose_ni}]
    context.update({"graph_date": graph_date, "graph_data":graph_data})
    # Diagnose
    MAM_count = diagnose_mam[-1]
    SAM_count = diagnose_sam[-1]
    NI_count = diagnose_ni[-1]
    # Nbre enfant dans le programme
    children_in_program = total_[-1]
    context.update({"MAM_count": MAM_count, "SAM_count": SAM_count, \
                                                    "NI_count": NI_count})

    # message
    messages = Message.objects.all()
    received = messages.filter(direction=Message.DIRECTION_INCOMING).count()
    sent = messages.filter(direction=Message.DIRECTION_OUTGOING).count()

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
