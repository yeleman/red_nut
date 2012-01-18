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
    category = 'health_center'
    context = {}
    context.update({"category": category})

    health_centers = HealthCenter.objects.all()
    inp_out = ProgramIO.objects.all()
    liste_health_center = []
    for health_center in health_centers:
        dict_ = {}
        dict_["health_center"] = health_center.name
        dict_["nb_child"] = inp_out.filter(patient__health_center__id=health_center.id).count()
        dict_["input"] = inp_out.filter(patient__health_center__id=health_center.id, \
                                                            event="e").count()
        dict_["nb_healing"] = inp_out.filter(patient__health_center__id=health_center.id, \
                                                        reason="a").count()
        dict_["url"] = reverse("details_health_center", args=[health_center.id])
        liste_health_center.append(dict_)
    context.update({"liste_health_center": liste_health_center})
    return render(request, 'health_center.html', context)
