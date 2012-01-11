#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render, RequestContext, HttpResponseRedirect
from django.utils.translation import ugettext as _, ugettext_lazy
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from nut.models import Patient, Seat, InputOutputProgram


class ChildrenForm(forms.Form):
    """ """
    seat = forms.ChoiceField(label=ugettext_lazy(u"Centre de centé"), \
                         choices=[('', _(u"All"))] + [(seat.code, seat.name) \
                                  for seat in Seat.objects.all() \
                                                          .order_by('name')])


class ResearchForm(forms.Form):
    """  """
    search_patient = forms.CharField(max_length=20, label="Recherche")


def children(request, *args, **kwargs):
    category = 'children'
    context = {}
    context.update({"category": category, "message": u"Recherche "})

    patients = Patient.objects.all()
    if request.method == "POST":
        form_r = ResearchForm(request.POST)
        form = ChildrenForm(request.POST)
        if "seat" in request.POST:
            if request.POST.get('seat'):
                patients = patients.filter(seat__code=request.POST.get('seat'))
        if "search_patient" in request.POST:
            if request.POST.get('search_patient'):
                val = request.POST.get('search_patient')

                query = (Q(first_name__contains=val) |
                         Q(last_name__contains=val) |
                         Q(surname_mother__contains=val))

                try:
                    query = query | Q(id__contains=int(val))
                except ValueError:
                    pass

                patients = Patient.objects.filter(query)

                if not patients:
                    context.update({"message": u"Votre requête ne trouve"
                                               u"aucun patient. \n"})
    else:
        form = ChildrenForm()
        form_r = ResearchForm()

    for patient in patients:
        patient_last = InputOutputProgram.objects \
                                            .filter(patient__id=patient.id)\
                                            .order_by('-date')
        if patient_last:
            patient.status = patient_last[0].get_event_display()
        patient.url_patient = reverse("details_child", args=[patient.id])

    num = kwargs["num"] or 1
    #pour mettre 20 rapport par page
    paginator = Paginator(patients, 15)
    try:
        page = paginator.page(int(num))
        # si le numero de la page est 2
        page.is_before_first = (page.number == 2)
        # si le numero de la page est egale au numero de l'avant derniere page
        page.is_before_last = (page.number == paginator.num_pages - 1)
        # On constitue l'url de la page suivante
        page.url_next = reverse("children", args=[int(num) + 1])
        # On constitue l'url de la page precedente
        page.url_previous = reverse("children", args=[int(num) - 1])
        # On constitue l'url de la 1ere page
        page.url_first = reverse("children")
        # On constitue l'url de la derniere page
        page.url_last = reverse("children", args=[paginator.num_pages])
        context.update({"page": page, "paginator": paginator, \
                                                        "lien": "before"})
    # affiche une erreur Http404 si l'on de passe la page est vide
    except EmptyPage:
        pass

    context.update({"form_r": form_r, "form": form})
    return render(request, 'children.html', context)
