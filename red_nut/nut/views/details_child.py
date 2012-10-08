#!/usr/bin/env python
# encoding=utf-8
# maintainer: Alou

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from zscore import zscore_from
from nut.models import Patient, NutritionalData, ProgramIO


@login_required
def details_child(request, *args, **kwargs):
    """ Details sur un enfant """
    num = kwargs["id"]

    context = {'category': "children", \
               'user': request.user}
    patient = Patient.objects.get(id=num)
    movements = ProgramIO.objects.filter(patient__id=patient.id)

    if patient.last_data_event():
        patient.statut = patient.last_data_event().get_event_display()
    try:
        output = movements.filter(event=ProgramIO.OUT).latest('date')
        context.update({"output": output})
    except:
        pass

    try:
        data_nuts = NutritionalData.objects.filter(patient__id=num)
        datanuts = data_nuts.order_by('-date')
        datanuts_ = data_nuts.order_by('date')
        datanut = datanuts.latest('date')
        datanut.zscore = zscore_from(datanut.height, datanut.weight)

        list_muac = [datanut.muac for datanut in datanuts_]
        list_weight = [datanut.weight for datanut in datanuts_]
        list_zscore = [zscore_from(datanut.height, datanut.weight)
                                                     for datanut in datanuts_]

        graph_date = [datanut.date.strftime('%d/%m') for datanut in datanuts_]
        graph_data = [{'name': "Poids", 'data': list_weight},
                      {'name': "PB", 'data': list_muac}]
        zscore_data = [{'name': "ZSCORE", 'data': list_zscore}]

        context.update({"graph_date": graph_date, \
                        "graph_data": graph_data, \
                        "zscore_data": zscore_data, \
                        'datanuts': datanuts})
    except NutritionalData.DoesNotExist:
        context.update({'error': 'Aucun details nutritionnel'})
    except ProgramIO.DoesNotExist:
        context.update({'error': 'Aucun details nutritionnel'})

    if patient.is_healing():
        weight_gain = "%.2f" % patient.weight_gain()
    else:
        weight_gain = None

    context.update({'patient': patient, "diagnosis": NutritionalData.URENS.get(patient.uren),
                    "weight_gain": weight_gain})
    return render(request, 'details_child.html', context)
