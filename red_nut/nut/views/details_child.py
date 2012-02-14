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

    context = {'category': "children",\
               'user': request.user}
    patient = Patient.objects.get(id=num)
    movements = ProgramIO.objects.filter(patient__id=patient.id)

    if patient.last_data_event():
        patient.status = patient.last_data_event().get_event_display()
    try:
        output = movements.filter(event=ProgramIO.OUT).latest('date')
        context.update({"output": output})
    except:
        pass

    try:
        input_ = movements.latest('date')
        data_nuts = NutritionalData.objects.filter(patient__id=num)
        datanuts = data_nuts.order_by('-date')
        datanuts_ = data_nuts.order_by('date')
        datanut = datanuts.latest('date')
        datanut.zscore = zscore_from(datanut.height, datanut.weight)

        context.update({'input_': input_, 'datanut': datanut, \
                        'datanuts': datanuts})
        list_muac = [datanut.muac for datanut in datanuts_]
        list_weight = [datanut.weight for datanut in datanuts_]
        list_zscore = [zscore_from(datanut.height, datanut.weight) for datanut in datanuts_]
        graph_date = [datanut.date.strftime('%d/%m') for datanut in datanuts_]
        graph_data = [{'name': "Poids", 'data': list_weight}, \
                      {'name': "PB",'data': list_muac}]
        zscore_data = [{'name': "ZSCORE", 'data': list_zscore}]
        context.update({"graph_date": graph_date, "graph_data": graph_data, "zscore_data": zscore_data})
    except NutritionalData.DoesNotExist:
        input_ = movements.latest('date')
        context.update({'error': 'Aucun details nutritionnel',
                                                "input_": input_})
    except ProgramIO.DoesNotExist:
        context.update({'error': 'Aucun details nutritionnel'})

    context.update({'patient': patient})
    return render(request, 'details_child.html', context)
