#!/usr/bin/env python
# encoding: utf-8
# maintainer: Fad/Alou

import datetime
import logging
import locale

import reversion
from django.conf import settings

from nosms.models import Message
from nosms.utils import send_sms

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, settings.DEFAULT_LOCALE)


class MalariaDataHolder(object):

    def get(self, slug):
        return getattr(self, slug)

    def field_name(self, slug):
        return MalariaReport._meta.get_field(slug).verbose_name

    def set(self, slug, data):
        try:
            setattr(self, slug, data)
        except AttributeError:
            exec 'self.%s = None' % slug
            setattr(self, slug, data)

    def fields_for(self, cat):
        u5fields = ['u5_total_consultation_all_causes', \
                    'u5_total_suspected_malaria_cases', \
                    'u5_total_simple_malaria_cases', \
                    'u5_total_severe_malaria_cases', \
                    'u5_total_tested_malaria_cases', \
                    'u5_total_confirmed_malaria_cases', \
                    'u5_total_treated_malaria_cases', \
                    'u5_total_inpatient_all_causes', \
                    'u5_total_malaria_inpatient', \
                    'u5_total_death_all_causes', \
                    'u5_total_malaria_death', \
                    'u5_total_distributed_bednets']
        if cat == 'u5':
            return u5fields
        if cat == 'o5':
            return [f.replace('u5', 'o5') for f in u5fields][:-1]
        if cat == 'pw':
            fields = [f.replace('u5', 'pw') for f in u5fields]
            fields.remove('pw_total_simple_malaria_cases')
            fields.extend(['pw_total_anc1', 'pw_total_sp1', 'pw_total_sp2'])
            return fields
        if cat == 'so':
            return ['stockout_act_children', \
                    'stockout_act_youth', \
                    'stockout_act_adult', \
                    'stockout_artemether', \
                    'stockout_quinine', \
                    'stockout_serum', \
                    'stockout_bednet', \
                    'stockout_rdt', \
                    'stockout_sp']

    def data_for_cat(self, cat, as_dict=False):
        data = []
        for field in self.fields_for(cat):
            data.append(self.get(field))
        return data


def entity_for(provider):
        entity = None
        for access in provider.access.all():
            if entity == None or access.target.level > entity.level:
                entity = access.target
        return entity


def nosms_handler(message):
    def main_palu_handler(message):
        if message.text.lower().startswith('palu '):
            if message.text.lower().startswith('palu passwd'):
                return palu_passwd(message)
            elif message.text.lower().strip() == 'palu aide':
                return palu_help(message, True)
            elif message.text.lower().startswith('palu aide'):
                return palu_help(message)
            else:
                return palu(message)
        else:
            return False

    if main_palu_handler(message):
        message.status = Message.STATUS_PROCESSED
        message.save()
        logger.info(u"[HANDLED] msg: %s" % message)
        return True
    logger.info(u"[NOT HANDLED] msg : %s" % message)
    return False


def palu_help(message, nousername=False):

    try:
        hotline = settings.HOTLINE_NUMBER
    except:
        hotline = '65731076'

    if nousername:
        kw1, kw2 = message.text.strip().lower().split()
        username = None
    else:
        kw1, kw2, uusername = message.text.strip().lower().split()
        try:
            username = uusername.split(':')[1]
        except:
            username = None

    provider = None
    if username:
        try:
            provider = Provider.objects.get(user__username=username)
        except Provider.DoesNotExist:
            pass

    if not provider:
        try:
            provider = Provider.objects.get(phone_number=message.identity)
        except:
            provider = None

    if not provider:
        text_message = u"[DEMANDE AIDE] Non identifié: %s" % message.identity
    else:
        text_message = u"[DEMANDE AIDE] %(provider)s de %(entity)s." \
                       % {'provider': provider, 'entity': entity_for(provider)}

    m = Message(identity=hotline, text=text_message)
    m.send()
    return True


def palu_passwd(message):
    error_start = u"Impossible de changer votre mot de passe. "
    try:
        kw1, kw2, username, \
        old_password, new_password = message.text.strip().lower().split()
    except ValueError:
        message.respond(error_start + u"Le format du SMS est incorrect.")
        return True

    try:
        provider = Provider.objects.get(user__username=username)
    except Provider.DoesNotExist:
        message.respond(error_start + u"Ce nom d'utilisateur (%s) " \
                                      u"n'existe pas." % username)
        return True

    if not provider.check_password(old_password):
        message.respond(error_start + u"Votre ancien mot de passe " \
                                      u"est incorrect.")
        return True

    try:
        provider.set_password(new_password)
        provider.save()
    except:
        message.respond(error_start + u"Essayez un autre nouveau " \
                                      u"mot de passe.")
        return True

    message.respond(u"Votre mot de passe a ete change et est " \
                    u"effectif immediatement. Merci.")

    return True


