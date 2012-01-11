#!/usr/bin/env python
# encoding: utf-8
# maintainer: Fadiga/Alou

import logging
import locale
from datetime import date, datetime
import reversion
from django.conf import settings

from nosmsd.utils import send_sms

from red_nut.nut.models import *
from red_nut.nut.models.Period import MonthPeriod

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, settings.DEFAULT_LOCALE)


def handler(message):
    def main_nut_handler(message):
        if message.content.lower().startswith('nut '):
            if message.content.lower().startswith('nut stock'):
                return nut_stock(message)
            elif message.content.lower().startswith('nut fol'):
                return followed_child(message)
            elif message.content.lower().startswith('nut register'):
                return nut_register(message)
            elif message.content.lower().startswith('nut research'):
                return id_information_research(message)
            elif message.content.lower().startswith('nut off'):
                return disable_child(message)
        else:
            return False

    if main_nut_handler(message):
        message.status = message.STATUS_PROCESSED
        message.save()
        logger.info(u"[HANDLED] msg: %s" % message)
        return True
    logger.info(u"[NOT HANDLED] msg : %s" % message)
    return False


def nut_stock(message):
    """ Incomming:
            nut stock type_seat code_seat month year #intrant stock_initial
            stock_received stock_used stock_lost #intrant stock_initial
            stock_received stock_used stock_lost
        Outgoing:
            [SUCCES] Le rapport de stock de seat a ete bien enregistre.
            or error message """

    def format_dict(values):
        """ forme un dictionnaire avec une liste de valeur """
        # create variables from text messages.
        args_names = ['intrant',
                   'stock_initial',
                   'stock_received',
                   'stock_used',
                   'stock_lost']
        args_values = values.split()
        dict_ = dict(zip(args_names, args_values))
        return dict_

    part = message.content.strip().lower().split("#")
    list_dict = []

    # common start of error message
    error_start = u"Impossible d'enregistrer le rapport. "
    if len(part) == 7:
        debut, p1, p2, p3, p4, p5, p6 = message.content.strip() \
                                               .lower().split("#")
        try:
            args_debut = ['kw1', 'kw2', "type", "code", 'month', 'year']
            args_values = debut.split()
            dict_debut = dict(zip(args_debut, args_values))
            dict_p1 = format_dict(p1)
            list_dict.append(dict_p1)
            dict_p2 = format_dict(p2)
            list_dict.append(dict_p2)
            dict_p3 = format_dict(p3)
            list_dict.append(dict_p3)
            dict_p4 = format_dict(p4)
            list_dict.append(dict_p4)
            dict_p5 = format_dict(p5)
            list_dict.append(dict_p5)
            dict_p6 = format_dict(p6)
            list_dict.append(dict_p6)
        except ValueError:
            # failure to split means we proabably lack a data or more
            # we can't process it.
            message.respond(error_start + u" Le format du SMS est incorrect.")
            return True

    if len(part) == 8:
        debut, p1, p2, p3, p4, p5, p6, p7 = message.content.strip()\
                                            .lower().split("#")
        try:
            args_debut = ['kw1', 'kw2', "type", "code", 'month', 'year']
            args_values = debut.split()
            dict_debut = dict(zip(args_debut, args_values))
            dict_p1 = format_dict(p1)
            list_dict.append(dict_p1)
            dict_p2 = format_dict(p2)
            list_dict.append(dict_p2)
            dict_p3 = format_dict(p3)
            list_dict.append(dict_p3)
            dict_p4 = format_dict(p4)
            list_dict.append(dict_p4)
            dict_p5 = format_dict(p5)
            list_dict.append(dict_p5)
            dict_p6 = format_dict(p6)
            list_dict.append(dict_p6)
            dict_p7 = format_dict(p7)
            list_dict.append(dict_p7)
        except ValueError:
            # failure to split means we proabably lack a data or more
            # we can't process it.
            message.respond(error_start + u" Le format du SMS est incorrect.")
            return True

    if len(part) == 2:
        debut, p1 = message.content.strip().lower().split("#")
        try:
            args_debut = ['kw1', 'kw2', "type", "code", 'month', 'year']
            args_values = debut.split()
            dict_debut = dict(zip(args_debut, args_values))
            dict_p1 = format_dict(p1)
            list_dict.append(dict_p1)
        except ValueError:
            # failure to split means we proabably lack a data or more
            # we can't process it.
            message.respond(error_start + u" Le format du SMS est incorrect.")
            return True

    if len(part) == 4:
        debut, p1, p2, p3 = message.content.strip().lower().split("#")
        try:
            args_debut = ['kw1', 'kw2', "type", "code", 'month', 'year']
            args_values = debut.split()
            dict_debut = dict(zip(args_debut, args_values))
            dict_p1 = format_dict(p1)
            list_dict.append(dict_p1)
            dict_p2 = format_dict(p2)
            list_dict.append(dict_p2)
            dict_p3 = format_dict(p3)
            list_dict.append(dict_p3)
        except ValueError:
            # failure to split means we proabably lack a data or more
            # we can't process it.
            message.respond(error_start + u" Le format du SMS est incorrect.")
            return True

    try:
        for di in list_dict:

            for key, value in di.items():
                if key in ('stock_initial', 'stock_received', \
                           'stock_used', 'stock_used', 'month', 'year'):
                    di[key] = int(value)
        for key, value in dict_debut.items():
            if key in ('month', 'year'):
                    dict_debut[key] = int(value)
    except:
        # failure to convert means non-numeric value which we can't process.
        message.respond(error_start + u" Les données sont malformées.")
        return True

    # save report stock
    try:
        for di in list_dict:
            stock = Stock()
            stock.period = MonthPeriod. \
                           find_create_from(year=dict_debut.get('year'), \
                           month=dict_debut.get('month'))
            stock.seat = Seat.objects.get(code=dict_debut.get('code'))

            stock.intrant = Input.objects.get(code=di.get('intrant'))
            stock.stock_initial = di.get('stock_initial')
            stock.stock_received = di.get('stock_received')
            stock.stock_used = di.get('stock_used')
            stock.stock_lost = di.get('stock_lost')
            stock.save()
    except Seat.DoesNotExist:
        message.respond(u"[ERREUR] Ce centre de santé n'est" \
                                      u" pas dans le programme.")
        return True
    except Exception as e:
        message.respond(error_start + u"Une erreur technique s'est " \
                        u"produite. Reessayez plus tard et " \
                        u"contactez Croix-Rouge si le probleme persiste.")
        logger.error(u"Unable to save report to DB. Message: %s | Exp: %r" \
                     % (message.content, e))
        return True

    message.respond(u"[SUCCES] Le rapport de stock de %(seat)s "
                    u"a ete bien enregistre. " %
                    {'seat': stock.seat.name})
    return True


