#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou

from nut.models import Period
from django import forms
from django.shortcuts import render


class PeriodForm(forms.Form):
    """ """
    period = forms.ChoiceField(label=(u"Periode:"),
                                      choices=[('', u"Toutes")] +
                                      [(period.id, period.name())
                                       for period in Period \
                                            .objects.all().order_by('id')])

def sms_for_period(period=None):
        from nosmsd.models import Inbox
        inbox = Inbox.objects.all()
        if period:
            inbox = Inbox.objects.filter(receivingdatetime__gte=period.start_on,\
                                          receivingdatetime__lte=period.end_on)\
                                  .all().order_by('-receivingdatetime')
        
        return inbox

def log_message(request):
    """ Display all messages received """
    
    context = {'category': 'log_message'}

    inbox_sms = sms_for_period(period=None)
    form = PeriodForm()
    if request.method == "POST":
        form = PeriodForm(request.POST)

        if form.is_valid():
            period = Period.objects.get(id=request.POST.get('period'))
            inbox_sms = sms_for_period(period)
        
    context.update({'inbox_sms': inbox_sms, 'form': form})
    return render(request, 'log_message.html', context)
