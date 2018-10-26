from datetime import datetime


def date_format(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%d-%m-%Y, %H:%M')


def text_simple(usr_msg_text):
    if len(usr_msg_text) == 64:
        return 'transaction'

    if str(usr_msg_text).replace(' ', '').lower() == 'topaccounts':
        return 'topaccounts'

    if str(usr_msg_text).lower() == 'price':
        return 'price'

    if str(usr_msg_text).lower() == 'stats':
        return 'stats'

    if str(usr_msg_text).replace(' ', '').lower() == 'lasttransactions':
        return 'lasttransactions'

    if str(usr_msg_text).replace(' ', '').lower() == 'generateaddress':
        return 'generateaddress'
