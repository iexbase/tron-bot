from datetime import datetime


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
