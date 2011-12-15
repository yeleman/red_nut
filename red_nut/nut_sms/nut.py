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
from red_nut.nut.models import Stock, DataNut, Patient, Seat, Input
from red_nut.nut.models.Period import MonthPeriod

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, settings.DEFAULT_LOCALE)


def nosms_handler(message):
    def main_nut_handler(message):
        if message.text.lower().startswith('nut '):
            if message.text.lower().startswith('nut stock'):
                return nut_stock(message)
            elif message.text.lower().startswith('nut fol'):
                return followed_child(message)
            elif message.text.lower().startswith('nut register'):
                return nut_register(message)
            elif message.text.lower().startswith('nut research'):
                return id_information_research(message)
            elif message.text.lower().startswith('nut off'):
                return disable_child(message)
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


def nut_register(message):
    """ Incomming:
            nut register seat first_name last_name surname_mother DDN_Age
        Outgoing:
            [SUCCES] Le rapport de Asacotoqua a été enregistre. Son id est 8.
            or [ERROR] xxxx n'est un code siège valid """

    nut, register, code_seat, first_name, last_name, surname_mother, \
                        DDN_Age = message.text.strip().lower().split()
    try:
        # On essai prendre le seat
        seat = Seat.objects.get(code=code_seat)
    except:
        # On envoi un sms pour signaler que le code n'est pas valid
        message.respond(u"[ERROR] %(seat)s n'est un code siège valid" % \
                                                        {'seat': code_seat})
        seat = None
    if seat != None:
        report = Patient()
        report.first_name = first_name
        report.last_name = last_name
        report.surname_mother = surname_mother
        report.DDN_Age = DDN_Age
        report.seat = seat
        report.save()
        message.respond(u"[SUCCES] Le rapport de %(seat)s a été "
                        u"enregistre. Son id est %(id)s." \
                        % {'seat': seat, 'id': report.id})
    return True


