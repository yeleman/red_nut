#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou, Fadiga


"""
    Contains functions dedicated to export the whole database into
    various format such as XLS and sqlite
"""

import StringIO

import xlwt

from django.conf import settings


def report_as_excel(health_centers):
    """
        Export the whole data base to XLS
    """

    def write_event(patient):
        """
            Return status
        """
        if patient.event == 'e':
            return 'ENTRE'

        return 'SORTIE'

    date_format = settings.EXCEL_DATE_FORMAT

    # On crée le doc xls
    book = xlwt.Workbook(encoding='utf-8')
    # On crée les feuilles
    sheet = book.add_sheet(u"Consommations")
    sheet_patient = book.add_sheet(u"Enfants")

    # J'agrandi les colonnes.
    for i in (1, 2, 8, 9, 12, 14, 15, 16, 17, 19):
        sheet_patient.col(i).width = 0x0d00 * 2

    for i in (0, 3, 4, 5):
        sheet_patient.col(i).width = 0x0d00 * 3

    sheet.col(0).width = 0x0d00 * 1.3

    i_ = i = 0

    # entete consommation d'intrant

    headers1 = (u"Code CSCOM",
                 u"CSCOM",
                 u"Code Intrant",
                 u"Intrant",
                 u"Initial",
                 u"Reçu",
                 u"Utilsé",
                 u"Perdu",
                 u"Restant",
                 u"Période")

    for index, title in enumerate(headers1):
        sheet.write(0, index, title)

    # entete liste des enfants
    headers2 = (u"ID",
                 u"Code CSCOM",
                 u"CSCOM",
                 u"Nom",
                 u"Prénom",
                 u"Mère",
                 u"DDN",
                 u"Sexe",
                 u"Date d'enregistrement",
                 u"Date de la visite",
                 u"Poids",
                 u"Taille",
                 u"Perimètre brachial",
                 u"Oedème",
                 u"UREN",
                 u"Date de la derniere visite",
                 u"Dernier status",
                 u"Date du dernier status",
                 u"Date de l'evenement",
                 u"Evenement",
                 u"Raison")

    for index, title in enumerate(headers2):
        sheet_patient.write(i_, index, title)

    for health_center in health_centers:

        reports = health_center.consumption_reports\
                               .select_related('input_type', 'period')
        for report in reports:
            i += 1
            sheet.write(i, 0, health_center.code)
            sheet.write(i, 1, health_center.name)
            sheet.write(i, 2, report.input_type.code)
            sheet.write(i, 3, report.input_type.name)
            sheet.write(i, 4, report.initial)
            sheet.write(i, 5, report.received)
            sheet.write(i, 6, report.used)
            sheet.write(i, 7, report.lost)
            sheet.write(i, 8, report.remaining())
            sheet.write(i, 9, report.period.middle().strftime("%m-%Y"))

        for patient in health_center.patients.all():
            i_ += 1
            sheet_patient.write(i_, 0, patient.nut_id)
            sheet_patient.write(i_, 1, health_center.code)
            sheet_patient.write(i_, 2, health_center.name)
            sheet_patient.write(i_, 3, patient.last_name)
            sheet_patient.write(i_, 4, patient.first_name)
            sheet_patient.write(i_, 5, patient.surname_mother)
            sheet_patient.write(i_, 6, patient.birth_date
                                              .strftime(date_format))
            sheet_patient.write(i_, 7, patient.sex)
            sheet_patient.write(i_, 8, patient.create_date
                                              .strftime(date_format))
            sheet_patient.write(i_, 15, patient.last_visit()
                                              .strftime(date_format))

            last_data_nut = patient.last_data_nut()
            sheet_patient.write(i_, 10, last_data_nut.weight)
            sheet_patient.write(i_, 11, last_data_nut.height)
            sheet_patient.write(i_, 12, last_data_nut.muac)
            sheet_patient.write(i_, 13, last_data_nut.get_oedema_display()
                                                     .upper())

            last_data_event = patient.last_data_event()

            sheet_patient.write(i_, 14, \
                                   patient.nutritional_data.latest().diagnosis)
            sheet_patient.write(i_, 16, write_event(last_data_event))

            sheet_patient.write(i_, 17, last_data_event.date
                                                       .strftime(date_format))
            sheet_patient.write(i_, 18, last_data_event.date
                                                       .strftime(date_format))
            sheet_patient.write(i_, 19, write_event(last_data_event))
            sheet_patient.write(i_, 20, last_data_event.get_reason_display()
                                                       .upper())

            datanut_patients = patient.nutritional_data.all()

            for data in datanut_patients.exclude(pk=last_data_nut.pk):
                i_ += 1

                sheet_patient.write(i_, 0, data.patient.nut_id)
                sheet_patient.write(i_, 10, data.weight)
                sheet_patient.write(i_, 11, data.height)
                sheet_patient.write(i_, 12, data.muac)
                sheet_patient.write(i_, 13, data.get_oedema_display().upper())
                sheet_patient.write(i_, 14, data.diagnosis)
                sheet_patient.write(i_, 9, data.date.strftime(date_format))

            patient_programios = patient.programios.all()
            for pp in patient_programios.exclude(pk=last_data_event.pk):
                i_ += 1
                sheet_patient.write(i_, 0, pp.patient.nut_id)
                sheet_patient.write(i_, 19, write_event(pp))

                sheet_patient.write(i_, 20, pp.get_reason_display().upper())
                sheet_patient.write(i_, 18, pp.date.strftime(date_format))

    stream = StringIO.StringIO()
    book.save(stream)

    return stream
