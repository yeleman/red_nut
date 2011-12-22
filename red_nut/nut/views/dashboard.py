#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.contrib import messages
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings

from nut.models import Seat, InputOutputProgram, Patient, DataNut
from nosms.models import Message
from nut.tools.utils import diagnose_patient


def dashboard(request):
    category = 'dashboard'
    context = {}
    context.update({"category": category})

    inp_out = InputOutputProgram.objects.all()
    datanut = DataNut.objects.all()

    li_diagnose = [(diagnose_patient(d.muac, d.oedema)) for d in datanut]
    MAM_count = li_diagnose.count('MAM')
    SAM_count = li_diagnose.count('SAM')
    NI_count = li_diagnose.count('SAM+')
    context.update({"MAM_count": MAM_count, "SAM_count": SAM_count, \
                                                    "NI_count": NI_count,})
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
    nbr_non_response = inp_out.filter(event="s", reason="d").count()
    non_response_rates = calculation_of_rates(nbr_non_response)
    #message
    messages = Message.objects.all()
    received = messages.filter(direction=Message.DIRECTION_INCOMING).count()
    sent = messages.filter(direction=Message.DIRECTION_OUTGOING).count()

    context.update({"children_in_program": children_in_program, \
                    "healing_rates": healing_rates, \
                    "abandonment_rates": abandonment_rates, \
                    "deaths_rates": deaths_rates, \
                    "non_response_rates":non_response_rates, \
                    "sent":sent, \
                    "received":received
                    })

    return render(request, 'dashboard.html', context)


def calculation_of_rates(nb):
    """ """
    tnb = Patient.objects.all().count()
    return (nb * 100) / tnb