def nut_register(message):
    """ Incomming:
            nut register code_seat first_name last_name surname_mother DDN_Age
        Outgoing:
            [SUCCES] Le rapport de Asacotoqua a été enregistre. Son id est 8.
            or  xxx n'est pas enregistrer"""

    nut, register, code_seat, first_name, last_name, surname_mother, \
                        DDN_Age = message.content.strip().lower().split()
    try:
        # On essai prendre le seat
        seat = Seat.objects.get(code=code_seat)
    except:
        # On envoi un sms pour signaler que le code n'est pas valid
        message.respond(u"[ERREUR] %(seat)s n'est pas un code centre "
                        u"valide." % {'seat': code_seat})
        seat = None
        return True
    if seat != None:
        patient = Patient()
        patient.first_name = first_name
        patient.last_name = last_name
        patient.surname_mother = surname_mother
        patient.DDN_Age = DDN_Age
        patient.create_date = date.today()
        patient.seat = seat
        patient.save()

        input_ =  InputOutputProgram()
        input_.patient_id = patient.id
        input_.event = "e"
        input_.date = datetime.today()
        input_.save()

        message.respond(u"[SUCCES] %(full_name)s a été bien enregistré." \
                        u" son id est %(id)s." \
                        % {'full_name': patient.full_name(), \
                           'id': patient.id})
    return True


