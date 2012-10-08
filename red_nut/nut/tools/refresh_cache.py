#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import json

from twill import commands as tw, get_browser
from twill.errors import TwillAssertionError

LOGIN_URL = 'http://crf.yeleman.com:8080/' 
DATA_URL = ['http://crf.yeleman.com:8080/dashboard/reset',
            'http://crf.yeleman.com:8080/dashboard']
AUTH_PATH = 'auth.json'

def get_credentials():
    with open(AUTH_PATH) as f:
        content = f.read()
        jsdata = json.loads(content)
        return jsdata.get('login'), jsdata.get('password')

def main():

    login, password = get_credentials()

    # log-in to Django site
    if login and password:
        tw.go(LOGIN_URL)
        tw.formvalue('1', 'username', login)
        tw.formvalue('1', 'password', password)
        tw.submit()

    if isinstance(DATA_URL, basestring):
        urls = [DATA_URL]
    else:
        urls = list(DATA_URL)

    # retrieve URIs
    for url in urls:
        try:
            tw.go(url)
            tw.code('200')
            tw.show()
        except TwillAssertionError:
            code = get_browser().get_code()           
            print (u"Unable to access %(url)s. "
                   u"Received HTTP #%(code)s."
                   % {'url': url, 'code': code})
    tw.reset_browser()


if __name__ == '__main__':
    main()