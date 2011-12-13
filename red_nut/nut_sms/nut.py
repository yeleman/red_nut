#!/usr/bin/env python
# encoding: utf-8
# maintainer: Fad/Alou

import datetime
import logging
import locale
from datetime import date
import reversion
from django.conf import settings

from nosms.models import Message
from nosms.utils import send_sms
from red_nut.nut.models import Stock, DataNut, Patient
from red_nut.nut.models import Seat
from red_nut.nut.models import Input
from red_nut.nut.models.Period import MonthPeriod

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, settings.DEFAULT_LOCALE)


def nosms_handler(message):
    def main_nut_handler(message):
        if message.text.lower().startswith('nut '):
            if message.text.lower().startswith('nut stock'):
                return nut_stock(message)
            if message.text.lower().startswith('nut fol'):
                return followed_child(message)
        else:
            return False

    if main_nut_handler(message):
        message.status = Message.STATUS_PROCESSED
        message.save()
        logger.info(u"[HANDLED] msg: %s" % message)
        return True
    logger.info(u"[NOT HANDLED] msg : %s" % message)
    return False


def nut_stock(message):
    """ Incomming:
            nut stock seat month year intrant stock_initial stock_received
            stock_used stock_lost
        Outgoing:
            [SUCCES] Le rapport de stock de seat a ete bien enregistre.
            or error message """

    # common start of error message
    error_start = u"Impossible d'enregistrer le rapport. "
    try:
        args_names = ['kw1', 'kw2', 'seat', 'month', 'year', \
        'intrant', 'stock_initial', \
        'stock_received', \
        'stock_used', \
        'stock_lost']
        args_values = message.text.strip().lower().split()
        arguments = dict(zip(args_names, args_values))
    except ValueError:
        # failure to split means we proabably lack a data or more
        # we can't process it.
        message.respond(error_start + u" Le format du SMS est incorrect.")
        return True
    try:
        for key, value in arguments.items():
            if key.split('_')[0] in ('stock_initial', 'stock_received', \
                                'stock_used', 'stock_used', 'month', 'year'):
                arguments[key] = int(value)
    except:
        # failure to convert means non-numeric value which we can't process.
        message.respond(error_start + u" Les données sont malformées.")
        return True

    # create the report
    try:
        stock = Stock()
        stock.period = MonthPeriod. \
                                find_create_from(year=arguments.get('year'), \
                                month=arguments.get('month'))
        stock.seat = Seat.objects.get(code=arguments.get('seat'))
        stock.intrant = Input.objects.get(code=arguments.get('intrant'))
        stock.stock_initial = arguments.get('stock_initial')
        stock.stock_received = arguments.get('stock_received')
        stock.stock_used = arguments.get('stock_used')
        stock.stock_lost = arguments.get('stock_lost')

        stock.save()

    except Exception as e:
        message.respond(error_start + u"Une erreur technique s'est " \
                        u"produite. Reessayez plus tard et " \
                        u"contactez YELEMAN si le probleme persiste.")
        logger.error(u"Unable to save report to DB. Message: %s | Exp: %r" \
                     % (message.text, e))
        return True
    except Exception as e:
        message.respond(error_start + u"Une erreur technique s'est " \
                        u"produite. Reessayez plus tard et " \
                        u"contactez YELEMAN si le probleme persiste.")
        logger.error(u"Unable to save report to DB. Message: %s | Exp: %r" \
                     % (message.text, e))
        return True
    message.respond(u"[SUCCES] Le rapport de stock de %(seat)s "
                    u"a ete bien enregistre. " %
                    {'seat': stock.seat.name})
    return True


def followed_child(message):
    """ Incomming:
            nut fol id date weight heught pb danger_sign
        Outgoing:
            [SUCCES] Les données nutritionnelles de full_name ont
            ete bien enregistre.
            or error message """

    # common start of error message
    error_start = u"Impossible d'enregistrer le rapport. "
    try:
        args_names = ['kw1', 'kw2', 'id', 'date', 'weight', \
        'heught', 'pb', 'danger_sign']
        args_values = message.text.strip().lower().split()
        arguments = dict(zip(args_names, args_values))
    except ValueError:
        # failure to split means we proabably lack a data or more
        # we can't process it.
        message.respond(error_start + u" Le format du SMS est incorrect.")
        return True

    try:
        for key, value in arguments.items():
            if key.split('_')[0] in ('id', 'weight', 'heught', 'pb'):
                arguments[key] = int(value)
        d, m, y = arguments.get('date').split('/')
        date_ = date(int(y), int(m), int(d))
    except:
        # failure to convert means non-numeric value which we can't process.
        message.respond(error_start + u" Les données sont malformées.")
        return True
    # create the datanut
    try:
        datanut = DataNut()
        datanut.patient = Patient.objects.get(id=arguments.get('id'))
        datanut.date = date_
        datanut.weight = arguments.get('weight')
        datanut.heught = arguments.get('heught')
        datanut.pb = arguments.get('pb')
        datanut.danger_sign = arguments.get('danger_sign')

        datanut.save()
    except Exception as e:
        message.respond(error_start + u"Une erreur technique s'est " \
                        u"produite. Reessayez plus tard et " \
                        u"contactez YELEMAN si le probleme persiste.")
        logger.error(u"Unable to save report to DB. Message: %s | Exp: %r" \
                     % (message.text, e))
        return True
    except Exception as e:
        message.respond(error_start + u"Une erreur technique s'est " \
                        u"produite. Reessayez plus tard et " \
                        u"contactez YELEMAN si le probleme persiste.")
        logger.error(u"Unable to save report to DB. Message: %s | Exp: %r" \
                     % (message.text, e))
        return True

    message.respond(u"[SUCCES] Les données nutritionnelles de %(full_name)s "
                    u"ont ete bien enregistre. " %
                    {'full_name': datanut.patient.full_name()})
