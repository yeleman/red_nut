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
            inbox = Inbox.objects.filter(receivingdatetime__gte=period \
                         .start_on, receivingdatetime__lte=period.end_on)\
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

    current_period()
    context = {'category': 'log_messagesms_per_center'}

    period_activities = []

    for period in Period.objects.all():

        all_identities = get_all_identities(period)

        contact_activities = []
        sent_counts = 0
        inbox_counts = 0
        register_counts = 0
        fol_counts = 0
        research_counts = 0
        off_counts = 0
        stock_counts = 0

        for identity in all_identities:
            inbox = Inbox.objects.filter(sendernumber=identity)
            sms_type = count_sms_type(inbox)
            if 'register' in sms_type.keys():
                register_counts += sms_type['register']
            if 'fol' in sms_type.keys():
                fol_counts += sms_type['fol']
            if 'research' in sms_type.keys():
                research_counts += sms_type['research']
            if 'off' in sms_type.keys():
                off_counts += sms_type['off']
            if 'stock' in sms_type.keys():
                stock_counts += sms_type['stock']

            inbox_count = Inbox.objects.filter(sendernumber=identity).count()
            sent_count = SentItems.objects \
                                  .filter(destinationnumber=identity) \
                                  .count()
            contact_activities.append({'identity': identity,
                        'inbox_count': inbox_count,
                        'sent_count': sent_count,
                        'sms_type': sms_type})
        inbox_counts = Inbox.objects \
                            .filter(receivingdatetime__gte=period.start_on,
                                    receivingdatetime__lte=period.end_on) \
                            .count()
        sent_counts = SentItems.objects \
                               .filter(sendingdatetime__gte=period.start_on,
                                       sendingdatetime__lte=period.end_on) \
                               .count()
        parts_sent_counts = SentItems.raw \
                               .filter(sendingdatetime__gte=period.start_on,
                                       sendingdatetime__lte=period.end_on) \
                               .count()
        period_activities.append({'period': period,
                                  'contacts': contact_activities,
                                  'sent_counts': sent_counts,
                                  'register_counts': register_counts,
                                  'fol_counts': fol_counts,
                                  'research_counts': research_counts,
                                  'off_counts': off_counts,
                                  'stock_counts': stock_counts,
                                  'inbox_counts': inbox_counts,
                                  'parts_sent_counts': parts_sent_counts})

    context.update({'period_activities': period_activities})
    return render(request, 'sms_per_center.html', context)
