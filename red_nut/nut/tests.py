"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_sms(self):
        pass
        #~ from red_nut.nut_sms.nut import handler
        #~ handler("nut stock URENI pmib 1 2011 #l75 1212 121 121 2112 #l100 121 12 112 12 #pln 1212 121 121 112")
