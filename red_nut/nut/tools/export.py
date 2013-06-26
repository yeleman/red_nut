#!/usr/bin/env python
# encoding=utf-8
# maintainer: alou, Fadiga
#
#Contains functions dedicated to export the whole database into
#   various format such as XLS and sqlite

import StringIO

import xlwt

from django.conf import settings
from nut.models import ProgramIO, NutritionalData


al_center = xlwt.Alignment()
# al_center.horz = xlwt.Alignment.HORZ_CENTER
al_center.vert = xlwt.Alignment.VERT_CENTER

#styles
style_title = xlwt.easyxf('font: name Times New Roman, height 200, bold on,'
                          'color black')
style_title.alignment = al_center


def report_as_excel(health_centers):
    """
        Export the whole data base to XLS
    """

    def write_event(patient):
        """
            Return status
        """
        if patient.event == ProgramIO.SUPPORT:
            return 'ENTRE'

        return 'SORTIE'

    date_format = settings.EXCEL_DATE_FORMAT

    # On crée le doc xls
    book = xlwt.Workbook(encoding='utf-8')
    # On crée les feuilles
    sheet = book.add_sheet(u"Consommations")
    sheet_patient = book.add_sheet(u"Enfants")

    # J'agrandi les colonnes.
    for i in (9, 10, 13, 17, 18, 19, 20):
        sheet_patient.col(i).width = 0x0d00 * 1.5

    for i in (0, 4, 5, 6):
        sheet_patient.col(i).width = 0x0d00 * 2.5

    sheet.col(0).width = 0x0d00 * 1.3
    sheet_patient.col(1).width = 0x0d00 * 1.2

    row = row_ = 0

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
        sheet.write(0, index, title, style_title)

    # entete liste des enfants
    headers2 = (u"ID",
                 u"Opération",
                 u"Code CSCOM",
                 u"CSCOM",
                 u"Nom",
                 u"Prénom",
                 u"Mère",
                 u"DDN",
                 u"DDN en mois",
                 u"Sexe",
                 u"Date d'enregistrement",
                 u"Date de la visite",
                 u"Poids",
                 u"Taille",
                 u"Perimètre brachial",
                 u"Oedème",
                 u"PPN",
                 u"UREN",
                 u"Date de la derniere visite",
                 u"Dernier status",
                 u"Date du dernier status",
                 u"Date de l'evenement",
                 u"Evenement",
                 u"Raison",
                 u"Durée Moyenne",
                 u"Gain de poids")

    for index, title in enumerate(headers2):
        sheet_patient.write(row, index, title, style_title)

    for health_center in health_centers:

        reports = health_center.consumption_reports\
                               .select_related('input_type', 'period')
        for report in reports:
            row_ += 1
            sheet.write(row_, 0, health_center.code)
            sheet.write(row_, 1, health_center.name)
            sheet.write(row_, 2, report.input_type.code)
            sheet.write(row_, 3, report.input_type.name)
            sheet.write(row_, 4, report.initial)
            sheet.write(row_, 5, report.received)
            sheet.write(row_, 6, report.used)
            sheet.write(row_, 7, report.lost)
            sheet.write(row_, 8, report.remaining())
            sheet.write(row_, 9, report.period.middle().strftime("%m-%Y"))

        for patient in [patient for patient in health_center.patients.all() if
             patient.uren in (NutritionalData.SAMP, NutritionalData.SAM)]:
            row += 1
            col = 0
            sheet_patient.write(row, col, patient.nut_id, style_title)
            col += 1
            sheet_patient.write(row, col, "Enregistrement")
            col += 1
            sheet_patient.write(row, col, health_center.code)
            col += 1
            sheet_patient.write(row, col, health_center.name)
            col += 1
            sheet_patient.write(row, col, patient.last_name)
            col += 1
            sheet_patient.write(row, col, patient.first_name)
            col += 1
            sheet_patient.write(row, col, patient.surname_mother)
            col += 1
            sheet_patient.write(row, col, patient.birth_date
                                              .strftime(date_format))
            col += 1
            sheet_patient.write(row, col, patient.dob)
            col += 1
            sheet_patient.write(row, col, patient.sex)
            col += 1
            sheet_patient.write(row, col, patient.create_date
                                              .strftime(date_format))
            col += 2
            first_data_nut = patient.first_data_nut()
            sheet_patient.write(row, col, first_data_nut.weight)
            col += 1
            sheet_patient.write(row, col, first_data_nut.height)
            col += 1
            sheet_patient.write(row, col, first_data_nut.muac)
            col += 1
            sheet_patient.write(row, col, first_data_nut.get_oedema_display()
                                                     .upper())
            col += 1
            sheet_patient.write(row, col, first_data_nut.nb_plumpy_nut)
            col += 1

            last_data_event = patient.last_data_event()
            sheet_patient.write(row, col,
                                NutritionalData.URENS_FR
                                               .get(patient.nutritional_data
                                               .latest().diagnosis))
            col += 1
            sheet_patient.write(row, col, patient.last_visit()
                                              .strftime(date_format))
            col += 1
            sheet_patient.write(row, col, write_event(last_data_event))
            col += 1
            sheet_patient.write(row, col, last_data_event.date
                                                       .strftime(date_format))
            # la dernière ligne
            rowpp = row
            datanut_patients = patient.nutritional_data.all().order_by("date")

            for data in datanut_patients.exclude(pk=first_data_nut.pk):
                row += 1
                col = 0
                sheet_patient.write(row, col, data.patient.nut_id, style_title)
                col += 1
                sheet_patient.write(row, col, u"Suivi")
                col += 10
                sheet_patient.write(row, col, data.date.strftime(date_format))
                col += 1
                sheet_patient.write(row, col, data.weight)
                col += 1
                sheet_patient.write(row, col, data.height)
                col += 1
                sheet_patient.write(row, col, data.muac)
                col += 1
                sheet_patient.write(row, col, data.get_oedema_display().upper())
                col += 1
                sheet_patient.write(row, col, data.nb_plumpy_nut)
                col += 1
                sheet_patient.write(row, col,
                                    NutritionalData.URENS_FR
                                                   .get(data.diagnosis))

            patient_programios = patient.programios.all().order_by("date")
            for pp in patient_programios:
                col_ = 21
                if pp.event == ProgramIO.OUT:
                    rowpp = row
                    sheet_patient.write(rowpp, 0, pp.patient.nut_id, style_title)
                    sheet_patient.write(row, 1, u"Sortie")

                sheet_patient.write(rowpp, col_, pp.date.strftime(date_format))
                col_ += 1
                sheet_patient.write(rowpp, col_, write_event(pp))
                col_ += 1
                sheet_patient.write(rowpp, col_, pp.get_reason_display())
                # sheet_patient.write(rowpp, col_, pp.get_reason_display().upper())
                rowpp += 1
                row += 1

            col_ += 1
            if not patient.in_program():
                avg_days = ProgramIO.out.filter(patient=patient).avg_days()
                sheet_patient.write(rowpp - 1, col_, avg_days)

            col_ += 1
            if patient.is_healing():
                avg_weight = patient.weight_gain_out()
                sheet_patient.write(rowpp - 1, col_, float("%.1f" % avg_weight))

    stream = StringIO.StringIO()
    book.save(stream)

    return stream
