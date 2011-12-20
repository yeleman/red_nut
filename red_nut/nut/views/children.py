#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.contrib import messages
from django.shortcuts import render, RequestContext, redirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.conf import settings
from django.core.urlresolvers import reverse

from nut.models import Patient, Seat


class childrenForm(forms.Form):

    seat = forms.ChoiceField(label=ugettext_lazy(u"Centre de centé"), \
                         choices=[('', _(u"All"))] + [(seat.code, seat.name) \
                                  for seat in Seat.objects.all() \
                                                          .order_by('name')])


def children(request):
    category = 'children'
    context = {}
    context.update({"category":category})

    patients = Patient.objects.all()
    for patient in patients:
        patient.url_patient = reverse("details_child", args=[patient.id])
    if request.method == "POST":
        form = childrenForm(request.POST)
        if request.POST.get('seat'):
            patients = patients.filter(seat__code=request.POST.get('seat'))
    else:
        form = childrenForm()

    context.update({"patients": patients, "form":form})

    return render(request, 'children.html', context)
