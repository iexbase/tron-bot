import datetime
import logging

import requests
import telegram
from datetime import datetime

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler,
    Updater,
    MessageHandler,
    CallbackQueryHandler,
    run_async,
    Filters
)
from tronapi import Tron

from tronapi_bot import config, views, helpers
from tronapi_bot.helpers import text_simple
from tronapi_bot.keyboards import reply_markup_p1


tron = Tron(
    full_node=config.TRON_FULL_NODE,
    solidity_node=config.TRON_SOLIDITY_NODE
)

logging.basicConfig(level=logging.DEBUG, format=config.LOG_FORMATTER)
logger = logging.getLogger()


def validate(bot, update, args):
    """Check TRON address"""

    address = ' '.join(args)
    bot.send_message(chat_id=update.message.chat_id,
                     text=tron.validate_address(address))


def tx(bot, update, args):
    """Get transaction details"""

    txid = ''.join(args)
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=_tx_view(txid))


def price(bot, update):
    """Get the latest TRON course from CoinmarketCap"""

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=_price_view())


def accounts(bot, update):
    """Top 10 Accounts with large balances"""

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=_accounts_view())


def block(bot, update, args):
    """Get information on the block"""

    block_id = ' '.join(args)
    detail = _block_view(block_id)

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=detail['reply_markup'],
                     text=detail['text'])


def send(bot, update, args):
    """Send transaction"""

    # f = FROM Address
    # t = To Address
    # a = float amount
    # p = private key
    f, t, a, p = ' '.join(args).split(' ')

    try:
        tron.private_key = str(p)
        result = tron.send_transaction(str(f), str(t), float(a))
        value = 'Successful Transaction'

        keyboard = [[InlineKeyboardButton("Transaction Detail", callback_data=result['txID'])]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=update.message.chat_id,
                         text=value, reply_markup=reply_markup)

    except Exception as e:
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         text=e)


def balance(bot, update, args):
    """Get a balance at"""

    data = ' '.join(args).split(' ')
    try:
        info = str("{:,}".format(tron.get_balance(data[0], True)))
    except Exception as e:
        info = str(e)

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=info)


def last_transactions(bot, update):
    """Get total transaction count"""

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=_tx_last_transactions())


def generate_address(bot, update):
    """Generate new address"""

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=_generate_address_view())


def statistics(bot, update):
    """Get statistics Blockchain TRON"""

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=_statistics_view())


@run_async
def start(bot, update):
    """The first launch of the bot"""

    usr_name = update.message.from_user.first_name
    if update.message.from_user.last_name:
        usr_name += ' ' + update.message.from_user.last_name
    usr_chat_id = update.message.chat_id

    text_response = views.BASE_START_TEXT.format(user_name=usr_name)

    bot.send_message(usr_chat_id, text_response, parse_mode="Markdown", reply_markup=reply_markup_p1)


def help(bot, update):
    """Assistant when working with the bot"""
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=_manual(),
                     reply_markup=reply_markup_p1)


def _manual():
    """Instructions and commands"""
    return views.HELP_VIEW


def _statistics_view():
    """TRON detailed statistics template"""

    base = requests.get('https://wlcyapi.tronscan.org/api/stats/overview?limit=1').json()['data']
    nodes = requests.get('https://server.tron.network/api/v2/node/nodemap?total=1').json()
    detail = base[-1]

    text = views.STATS_VIEW.format(nodes=str(nodes['total']),
                                   height=str(detail['totalBlockCount']),
                                   total_tx=str(detail['totalTransaction']),
                                   total_accounts=str(detail['totalAddress']),
                                   new_block_height=str(detail['newBlockSeen']),
                                   new_accounts=str(detail['newAddressSeen']),
                                   new_tx=str(detail['newTransactionSeen']),
                                   time=helpers.date_format(detail['date']))
    return text


def _tx_last_transactions():
    """Template for getting a total transaction count"""

    data = requests.get(
        'https://wlcyapi.tronscan.org/api/transaction?sort=-timestamp&count=true&limit=10&start=0').json()

    text = ''
    for tx in data['data']:

        if len(tx['toAddress']) < 20:
            continue

        token = 'TRX'
        amount = 0
        if 'token' in tx['contractData']:
            token = tx['contractData']['token']

        if 'amount' in tx['contractData']:
            amount = tx['contractData']['amount']

        # Transaction status
        status = "UNCONFIRMED"
        if tx['confirmed']:
            status = "CONFIRMED"

        text += '\n*Hash:* ' + str(tx['hash'])
        text += '\n*Status*: ' + status
        text += '\n*Block:* ' + str(tx['block'])
        text += '\n*Time:* ' + datetime.fromtimestamp(tx['timestamp'] / 1000).strftime('%d-%m-%Y, %H:%M')
        text += '\n*Owner Address:* ' + str(tx['ownerAddress'])
        text += '\n*Contract Address:* ' + str(tx['toAddress'])
        if amount != 0:
            text += '\n*Value:* %s %s' % (str(tron.fromSun(amount)), token)
        text += '\n-----------------'

    text += '\n*Total:* ' + str("{:,}".format(data['total']))
    return text


def _generate_address_view():
    """Template for creating a new address"""

    result = tron.create_account
    text = views.CREATE_ACCOUNT\
        .format(address=result.address.base58,
                privateKey=result.private_key,
                publicKey=result.public_key)

    return text


