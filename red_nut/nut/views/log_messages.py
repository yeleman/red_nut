#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou

from nut.models import Period
from django import forms
from django.shortcuts import render
from nosmsd.models import Inbox, SentItems

from red_nut.nut.models.period import MonthPeriod


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

def current_period():
    """ Period of current date """
    from datetime import date
    return MonthPeriod.find_create_by_date(date.today())

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

    def get_all_identities(period):
        identities = []

        inbox = Inbox.objects.filter(receivingdatetime__gte=period.start_on,
                                     receivingdatetime__lte=period.end_on)

        sent = SentItems.objects.filter(sendingdatetime__gte=period.start_on,
                                        sendingdatetime__lte=period.end_on)

        for sms in inbox:
            if not sms.identity in identities:
                identities.append(sms.identity)

        for sms in sent:
            if not sms.identity in identities:
                identities.append(sms.identity)

        return identities

    def count_sms_type(inbox):
        keywords = ['register', 'fol', 'research', 'off', 'stock']
        counts = {}

        for sms in inbox:
            for kw in keywords:
                if sms.content.startswith('nut %s' % kw):
                    counts[kw] = counts.get(kw, 0) + 1

        return counts

    context = {'category': 'log_messagesms_per_center'}

    period_activities = []

    for period in Period.objects.all():

        all_identities = get_all_identities(period)

        contact_activities = []
        for identity in all_identities:
            inbox = Inbox.objects.filter(sendernumber=identity)
            sms_type = count_sms_type(inbox)
            inbox_count = Inbox.objects.filter(sendernumber=identity).count()
            sent_count = SentItems.objects.filter(destinationnumber=identity).count()
            contact_activities.append({'identity': identity,
                        'inbox_count': inbox_count,
                        'sent_count': sent_count,
                        'sms_type': sms_type})
        period_activities.append({'period': period,
                                  'contacts':contact_activities})

    context.update({'period_activities': period_activities})
    return render(request, 'sms_per_center.html', context)
