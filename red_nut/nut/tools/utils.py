#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin


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
