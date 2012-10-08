#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga


from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from nut.models import HealthCenter, Patient, ProgramIO


@login_required
def health_center(request):
    """ """
    context = {"category": 'health_center', "user": request.user}

    health_centers = HealthCenter.objects.exclude(parent=None)
    movements =  Patient.by_uren.all()
    liste_health_center = []
    for health_center in health_centers:
        movement = movements\
                    .filter(health_center=health_center).all_uren()
        dict_hc = {}
        nb_supports = [patient for patient in movement \
                                if patient.last_data_event()\
                                .event == ProgramIO.SUPPORT].__len__()
        nb_reason_ab = [patient for patient in movement \
                                if patient.last_data_event()\
                                .reason == ProgramIO.ADBANDONMENT].__len__()
        dict_hc["health_center"] = health_center.name
        dict_hc["nb_child"] = len(movement)
        dict_hc["nb_supports"] = nb_supports
        dict_hc["Reason_type"] = nb_reason_ab
        dict_hc["url"] = reverse("details_health_center", \
                                args=[health_center.id])
        liste_health_center.append(dict_hc)

    context.update({"liste_health_center": liste_health_center})

    return render(request, 'health_center.html', context)
