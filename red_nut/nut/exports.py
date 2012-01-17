#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin
# maintainer: Fad

import xlwt
import StringIO

def report_as_excel(stocks, patients, datanuts):
    """ Export les données du stock en xls """
    # On crée le doc xls
    book = xlwt.Workbook(encoding='utf-8')
    if stocks:
        # On crée une feuille nommé Stocks
        sheet = book.add_sheet(u"Stocks")
        # J'agrandi la colonne à trois fois la normale.
        sheet.col(0).width = 0x0d00 * 3

        sheet.write_merge(0, 0, 0, 12, u"Tableau des consomations d'intrants.")
        sheet.write(1, 0, u"CSCOM")
    if patients or datanuts:
        # On crée une feuille nommé patients
        sheet = book.add_sheet(u"patients")
        # J'agrandi la colonne à trois fois la normale.
        sheet.col(0).width = 0x0d00 * 3
        sheet.col(1).width = 0x0d00 * 3
        sheet.col(2).width = 0x0d00 * 3
        sheet.col(5).width = 0x0d00 * 2
        sheet.col(6).width = 0x0d00 * 2
        sheet.col(7).width = 0x0d00 * 2
        sheet.col(10).width = 0x0d00 * 2

        sheet.write_merge(0, 0, 0, 11, u"Liste des patients.")
        sheet.write(2, 0, u"CSCOM")
        sheet.write(4, 0, u"Nom")
        sheet.write(4, 1, u"Prénom")
        sheet.write(4, 2, u"Mère")
        sheet.write(4, 3, u"DDN")
        sheet.write(4, 4, u"Sexe")
        sheet.write(4, 5, u"Date d'enregistrement")
        sheet.write(4, 6, u"Dernier status")
        sheet.write(4, 7, u"Derniere visite")
        sheet.write(4, 8, u"Poids")
        sheet.write(4, 9, u"Taille")
        sheet.write(4, 10, u"Perimètre brachial")
        sheet.write(4, 11, u"Oedème")
        i = 5
        for patient in patients:
            datanut_patient = datanuts.filter(patient__id=patient.id) \
                                      .order_by('date')
            sheet.write(i, 0, patient.last_name)
            sheet.write(i, 1, patient.first_name)
            sheet.write(i, 2, patient.surname_mother)
            sheet.write(i, 3, patient.birth_date.strftime("%d %b %Y"))
            sheet.write(i, 4, patient.sex)
            sheet.write(i, 5, patient.create_date.strftime("%d %b %Y"))
            sheet.write(i, 6, patient.last_data_event().get_event_display())
            sheet.write(i, 7, patient.last_visit().strftime("%d %b %Y"))
            sheet.write(i, 8, patient.last_data_nut().weight)
            sheet.write(i, 9, patient.last_data_nut().height)
            sheet.write(i, 10, patient.last_data_nut().muac)
            sheet.write(i, 11, patient.last_data_nut().get_oedema_display())
            i += 1
            if datanut_patient:
                pass





    stream = StringIO.StringIO()
    book.save(stream)

    return stream