def id_information_research(message):
    """ Incomming:
            nut research seat first_name(op) last_name(op) surname_mother(op)
            None = n
        Outgoing:
            Il existe 2 patient(s) du prénom first_name: last_name
            surname_mother de l'id 7, last_name surname_mother de l'id 8.
            or  Il n'existe aucun patient du prénom first_name """

    nut, research, code_seat, first_name, last_name, \
                    surname_mother = message.content.strip().lower().split()

    #Si SMS ne contient que le nom
    if first_name == "n" and surname_mother == "n":
        patient = [(u"%(first)s %(mother)s de l'id %(id)s" % \
                            {"id": op.id, "first": op.first_name, \
                             "mother": op.surname_mother}) for op in \
                             Patient.objects.filter(seat__code=code_seat, \
                             last_name=last_name)]
        if patient:
            message.respond(u"[SUCCES] Il existe %(nber)s patient(s) du nom "
                            u"%(last_name)s: %(patient)s." \
                                % {'nber': patient.__len__(), \
                                   'last_name': last_name, \
                                   'patient': ', '.join(patient)})
            return True
        else:
            message.respond(u"[ERREUR] Il n'existe aucun patient du nom " \
                            u"%(last_name)s" \
                                                % {'last_name': last_name})
            return True
    #Si SMS ne contient que le prénom et nom de sa mère
    if first_name != "n" and surname_mother != "n" and last_name == "n":
        patient = [(u"%(last)s de l'id %(id)s" % \
                    {"id":op.id, "last": op.last_name}) for op in \
                        Patient.objects.filter(seat__code=code_seat, \
                                               surname_mother=surname_mother, \
                                               first_name=first_name)]
        if patient:
            message.respond(u"[SUCCES] Il existe %(nber)s patient(s) du " \
                            u"prénom %(first_name)s et du nom de mère " \
                            u"%(surname_mother)s: %(patient)s." % \
                                            {'nber': patient.__len__(), \
                                            'first_name': first_name, \
                                            'surname_mother': surname_mother, \
                                            'patient': ', '.join(patient)})
            return True
        else:
            message.respond(u"[ERREUR] Il n'existe aucun patient du prénom "
                            u"%(first_name)s et du nom de mère "
                            u"%(surname_mother)s" % {'surname_mother': \
                                    surname_mother, 'first_name': first_name})
            return True

    #Si SMS ne contient que le nom de sa mère
    if first_name == "n" and last_name == "n":

        patient = [(u"%(first)s %(last)s de l'id %(id)s" % \
                                    {"id":op.id, "first": op.first_name, \
                                                 "last": op.last_name}) \
                    for op in Patient.objects.filter(seat__code=code_seat, \
                                            surname_mother=surname_mother)]
        if patient:
            message.respond(u"[SUCCES] Il existe %(nber)s patient(s) du nom " \
                            u"de mère %(surname_mother)s: %(patient)s." \
                                % {'nber': patient.__len__(), \
                                   'surname_mother': surname_mother, \
                                   'patient': ', '.join(patient)})
            return True
        else:
            message.respond(u"[ERREUR] Il n'existe aucun patient du nom de " \
                            u"sa mère %(surname_mother)s" % {'surname_mother': \
                                                        surname_mother})
            return True

    #Si SMS ne cotient que le prénom et nom
    if first_name != "n" and last_name != "n" and surname_mother == "n":
        patient = [(u"%(mother)s de l'id %(id)s" % \
                        {"id":op.id, "mother": op.surname_mother}) \
                        for op in Patient.objects \
                                            .filter(seat__code=code_seat, \
                                                     last_name=last_name, \
                                                     first_name=first_name)]
        if patient:
            message.respond(u"[SUCCES] Il existe %(nber)s patient(s) du " \
                            u"prénom %(first_name)s et nom %(last_name)s: "
                            u"%(patient)s." % {'nber': patient.__len__(), \
                                               'first_name': first_name, \
                                               'last_name': last_name, \
                                               'patient': ', '.join(patient)})
            return True
        else:
            message.respond(u"[ERREUR] Il n'existe aucun patient du prénom "
                            u"%(first_name)s et nom %(last_name)s"
                                            % {'last_name': last_name, \
                                               'first_name': first_name})
            return True

    #Si SMS ne cotient que prénom
    if surname_mother == "n" and last_name == "n":
        patient = [(u"%(last)s %(mother)s de l'id %(id)s" % \
                    {"id": op.id, "last": op.last_name, \
                                        "mother": op.surname_mother}) \
                                            for op in Patient.objects \
                                            .filter(seat__code=code_seat, \
                                                    first_name=first_name)]
        if patient:
            message.respond(u"[SUCCES] Il existe %(nber)s patient(s) du " \
                            u"prénom %(first_name)s: %(patient)s." \
                                            % {'nber': patient.__len__(), \
                                               'first_name': first_name, \
                                               'patient': ', '.join(patient)})
            return True
        else:
            message.respond(u"[ERREUR] Il n'existe aucun patient du prénom "
                            u"%(first_name)s" % {'first_name': first_name})
            return True

    #Si SMS ne cotient que nom et le nom de la mère
    if surname_mother != "n" and last_name != "n" and first_name == "n":
        patient = [(u"%(first_name)s de l'id %(id)s" % \
                        {"id":op.id, "first_name": op.first_name}) \
                        for op in Patient.objects \
                        .filter(seat__code=code_seat, last_name=last_name, \
                                            surname_mother=surname_mother)]
        if patient:
            message.respond(u"[SUCCES] Il existe %(nber)s patient(s) du nom " \
                            u"%(last_name)s et nom de sa mère " \
                            u"%(surname_mother)s: %(patient)s." \
                                % {'nber': patient.__len__(), \
                                   'surname_mother': surname_mother, \
                                   'last_name': last_name, \
                                   'patient': ', '.join(patient)})
            return True
        else:
            message.respond(u"[ERREUR] Il n'existe aucun patient du nom" \
                            u"%(last_name)s et nom de sa mère " \
                            u"%(surname_mother)s"
                                        % {'last_name': last_name, \
                                           'surname_mother': surname_mother})
            return True

    #Si tout est remplis
    if first_name != "n" and surname_mother != "n" and last_name != "n":
        patient = [(u"l'id %(id)s " % {"id":op.id}) for op in \
                        Patient.objects.filter(seat__code=code_seat, \
                                               last_name=last_name, \
                                               surname_mother=surname_mother, \
                                                    first_name=first_name)]
        if patient:
            message.respond(u"[SUCCES] Il existe %(nber)s patient(s) du " \
                            u"prénom %(first_name)s, nom %(last_name)s et " \
                            u"nom de sa mère %(last_name)s: %(patient)s." \
                                            % {'nber': patient.__len__(), \
                                            'first_name': first_name, \
                                            'last_name': last_name, \
                                            'surname_mother': surname_mother, \
                                            'patient': ', '.join(patient)})
            return True
        else:
            message.respond(u"[ERREUR] Il n'existe aucun patient du prénom "
                            u"%(first_name)s nom %(last_name)s et nom de"
                            u" sa mère %(surname_mother)s" % {'last_name': \
                                        last_name, 'first_name': first_name, \
                                        'surname_mother': surname_mother})
            return True
    return True