def palu(message):

    # common start of error message
    error_start = u"Impossible d'enregistrer le rapport. "

    # create variables from text messages.
    try:
        args_names = ['kw1', 'username', 'password', 'month', 'year', \
        'u5_total_consultation_all_causes', \
        'u5_total_suspected_malaria_cases', \
        'u5_total_simple_malaria_cases', \
        'u5_total_severe_malaria_cases', \
        'u5_total_tested_malaria_cases', \
        'u5_total_confirmed_malaria_cases', \
        'u5_total_treated_malaria_cases', \
        'u5_total_inpatient_all_causes', \
        'u5_total_malaria_inpatient', \
        'u5_total_death_all_causes', \
        'u5_total_malaria_death', \
        'u5_total_distributed_bednets', \
        'o5_total_consultation_all_causes', \
        'o5_total_suspected_malaria_cases', \
        'o5_total_simple_malaria_cases', \
        'o5_total_severe_malaria_cases', \
        'o5_total_tested_malaria_cases', \
        'o5_total_confirmed_malaria_cases', \
        'o5_total_treated_malaria_cases', \
        'o5_total_inpatient_all_causes', \
        'o5_total_malaria_inpatient', \
        'o5_total_death_all_causes', \
        'o5_total_malaria_death', \
        'pw_total_consultation_all_causes', \
        'pw_total_suspected_malaria_cases', \
        'pw_total_severe_malaria_cases', \
        'pw_total_tested_malaria_cases', \
        'pw_total_confirmed_malaria_cases', \
        'pw_total_treated_malaria_cases', \
        'pw_total_inpatient_all_causes', \
        'pw_total_malaria_inpatient', \
        'pw_total_death_all_causes', \
        'pw_total_malaria_death', \
        'pw_total_distributed_bednets', \
        'pw_total_anc1', \
        'pw_total_sp1', \
        'pw_total_sp2', \
        'stockout_act_children', 'stockout_act_youth', 'stockout_act_adult', \
        'stockout_artemether', 'stockout_quinine', 'stockout_serum', \
        'stockout_bednet', 'stockout_rdt', 'stockout_sp']
        args_values = message.text.strip().lower().split()
        arguments = dict(zip(args_names, args_values))
    except ValueError:
        # failure to split means we proabably lack a data or more
        # we can't process it.
        message.respond(error_start + u" Le format du SMS est incorrect.")
        return True

    # convert form-data to int or bool respectively
    try:
        for key, value in arguments.items():
            if key.split('_')[0] in ('u5', 'o5', 'pw', 'month', 'year'):
                arguments[key] = int(value)
            if key.split('_')[0] == 'stockout':
                arguments[key] = MalariaReport.YES if bool(int(value)) \
                                                   else MalariaReport.NO
    except:
        raise
        # failure to convert means non-numeric value which we can't process.
        message.respond(error_start + u" Les données sont malformées.")
        return True

    # check credentials
    try:
        provider = Provider.objects.get(user__username=arguments['username'])
    except Provider.DoesNotExist:
        message.respond(error_start + u"Ce nom d'utilisateur " +
                                      u"(%s) n'existe pas." % \
                                      arguments['username'])
        return True
    if not provider.check_password(arguments['password']):
        message.respond(error_start + u"Votre mot de passe est incorrect.")
        return True

    # now we have well formed and authenticated data.
    # let's check for business-logic errors.

    # create a data holder for validator
    data_browser = MalariaDataHolder()

    # feed data holder with sms provided data
    for key, value in arguments.items():
        if key.split('_')[0] in ('u5', 'o5', 'pw', \
                                 'stockout', 'year', 'month'):
            data_browser.set(key, value)

    # feed data holder with guessable data
    try:
        hc = entity_for(provider).slug
    except:
        hc = None
    data_browser.set('hc', hc)
    today = datetime.date.today()
    data_browser.set('fillin_day', today.day)
    data_browser.set('fillin_month', today.month)
    data_browser.set('fillin_year', today.year)
    data_browser.set('author', provider.name())

    # create validator and fire
    validator = MalariaReportValidator(data_browser)
    validator.errors.reset()
    try:
        validator.validate()
    except AttributeError as e:
        message.respond(error_start + e.__str__())
        return True
    errors = validator.errors

    # return first error to user
    if errors.count() > 0:
        message.respond(error_start + errors.all()[0])
        return True

    # create the report
    try:
        period = MonthPeriod.find_create_from(year=data_browser.get('year'), \
                                              month=data_browser.get('month'))
        entity = Entity.objects.get(slug=data_browser.get('hc'), \
                                    type__slug='cscom')
        report = MalariaReport.start(period, entity, provider, \
                                     type=MalariaReport.TYPE_SOURCE)

        report.add_underfive_data(*data_browser.data_for_cat('u5'))
        report.add_overfive_data(*data_browser.data_for_cat('o5'))
        report.add_pregnantwomen_data(*data_browser.data_for_cat('pw'))
        report.add_stockout_data(*data_browser.data_for_cat('so'))
        #report.save()
        with reversion.create_revision():
            report.save()
            reversion.set_user(provider.user)

    except Exception as e:
        message.respond(error_start + u"Une erreur technique s'est " \
                        u"produite. Reessayez plus tard et " \
                        u"contactez ANTIM si le probleme persiste.")
        logger.error(u"Unable to save report to DB. Message: %s | Exp: %r" \
                     % (message.text, e))
        return True

    message.respond(u"[SUCCES] Le rapport de %(cscom)s pour %(period)s "
                    u"a ete enregistre. " \
                    u"Le No de recu est #%(receipt)s." \
                    % {'cscom': report.entity.display_full_name(), \
                       'period': report.period, \
                       'receipt': report.receipt})
    try:
        to = contact_for(report.entity.parent).phone_number
    except:
        raise
        to = None
    if not to:
        return True
    send_sms(to, u"[ALERTE] Le CSCom %(cscom)s vient d'envoyer le " \
                 u"rapport #%(receipt)s pour %(period)s." \
                 % {'cscom': report.entity.display_full_name(), \
                    'period': report.period, \
                    'receipt': report.receipt})
    return True
