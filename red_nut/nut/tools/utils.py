#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from datetime import date, timedelta


def week_from_weeknum(year, weeknum, is_iso=False):
    """ datetime tuple of start/end of week from a week number (and year) """
    sy = datetime(year, 1, 1, 0, 0)
    ey = datetime(year, 12, 31, 23, 59)
    ONE_WEEK = 7
    ONE_SEC = 0.00001

    # retrieve start of year day
    sy_dow = sy.isoweekday if is_iso else sy.weekday()

    # find first real week (first Mon/Sun)
    if sy_dow != 0:
        sy = sy + timedelta(ONE_WEEK - sy_dow)

    # if we want first week, it's from Jan 1st to next Mon/Sun
    if weeknum == 0:
        start_week = sy
        end_week = start_week + timedelta(ONE_WEEK - sy_dow) \
                              - timedelta(ONE_SEC)
    else:
        weeknum -= 1  # cause we've set start as first real week
        start_week = sy + timedelta(ONE_WEEK * weeknum)
        end_week = start_week + timedelta(ONE_WEEK) - timedelta(ONE_SEC)

    return (start_week, end_week)


def next_month(year, month):
    """ next year and month as int from year and month """
    if month < 12:
        return (year, month + 1)
    else:
        return (year + 1, 1)


def diagnose_patient(muac, oedema):
    '''Diagnosis of the patient'''
    if muac is None or muac == 0:
        return None
    elif muac < 80:
        return "SAM+"
    elif oedema == 'Y' or muac < 110:
        return "SAM"
    elif muac < 125:
        return "MAM"


def number_days(begin, end):
    ''' return the number of days in two dates '''
    if end and begin:
        number = end - begin
        return number.days
    return None


def diff_weight(p1, p2):
    return p2 - p1


def date_graphic(date_on):
    l_date = [date_on]
    while(date_on <= date.today()):
        date_on += timedelta(7)
        l_date.append(date_on)
    return l_date
