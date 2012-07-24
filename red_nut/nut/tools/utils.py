#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from datetime import datetime, timedelta


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


def date_range(start, stop=None, days=1):
    """ """
    stop = stop or datetime.today()

    while(start <= stop):
        yield start
        start += timedelta(days)

    yield stop


def week_range(start, stop=None, days=1):
    """ """
    return date_range(start, stop, 7)



def percentage_calculation(nb, tnb):
    try:
        return (nb * 100) / tnb
    except ZeroDivisionError:
        return 0


def extract(data, *keys, **kwargs):
    """
        Extract a data from nested mapping and sequences using a list of keys
        and indices to apply successively. If a key error or an index error
        is raised, returns the default value.

        res = extract(data, 'test', 0, 'bla')

        is the equivalent of

        try:
            res = data['test'][0]['bla']
        except (KeyError, IndexError):
            res = None

    """

    try:
      value = data[keys[0]]
      for key in keys[1:]:
          value = value[key]
    except (KeyError, IndexError, TypeError):
      return kwargs.get('default', None)

    return value


def weight_gain_calc(last_datanut, min_datanut):
    """
        Calcul le gain de poids avec la formule suivante:
        gain de poids = ((poids de sorti * 1000) -
                         (poids le plus bas * 1000)) /
                         (poids le plus bas * (date de sorti -
                          date du poids le plus bas))
    """
    try:
        gain = ((last_datanut.weight * 1000)
                - (min_datanut.weight * 1000)) / \
               (min_datanut.weight
                * (last_datanut.date - min_datanut.date).days)
    except ZeroDivisionError:
        gain = 0
    return gain