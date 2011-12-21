#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
#~ from django.contrib import meseatages
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.core.urlresolvers import reverse
from django.conf import settings

from nut.models import Seat, InputOutputProgram


def health_center(request):
    category = 'health_center'
    context = {}
    context.update({"category": category})

    seats = Seat.objects.all()
    inp_out = InputOutputProgram.objects.all()
    liste_seat = []
    for seat in seats:
        dict_ = {}
        dict_["seat"] = seat.name
        dict_["nb_child"] = inp_out.filter(patient__seat__id = seat.id).count()
        dict_["input"] = inp_out.filter(patient__seat__id = seat.id, event ="e").count()
        dict_["nb_healing"] = inp_out.filter(patient__seat__id=seat.id, reason="a").count()
        dict_["url"] = reverse("details_health_center", \
                                                args=[seat.id])
        liste_seat.append(dict_)
    context.update({"liste_seat": liste_seat})
    return render(request, 'health_center.html', context)
