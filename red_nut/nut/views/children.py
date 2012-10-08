#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.paginator import  EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import PageNotAnInteger

from nut.models import Patient, HealthCenter
from nut.tools.digg_paginator import FlynsarmyPaginator


class ChildrenForm(forms.Form):
    """ """
    health_center = forms.ChoiceField(label=(u"Centre de centé"),
                                      choices=[('', _(u"All"))] +
                                      [(health_center.code, health_center.name)
                                       for health_center in HealthCenter \
                                            .objects.all().order_by('name')])


class ResearchForm(forms.Form):
    """  """
    search_patient = forms.CharField(max_length=20, label="Recherche")


@login_required
def children(request):
    context = {'category': 'children', 'user': request.user}
    context.update({"message": u"Recherche "})

    patients = Patient.by_uren.all().order_by("-create_date").all_uren()

    if request.method == "POST":
        form_r = ResearchForm(request.POST)
        form = ChildrenForm(request.POST)
        if "health_center" in request.POST:
            if request.POST.get('health_center'):
                patients = patients.filter(health_center__code=request \
                                   .POST.get('health_center'))
        if "search_patient" in request.POST:
            if request.POST.get('search_patient'):
                val = request.POST.get('search_patient').title()
                query = (Q(first_name__contains=val) |
                         Q(last_name__contains=val) |
                         Q(surname_mother__contains=val) |
                         Q(nut_id__contains=val))

                patients = Patient.objects.filter(query)

                if not patients:
                    context.update({"message": u"Votre requête ne trouve"
                                               u"aucun patient. \n"})
    else:
        form = ChildrenForm()
        form_r = ResearchForm()

    for patient in patients:
        patient.url_patient = reverse("details_child", args=[patient.id])

    #pour mettre 20 rapport par page
    paginator = FlynsarmyPaginator(list(patients), 20, adjacent_pages=10)

    if patients:
        page = request.GET.get('page', 1)
        try:
            patients_list = paginator.page(page)
        except PageNotAnInteger:
            patients_list = paginator.page(1)
        except EmptyPage:
            patients_list = paginator.page(paginator.num_pages)
    else:
        patients_list = []

    context.update({'patients': patients_list, "form_r": form_r, "form": form})
    return render(request, 'children.html', context)
