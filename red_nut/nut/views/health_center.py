#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.core.urlresolvers import reverse
from django.conf import settings

from nut.models import HealthCenter, ProgramIO


def health_center(request):
    """ """
    context = {"category": 'health_center'}

    health_centers = HealthCenter.objects.all()
    movement = ProgramIO.objects.all()
    liste_health_center = []
    for health_center in health_centers:
        dict_hc = {}
        dict_hc["health_center"] = health_center.name
        dict_hc["nb_child"] = movement\
                    .filter(patient__health_center__id=health_center.id)\
                           .count()
        dict_hc["input"] = movement\
                        .filter(patient__health_center__id=health_center.id,
                                    event=ProgramIO.SUPPORT).count()
        dict_hc["nb_healing"] = movement\
                         .filter(patient__health_center__id=health_center.id,
                                 reason=ProgramIO.ADBANDONMENT)\
                                             .count()
        dict_hc["url"] = reverse("details_health_center", \
                                args=[health_center.id])
        liste_health_center.append(dict_hc)

    context.update({"liste_health_center": liste_health_center})

    return render(request, 'health_center.html', context)
