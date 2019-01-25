# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

import locale
import lxml.html
import lxml.html.clean
from datetime import datetime

from tronapi_bot.constants import DAPPS_API

locale.setlocale(locale.LC_ALL, '')


def currency(amount):
    return str(locale.currency(amount, grouping=True))


def format_html(text):
    result = lxml.html.fromstring(text)
    cleaner = lxml.html.clean.Cleaner(style=True)
    result = cleaner.clean_html(result)

    return result.text_content()


def dapps_category(categoty: str):
    if categoty == 'dapps_0':
        return DAPPS_API + '/list/bonus?category=-1&start=0&limit=10'
    elif categoty == 'dapps_games':
        return DAPPS_API + '/list?category=1&start=0&limit=10'
    elif categoty == 'dapps_exchangers':
        return DAPPS_API + '/list?category=2&start=0&limit=10'
    elif categoty == 'dapps_gambling':
        return DAPPS_API + '/list?category=5&start=0&limit=10'
    elif categoty == 'dapps_collectibles':
        return DAPPS_API + '/list?category=3&start=0&limit=10'
    elif categoty == 'dapps_other':
        return DAPPS_API + '/list?category=0&start=0&limit=10'


def date_format(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%d-%m-%Y, %H:%M')


def text_simple(usr_msg_text):
    if len(usr_msg_text) == 64:
        return 'transaction'

    return str(usr_msg_text).replace(' ', '').lower()


def get_contract_type(t: int):
    if t == 1:
        return 'Transfer'
    elif t == 2:
        return 'Transfer Asset'
    elif t == 4:
        return 'Vote'
    elif t == 6:
        return 'Create'
    elif t == 9:
        return 'Participate'
    elif t == 11:
        return 'Freeze'
    elif t == 12:
        return 'Unfreeze'
    elif t == 44:
        return 'Exchange'
    elif t == 31:
        return 'Trigger Smart Contract'
    else:
        return 'Unregistred Name'