def id_information_research(message):
    """ Incomming:
            nut research seat first_name(op) last_name(op) surname_mother(op)
            None = n
        Outgoing:
            [SUCCES] Le rapport de Asacotoqua a été enregistre. Son id est 8.
            or  xxx n'est pas enregistrer"""

    nut, research, code_seat, first_name, last_name, \
                    surname_mother = message.text.strip().lower().split()
    #Si SMS ne contient que le nom
    if first_name == "n" and surname_mother == "n":
        patient = [(u"%(first)s %(mother)s de l'id %(id)s" % \
                    {"id":op.id,"first": op.first_name, \
                    "mother": op.surname_mother}) for op in \
                        Patient.objects.filter(seat__code=code_seat, \
                        last_name=last_name)]
        if patient:
            message.respond(u" Il existe %(nber)s patient(s) du nom %(last_name)s: %(patient)s." \
                        % {'nber': patient.__len__(), 'last_name': last_name, \
                            'patient': ', '.join(patient)})
        else:
            message.respond(u"Il n'existe aucun patient du nom %(last_name)s" \
                        % {'last_name': last_name})
    #Si SMS ne contient que le prénom et nom de mère
    if first_name != "n" and surname_mother != "n" and last_name == "n":
        patient = [(u"%(last)s de l'id %(id)s" % \
                    {"id":op.id, "last": op.last_name}) for op in \
                        Patient.objects.filter(seat__code=code_seat, \
                                                surname_mother=surname_mother, \
                                                first_name=first_name)]
        if patient:
            message.respond(u" Il existe %(nber)s patient(s) du prénom %(first_name)s " \
                            u"et nom de mère %(surname_mother)s: %(patient)s." \
                            % {'nber': patient.__len__(), \
                            'first_name': first_name, \
                            'surname_mother': surname_mother, \
                            'patient': ', '.join(patient)})
        else:
            message.respond(u"Il n'existe aucun patient du prénom %(first_name)s " \
                            u"et nom de mère %(surname_mother)s"
                            % {'surname_mother': surname_mother, \
                                            'first_name': first_name})
    #Si SMS ne contient que le nom de mère
    if first_name == "n" and last_name == "n":

        patient = [(u"%(first)s %(last)s de l'id %(id)s" % \
                    {"id":op.id,"first": op.first_name, \
                        "last": op.last_name}) for op in \
                        Patient.objects.filter(seat__code=code_seat, \
                        surname_mother=surname_mother)]
        if patient:
            message.respond(u" Il existe %(nber)s patient(s) du nom de mère %(surname_mother)s: %(patient)s." \
                        % {'nber': patient.__len__(), 'surname_mother': surname_mother, \
                            'patient': ', '.join(patient)})
        else:
            message.respond(u"Il n'existe aucun patient du nom de mère %(surname_mother)s" \
                        % {'surname_mother': surname_mother})
    #Si SMS ne cotient que le prénom et nom
    if first_name != "n" and last_name != "n" and surname_mother == "n":
        patient = [(u"%(mother)s de l'id %(id)s" % \
                    {"id":op.id, "mother": op.surname_mother}) for op in \
                        Patient.objects.filter(seat__code=code_seat, \
                        last_name=last_name, first_name=first_name)]
        if patient:
            message.respond(u" Il existe %(nber)s patient(s) du prénom %(first_name)s " \
                            u"et nom %(last_name)s: %(patient)s." \
                            % {'nber': patient.__len__(), \
                            'first_name': first_name, \
                            'last_name': last_name, \
                            'patient': ', '.join(patient)})
        else:
            message.respond(u"Il n'existe aucun patient du prénom %(first_name)s " \
                            u"et nom %(last_name)s"
                            % {'last_name': last_name, \
                                            'first_name': first_name})
    #Si SMS ne cotient que prénom
    if surname_mother == "n" and last_name == "n":
        patient = [(u"%(last)s %(mother)s de l'id %(id)s" % \
                    {"id":op.id,"last": op.last_name,"mother": \
                            op.surname_mother}) for op in \
                        Patient.objects.filter(seat__code=code_seat, \
                                                first_name=first_name)]
        if patient:
            message.respond(u" Il existe %(nber)s patient(s) du prénom %(first_name)s: %(patient)s." \
                        % {'nber': patient.__len__(), 'first_name': first_name, \
                            'patient': ', '.join(patient)})
        else:
            message.respond(u"Il n'existe aucun patient du prénom %(first_name)s" \
                        % {'first_name': first_name})
    #Si tout est remplis
    if first_name != "n" and surname_mother != "n" and last_name != "n":
        patient = [(u"l'id %(id)s " % {"id":op.id}) for op in \
                        Patient.objects.filter(seat__code=code_seat, \
                                               last_name=last_name, \
                                               surname_mother=surname_mother, \
                                                    first_name=first_name)]
        if patient:
            message.respond(u" Il existe %(nber)s patient(s) du prénom %(first_name)s" \
                            u", nom %(last_name)s et nom de mère "
                            u"%(last_name)s: %(patient)s." \
                            % {'nber': patient.__len__(), \
                            'first_name': first_name, \
                            'last_name': last_name, \
                            'surname_mother': surname_mother, \
                            'patient': ', '.join(patient)})
        else:
            message.respond(u"Il n'existe aucun patient du prénom %(first_name)s " \
                            u" nom %(last_name)s et nom de mère %(surname_mother)s"
                            % {'last_name': last_name, \
                                            'first_name': first_name, \
                                            'surname_mother': surname_mother})

    return True


def followed_child(message):
    """ Incomming:
            nut fol id weight heught pb danger_sign
        Outgoing:
            [SUCCES] Les données nutritionnelles de full_name ont
            ete bien enregistre.
            or error message """

    # common start of error message
    error_start = u"Impossible d'enregistrer les donnees. "
    try:
        args_names = ['kw1', 'kw2', 'id', 'weight', \
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
    except:
        # failure to convert means non-numeric value which we can't process.
        message.respond(error_start + u" Les données sont malformées.")
        return True
    # create the datanut
    try:
        datanut = DataNut()
        datanut.patient = Patient.objects.get(id=arguments.get('id'))
        datanut.date = date.today()
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
    return True

def disable_child(message):
    """  Incomming:
            nut off id
         Outgoing:
            [SUCCES] full_name ne fait plus partie du programme.
            or error message """

    # common start of error message
    error_start = u"Impossible de desactiver. "
    kw1, kw2, id_= message.text.strip().lower().split()
    try:
        patient = Patient.objects.get(id=id_)
    except:
        message.respond(u"Cet enfant n'existe pas dans le programme")
        return True

    patient.status = False
    patient.save()

    message.respond(u"[SUCCES] %(full_name)s ne fait plus partie "
                    u"du programme." %
                    {'full_name': patient.full_name()})
    return True
