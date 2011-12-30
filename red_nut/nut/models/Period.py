#!/usr/bin/env python
# encoding=utf-8
# maintainer: Fadiga

from datetime import datetime, date, timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from nut.tools.utils import week_from_weeknum, next_month


class DayManager(models.Manager):
    def get_query_set(self):
        return super(DayManager, self).get_query_set() \
                                      .filter(period_type=Period.DAY)


class WeekManager(models.Manager):
    def get_query_set(self):
        return super(WeekManager, self).get_query_set() \
                                       .filter(period_type=Period.WEEK)


class MonthManager(models.Manager):
    def get_query_set(self):
        return super(MonthManager, self).get_query_set() \
                                        .filter(period_type=Period.MONTH)


class QuarterManager(models.Manager):
    def get_query_set(self):
        return super(QuarterManager, self).get_query_set() \
                                          .filter(period_type=Period.QUARTER)


class SemesterManager(models.Manager):
    def get_query_set(self):
        return super(SemesterManager, self).get_query_set() \
                                           .filter(period_type=Period.SEMESTER)


class YearManager(models.Manager):
    def get_query_set(self):
        return super(YearManager, self).get_query_set() \
                                       .filter(period_type=Period.YEAR)


class CustomManager(models.Manager):
    def get_query_set(self):
        return super(CustomManager, self).get_query_set() \
                                        .filter(period_type=Period.CUSTOM)


class Period(models.Model):
    ''' Represents a Period of time. Base class ; should not be used directly.

    Use DayPeriod, MonthPeriod, etc instead.
    Provides easy way to find/create period for reporting.

    p = MonthPeriod.find_create_from(2011, 3)
    p.next() '''

    class Meta:
        app_label = 'nut'
        unique_together = ('start_on', 'end_on', 'period_type')
        verbose_name = _(u"Period")
        verbose_name_plural = _(u"Periods")

    ONE_SECOND = 0.0001
    ONE_MICROSECOND = 0.00000000001

    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    QUARTER = 'quarter'
    SEMESTER = 'semester'
    YEAR = 'year'
    CUSTOM = 'custom'

    PERIOD_TYPES = (
        (DAY, _(u"Day")),
        (WEEK, _(u"Week")),
        (MONTH, _(u"Month")),
        (QUARTER, _(u"Quarter")),
        (SEMESTER, _(u"Semester")),
        (YEAR, _(u"Year")),
        (CUSTOM, _(u"Custom")),
    )

    start_on = models.DateTimeField(_(u"Start On"))
    end_on = models.DateTimeField(_(u"End On"))
    period_type = models.CharField(max_length=15, \
                                   choices=PERIOD_TYPES, default=CUSTOM, \
                                   verbose_name=_(u"Type"))

    objects = models.Manager()
    days = DayManager()
    weeks = WeekManager()
    months = MonthManager()
    quarters = QuarterManager()
    semesters = SemesterManager()
    years = YearManager()
    customs = CustomManager()
    django = models.Manager()

    @classmethod
    def type(cls):
        ''' default type for period creation '''
        return cls.CUSTOM

    @classmethod
    def delta(self):
        ''' timedelta() length of a period. 1 = one day. '''
        return 1 / 24

    @property
    def pid(self):
        ''' A locale safe identifier of the period '''
        return self.middle().strftime('%s')

    def middle(self):
        ''' datetime at half of the period duration '''
        return self.start_on + ((self.end_on - self.start_on) / 2)

    def __unicode__(self):
        return self.name()

    def name(self):
        try:
            cls = eval(u"%sPeriod" % self.period_type.title())
            return cls.objects.get(id=self.id).name()
        except:
            # TRANSLATORS: Python date format for Generic .name()
            return self.middle().strftime(ugettext('%c'))

    def full_name(self):
        return self.name()

    def next(self):
        ''' returns next period in time '''
        return self.find_create_by_date(self.middle() \
                                        + timedelta(self.delta()))

    def previous(self):
        ''' returns next period in time '''
        return self.find_create_by_date(self.middle() \
                                        - timedelta(self.delta()))

    @classmethod
    def boundaries(cls, date_obj):
        ''' start and end dates of a period from a date. '''
        start = date_obj - timedelta(cls.delta() / 2)
        end = start + cls.delta()
        return (start, end)

    def includes(self, date_obj):
        ''' check if provided value is within this Period's scope

        date_obj can be:
         * datetime instance
         * date instance
         * integer (year) '''
        if isinstance(date, date_obj):
            date_obj = datetime(date.year, date.month, date.day, 12, 0)
        if isinstance(datetime, date_obj):
            return self.start_on < date_obj and self.end_on > date_obj
        elif isinstance(int, date_obj):
            pass
        return False
        # not sure what to do??
        raise ValueError("Can not understand date object.")

    @classmethod
    def find_create_from(cls, year, month=None, day=None, \
                         week=None, hour=None, minute=None, second=None, \
                         dont_create=False):

        if not week and not month:
            # assume year search
            sy = datetime(year, 1, 1, 0, 0)
            ey = sy.replace(year=year + 1) - timedelta(ONE_MICROSECOND)
            try:
                period = cls.objects.filter(start_on__lte=sy, \
                                            end_on__gte=ey)[0]
            except IndexError:
                period = cls.find_create_with(sy, ey)
            return period

        if week:
            sw, ew = week_from_weeknum(year, week, is_iso=False)
            period = cls.find_create_with(sw, ew)
            return period

        month = month if month else 1
        day = day if day else 1
        hour = hour if hour else 0
        minute = minute if minute else 0
        second = second if second else 0

        date_obj = datetime(year, month, day, hour, minute, second)

        period = cls.find_create_by_date(date_obj, dont_create)

        return period

    @classmethod
    def find_create_by_date(cls, date_obj, dont_create=False):
        ''' creates a period to fit the provided date in '''
        if not isinstance(date_obj, datetime):
            date_obj = datetime.fromtimestamp(float(date_obj.strftime('%s')))

        try:
            period = [period for period in cls.objects.all() \
                                        if period.start_on <= date_obj \
                                        and period.end_on >= date_obj][0]
        except IndexError:
            if dont_create:
                raise
            period = cls.find_create_with(*cls.boundaries(date_obj))
            period.save()
        return period

    @classmethod
    def find_create_with(cls, start_on, end_on, period_type=None):
        ''' creates a period with defined start and end dates '''
        if not period_type:
            period_type = cls.type()
        try:
            period = cls.objects.get(start_on=start_on, \
                                     end_on=end_on, period_type=period_type)
        except cls.DoesNotExist:
            period = cls(start_on=start_on, end_on=end_on, \
                         period_type=period_type)
            period.save()
        return period


