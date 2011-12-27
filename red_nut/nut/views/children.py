#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render, RequestContext, HttpResponseRedirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.core.urlresolvers import reverse

from nut.models import Patient, Seat, InputOutputProgram


class ChildrenForm(forms.Form):
    """ """
    seat = forms.ChoiceField(label=ugettext_lazy(u"Centre de centé"), \
                         choices=[('', _(u"All"))] + [(seat.code, seat.name) \
                                  for seat in Seat.objects.all() \
                                                          .order_by('name')])


class ResearchForm(forms.Form):
    """  """
    id_patient = forms.CharField(max_length=20, label="L'Identifiant")


def children(request):
    category = 'children'
    context = {}
    context.update({"category": category, "message": u"L'identifiant"})

    patients = Patient.objects.all()
    if request.method == "POST":
        form_r = ResearchForm(request.POST)
        form = ChildrenForm(request.POST)
        if "seat" in request.POST:
            if request.POST.get('seat'):
                patients = patients.filter(seat__code=request.POST.get('seat'))
        if "id_patient" in request.POST:
            if request.POST.get('id_patient'):
                try:
                    patient = patients.filter(id=request.POST \
                                              .get('id_patient'))
                    return HttpResponseRedirect(reverse("details_child", \
                                                        args=[patient[0].id]))
                except:
                    context.update({"message": u"Cet id ne correspond à "
                                               u"aucun patient \n\n"})
                    pass
    else:
        form = ChildrenForm()
        form_r = ResearchForm()

    for patient in patients:
        patient_last = InputOutputProgram.objects.filter(patient__id=patient.id).order_by('-date')
        if patient_last:
            patient.status = patient_last[0].event
        patient.url_patient = reverse("details_child", \
                                                args=[patient.id])

    context.update({"patients": patients, "form_r": form_r, "form": form})
    return render(request, 'children.html', context)