def _block_view(block_id):
    """Template for getting the details of the block

    Args:
        block_id (str): Block ID (example: latest, 123444, hash)

    """
    try:
        result = tron.trx.get_block(block_id)

        header = result['block_header']['raw_data']
        text = views.BLOCK_VIEW.format(id=result['blockID'],
                                       height=str(header['number']),
                                       time=helpers.date_format(header['timestamp']),
                                       count=str(len(result['transactions'])),
                                       parent=header['parentHash'])

        keyboard = []
        index = 1
        for tx in result['transactions']:
            keyboard = keyboard + [[InlineKeyboardButton('Transaction #' + str(index), callback_data=tx['txID'])]]
            index = index + 1
        reply_markup = InlineKeyboardMarkup(keyboard)

        return {
            'text': text,
            'reply_markup': reply_markup
        }
    except Exception:
        return {
            'text': 'Sorry, block not found',
            'reply_markup': None
        }


def _accounts_view():
    """Template for getting information about TOP 10 addresses with large balances"""

    data = requests.get('https://api.tronscan.org/api/account?sort=-balance&limit=10&start=0').json()['data']
    text = ""
    for account in data:

        if len(account['name']) == 0:
            account['name'] = 'NoName'

        text += views.ACCOUNTS_VIEW.format(name=account['name'],
                                           address=account['address'],
                                           balance=str("{:,}".format(account['balance'])))
    return text


def _price_view():
    """Template for get the current exchange rate and cryptocurrency volumes TRON"""

    data = requests.get(config.URL_COINMARKET_API_TRON).json()['data']
    data_usd = data['quotes']['USD']

    return views.PRICE_VIEW.format(price=round(data_usd['price'], 3),
                                   rank=data['rank'],
                                   market_cap=str("{:,}".format(data_usd["market_cap"])),
                                   volume_24h=str("{:,}".format(data_usd["volume_24h"])))


def _tx_view(tx_id):
    """Template for obtaining transaction details

    Args:
        tx_id (str): Transaction ID

    """

    data = requests.get("https://api.tronscan.org/api/transaction/" + tx_id).json()
    text = "Sorry, the transaction could not be found."

    if 'hash' in data:

        token = 'TRX'
        if 'token' in data['contractData']:
            token = data['contractData']['token']

        # Статус транзакции
        status = "UNCONFIRMED"
        if data['confirmed']:
            status = "CONFIRMED"

        text = views.TX_VIEW.format(hash=str(data['hash']),
                                    status=status,
                                    block=str(data['block']),
                                    time=helpers.date_format(data['timestamp']),
                                    owner_address=data['ownerAddress'],
                                    to_address=data['toAddress'],
                                    value=str("{:,}".format(data['contractData']['amount'])),
                                    token=token)
    return text


def callback_data(bot, update):
    query = update.callback_query

    if len(query.data) == 64:
        bot.edit_message_text(text=_tx_view(query.data),
                              chat_id=query.message.chat_id,
                              parse_mode=telegram.ParseMode.MARKDOWN,
                              message_id=query.message.message_id)


@run_async
def filter_text_input(bot, update):
    usr_msg_text = update.effective_message.text
    usr_chat_id = update.message.chat_id

    print('----')
    print(update)

    dict_to_request = text_simple(usr_msg_text)

    # Get transaction information by ID
    if dict_to_request == 'transaction':
        return bot.send_message(chat_id=usr_chat_id,
                                parse_mode=telegram.ParseMode.MARKDOWN,
                                text=_tx_view(usr_msg_text))

    if dict_to_request == 'topaccounts':
        return bot.send_message(chat_id=usr_chat_id,
                                parse_mode=telegram.ParseMode.MARKDOWN,
                                text=_accounts_view())

    if dict_to_request == 'price':
        bot.send_message(chat_id=usr_chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         text=_price_view())

    if dict_to_request == 'lasttransactions':
        bot.send_message(chat_id=usr_chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         text=_tx_last_transactions())

    if dict_to_request == 'generateaddress':
        bot.send_message(chat_id=usr_chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         text=_generate_address_view())

    if dict_to_request == 'stats':
        bot.send_message(chat_id=usr_chat_id,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         text=_statistics_view())


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Run the TRON bot

    # We create EventHandler and we transfer a token.
    updater = Updater(config.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # callback query
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_data))

    # messages
    dp.add_handler(MessageHandler(Filters.text, filter_text_input))

    # commands
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('tx', tx, pass_args=True))
    dp.add_handler(CommandHandler("validate", validate, pass_args=True))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("send", send, pass_args=True))
    dp.add_handler(CommandHandler("block", block, pass_args=True))
    dp.add_handler(CommandHandler("balance", balance, pass_args=True))
    dp.add_handler(CommandHandler("accounts", accounts))
    dp.add_handler(CommandHandler("lasttransactions", last_transactions))
    dp.add_handler(CommandHandler("generateaddress", generate_address))
    dp.add_handler(CommandHandler("statistics", statistics))

    # log all errors
    dp.add_error_handler(error)

    # Run the bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    # for use start_webhook updates method,
    # see https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks
    # updater.start_webhook(listen='127.0.0.1', port=5006, url_path=TOKEN_BOT)
    # updater.bot.set_webhook(url='https://0.0.0.0/' + TOKEN_BOT,
    #                   certificate=open('/etc/nginx/PUBLIC.pem', 'rb'))


if __name__ == '__main__':
    main()