class DayPeriod(Period):

    class Meta:
        proxy = True
        app_label = 'bolibana'
        verbose_name = _(u"Period")
        verbose_name_plural = _(u"Periods")

    objects = DayManager()

    @classmethod
    def type(cls):
        return cls.DAY

    def name(self):
        # Translators: Python's date format for DayPeriod.name()
        return self.middle().strftime(ugettext('%x'))

    @classmethod
    def delta(self):
        return 1

    @classmethod
    def boundaries(cls, date_obj):
        start = date_obj.replace(hour=0, minute=0, \
                                 second=0, microsecond=0)
        end = start + timedelta(cls.delta()) - timedelta(ONE_MICROSECOND)
        return (start, end)


class MonthPeriod(Period):

    class Meta:
        proxy = True
        app_label = 'bolibana'
        verbose_name = _(u"Period")
        verbose_name_plural = _(u"Periods")

    objects = MonthManager()

    @classmethod
    def type(cls):
        return cls.MONTH

    @property
    def pid(self):
        return self.middle().strftime('%m%Y')

    def name(self):
        # Translators: Python's date format for MonthPeriod.name()
        return ugettext(u"%(formatted_date)s") % \
                 {'formatted_date': self.middle().strftime(ugettext('%m %Y'))}

    def full_name(self):
        # Translators: Python's date format for MonthPeriod.full_name()
        return ugettext(u"%(formatted_date)s") % \
                 {'formatted_date': self.middle()\
                                        .strftime(ugettext('%B %Y'))\
                                        .decode('utf-8')}

    @classmethod
    def delta(self):
        return 28

    @classmethod
    def boundaries(cls, date_obj):
        nyear, nmonth = next_month(date_obj.year, date_obj.month)

        start = date_obj.replace(day=1, hour=0, minute=0, \
                                 second=0, microsecond=0)
        end = start.replace(year=nyear, month=nmonth) \
              - timedelta(cls.ONE_MICROSECOND)
        return (start, end)


class YearPeriod(Period):

    class Meta:
        proxy = True
        app_label = 'bolibana'
        verbose_name = _(u"Period")
        verbose_name_plural = _(u"Periods")

    objects = YearManager()

    @classmethod
    def type(cls):
        return cls.YEAR

    def name(self):
        # Translators: Python's date format for YearPeriod.name()
        return self.middle().strftime(ugettext('%Y'))

    @classmethod
    def delta(self):
        return 365

    @classmethod
    def boundaries(cls, date_obj):
        start = date_obj.replace(month=0, day=0, hour=0, minute=0, \
                                 second=0, microsecond=0)
        end = start + timedelta(cls.delta()) - timedelta(ONE_MICROSECOND)
        return (start, end)
