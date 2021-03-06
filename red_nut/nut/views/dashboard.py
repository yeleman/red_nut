#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from nut.models import ProgramIO, Patient, NutritionalData
from nosmsd.models import Inbox, SentItems
from nut.tools.utils import week_range, percentage_calculation, extract


@login_required
def dashboard(request):

    context = {"category": 'dashboard', 'user': request.user}

    # le nombre total d'enfant
    patients = Patient.by_uren.all().all_uren()
    nbr_total_patient = len(patients)

    # Taux guerison
    nbr_healing = len(ProgramIO.healing.all().all_uren())
    healing_rates = percentage_calculation(nbr_healing,
                                                      nbr_total_patient)

    # Taux abandon
    nbr_abandonment = len(ProgramIO.abandon.all().all_uren())
    abandonment_rates = percentage_calculation(nbr_abandonment,
                                                      nbr_total_patient)
    # Taux déces
    nbr_deaths = len(ProgramIO.death.all().all_uren())
    deaths_rates = percentage_calculation(nbr_deaths, nbr_total_patient)

    # Taux non repondant
    nbr_non_response = len(ProgramIO.nonresp.all().all_uren())

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
    context.update({"avg_weight": "%.2f" % Patient.avg_weight_gain()})

    # graphic
    total_patient = []
    graph_date = []
    diagnose_samp = []
    diagnose_sam = []
    # Ordonne les programio par order décroissante
    programio = ProgramIO.by_uren.order_by('-date').all_uren()

    nbr_date_graph = len(programio)
    if len(programio) > 100:
        nbr_date_graph = 100

    try:
        week_dates = week_range(programio[nbr_date_graph].date)
    except IndexError:
        week_dates = []

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
                l_diagnose.append(patient.uren)
            except NutritionalData.DoesNotExist:
                pass
        diagnose_samp.append(l_diagnose.count(NutritionalData.SAMP))
        diagnose_sam.append(l_diagnose.count(NutritionalData.SAM))

        graph_data = [{'name': "Total", 'data': total_patient},
                      {'name': "MAS+", 'data': diagnose_samp},
                      {'name': "MAS", 'data': diagnose_sam}]

        context.update({"graph_date": graph_date, "graph_data": graph_data})

    # Diagnose
    SAMP_count = extract(diagnose_samp, -1, default=0)
    SAM_count = extract(diagnose_sam, -1, default=0)

    # Nbre d'enfant dans le programme
    children_in_program = extract(total_patient, -1, default=0)

    # Nbre d'enfant en retard de consultation
    patients_late = []
    for patient in patients:
        if not patient.last_data_event().is_output and patient.is_late:
            patients_late.append(patient)
    patients_late = len(patients_late)

    # message
    received = Inbox.objects.count()
    sent = SentItems.objects.count()

    context.update({"children_in_program": children_in_program, \
                    "sent": sent, "received": received, \
                    "SAMP_count": SAMP_count, "SAM_count": SAM_count, \
                    "patients_late": patients_late})

    return render(request, 'dashboard.html', context)


def dashboard_clear_cache(request):
    # clear the whole django cache
    from django.core.cache import get_cache
    cache = get_cache('default')
    cache.clear()
    return HttpResponse(u"OK")