def followed_child(message):
    """ Incomming:
            nut fol id weight height oedema muac danger_sign
        Outgoing:
            [SUCCES] Les données nutritionnelles de full_name ont
            ete bien enregistre.
            or error message """

    # common start of error message
    error_start = u"Impossible d'enregistrer les donnees. "
    try:
        args_names = ['kw1', 'kw2', 'id', 'weight', \
        'height', 'oedema', 'muac', 'danger_sign']
        args_values = message.content.strip().lower().split()
        arguments = dict(zip(args_names, args_values))
    except ValueError:
        # failure to split means we proabably lack a data or more
        # we can't process it.
        message.respond(error_start + u" Le format du SMS est incorrect.")
        return True

    try:
        for key, value in arguments.items():
            if key.split('_')[0] in ('id', 'weight', 'height', 'muac'):
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
        datanut.height = arguments.get('height')
        datanut.oedema = arguments.get('oedema').upper()
        datanut.muac = arguments.get('muac')
        datanut.danger_sign = arguments.get('danger_sign')
        if arguments.get('danger_sign')  == None:
            datanut.danger_sign = ""

        datanut.save()
    except Patient.DoesNotExist:
        message.respond(u"[ERREUR] Ce patient n'existe pas" \
                                      u" dans le programme.")
        return True
    except Exception as e:
        message.respond(error_start + u"Une erreur technique s'est " \
                        u"produite. Reessayez plus tard et " \
                        u"contactez Croix-Rouge si le probleme persiste.")
        logger.error(u"Unable to save report to DB. Message: %s | Exp: %r" \
                     % (message.content, e))
        return True

    message.respond(u"[SUCCES] Les données nutritionnelles de %(full_name)s "
                    u"ont ete bien enregistre. " %
                    {'full_name': datanut.patient.full_name()})
    return True


def disable_child(message):
    """  Incomming:
            nut off id reason
         Outgoing:
            [SUCCES] full_name ne fait plus partie du programme.
            or error message """

    kw1, kw2, id_, reason = message.content.strip().lower().split()
    try:
        patient = Patient.objects.get(id=id_)
        input_ = InputOutputProgram()
        input_.reason = reason
        input_.event = "s"
        input_.patient_id = id_
        input_.save()
    except:
        message.respond(u"[ERREUR] Cet enfant n'existe" \
                                      u" pas dans le programme.")
        return True

    message.respond(u"[SUCCES] %(full_name)s ne fait plus partie "
                    u"du programme." %
                    {'full_name': patient.full_name()})
    return True
