#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou

from nut.models import Period
from django import forms
from django.shortcuts import render
from nosmsd.models import Inbox, SentItems


class PeriodForm(forms.Form):
    """ """
    period = forms.ChoiceField(label=(u"Periode:"),
                                      choices=[('', u"Toutes")] +
                                      [(period.id, period.name())
                                       for period in Period \
                                            .objects.all().order_by('id')])

def sms_received_for_period(period=None):

        inbox = Inbox.objects.all()
        if period:
            inbox = Inbox.objects.filter(receivingdatetime__gte=period.start_on,\
                                          receivingdatetime__lte=period.end_on)\
                                  .all().order_by('-receivingdatetime')

        return inbox

def log_message(request):
    """ Display all messages received """

    context = {'category': 'log_message'}

    inbox_sms = sms_received_for_period(period=None)
    form = PeriodForm()
    if request.method == "POST":
        form = PeriodForm(request.POST)

        if form.is_valid():
            period = Period.objects.get(id=request.POST.get('period'))
            inbox_sms = sms_received_for_period(period)

    context.update({'inbox_sms': inbox_sms, 'form': form})
    return render(request, 'log_message.html', context)

def sms_per_center(request):
    """ display the number of SMS per center """

    def create_list(inbox, sent):
        identies = []
        for sms in inbox:
            if not sms.identity in identies:
                identies.append(sms.identity)

        for sms in sent:
            if not sms.identity in identies:
                identies.append(sms.identity)

        return identies

    def compte_sms(inbox):
        register = 0
        fol = 0
        research = 0
        off = 0
        stock = 0

        for sms in inbox:
            if 'register' in sms.content:
                register += 1
            if 'fol' in sms.content:
                register += 1
            if 'research' in sms.content:
                register += 1
            if 'off' in sms.content:
                register += 1
            if 'stock' in sms.content:
                register += 1
            print sms.content
        list_values = [register,fol,research,off,stock]
        return list_values

    context = {'category': 'log_messagesms_per_center'}

    inbox = Inbox.objects.all()

    sent = SentItems.objects.all()
    identies =  create_list(inbox, sent)

    sms = []
    for identity in identies:
        inbox = Inbox.objects.filter(sendernumber=identity)
        register, fol, research, off, stock = compte_sms(inbox)
        count_inbox = Inbox.objects.filter(sendernumber=identity).count()
        count_sent = SentItems.objects.filter(destinationnumber=identity).count()
        sms.append({'identity': identity,
                    'count_inbox': count_inbox,
                    'count_sent': count_sent,
                    'register': register, 'fol': fol, 'research': research,
                    'off': off, 'stock': stock})

    context.update({'sms': sms})
    return render(request, 'sms_per_center.html', context)
