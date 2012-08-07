#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.decorators import login_required

from nut.models import Patient


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

    num = kwargs["num"] or 1
    #pour mettre 20 rapport par page
    paginator = Paginator(patients, 20)
    try:
        page = paginator.page(int(num))
        # si le numero de la page est 2
        page.is_before_first = (page.number == 2)
        # si le numero de la page est egale au numero de l'avant derniere page
        page.is_before_last = (page.number == paginator.num_pages - 1)
        # On constitue l'url de la page suivante
        page.url_next = reverse("child_delay", args=[int(num) + 1])
        # On constitue l'url de la page precedente
        page.url_previous = reverse("child_delay", args=[int(num) - 1])
        # On constitue l'url de la 1ere page
        page.url_first = reverse("child_delay")
        # On constitue l'url de la derniere page
        page.url_last = reverse("child_delay", args=[paginator.num_pages])
        context.update({"page": page, "paginator": paginator, \
                                                        "lien": "before"})
    # affiche une erreur Http404 si l'on de passe la page est vide
    except EmptyPage:
        pass

    return render(request, 'child_delay.html', context)
