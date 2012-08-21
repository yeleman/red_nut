#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.paginator import EmptyPage
from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger

from nut.models import Patient
from nut.tools.digg_paginator import FlynsarmyPaginator


@login_required
def child_delay(request, *args, **kwargs):
    """ """
    category = 'child_delay'
    context = {'user': request.user}
    context.update({"category": category, "message": u"Recherche "})

    patients = [patient.last_data_event() \
                for patient in Patient.objects.all().order_by("create_date") \
                if patient.is_late and not patient.last_data_event().is_output]

    for patient in patients:
        patient.url_details_child = reverse("details_child", \
                                                args=[patient.patient.id])

    #pour mettre 20 rapport par page
    paginator = FlynsarmyPaginator(list(patients), 20, adjacent_pages=1)

    if patients:
        page = request.GET.get('page', 1)
        try:
            patients_list = paginator.page(page)
        except PageNotAnInteger:
            patients_list = paginator.page(1)
        except EmptyPage:
            patients_list = paginator.page(paginator.num_pages)
        # affiche une erreur Http404 si l'on de passe la page est vide
    else:
        patients_list = []

    context.update({'patients': patients_list})
    return render(request, 'child_delay.html', context)
