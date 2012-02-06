#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from django import forms
from django.shortcuts import render, RequestContext, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from nut.models import Patient, HealthCenter


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
def children(request, *args, **kwargs):
    category = 'children'
    context = {'user': request.user.get_full_name()}
    context.update({"category": category, "message": u"Recherche "})

    patients = Patient.objects.all()
    if request.method == "POST":
        form_r = ResearchForm(request.POST)
        form = ChildrenForm(request.POST)
        if "health_center" in request.POST:
            if request.POST.get('health_center'):
                patients = patients.filter(health_center__code=request \
                                   .POST.get('health_center'))
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
        patient.url_patient = reverse("details_child", args=[patient.id])

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
