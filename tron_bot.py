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
    Filters,
    ConversationHandler,
    RegexHandler
)
from tronapi import Tron

from tronapi_bot import config, views, helpers
from tronapi_bot.helpers import text_simple, get_contract_type
from tronapi_bot.keyboards import reply_markup_p1, reply_markup_send

# initial tron-api-python
tron = Tron(
    full_node=config.TRON_FULL_NODE,
    solidity_node=config.TRON_SOLIDITY_NODE
)

# Enabled logging
logging.basicConfig(
    level=logging.DEBUG,
    format=config.LOG_FORMATTER
)
logger = logging.getLogger()

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


def validate(bot, update, args):
    """Check TRON address"""

    address = ' '.join(args)
    bot.send_message(
        chat_id=update.message.chat_id,
        text=tron.isAddress(address)
    )


def tx(bot, update, args):
    """Get transaction details"""

    tx_id = ''.join(args)
    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=_tx_view(tx_id)
    )


def price(bot, update):
    """Get the latest TRON course from CoinMarketCap"""

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=_price_view()
    )


def accounts(bot, update):
    """Top 10 Accounts with large balances"""

    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     text=_accounts_view())


def block(bot, update, args):
    """Get information on the block"""

    text = _block_view(' '.join(args))
    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=text
    )


def send(bot, update):
    update.message.reply_text(
        "Before sending a transaction, fill in all the necessary items",
        reply_markup=reply_markup_send
    )

    return CHOOSING


def balance(bot, update, args):
    """Get a balance at"""

    data = ' '.join(args).split(' ')
    try:
        info = str("{:,}".format(tron.trx.get_balance(data[0], True)))
    except Exception as e:
        info = str(e)

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=info
    )


def last_transactions(bot, update):
    """Get last 10 transactions"""

    data = requests.get(
        config.TRONSCAN_API + '/transaction?sort=-timestamp&count=true&limit=10&start=0'
    ).json()

    keyboard = []
    for tx in data['data']:
        keyboard.append([
            InlineKeyboardButton(tx['hash'], callback_data=tx['hash'])
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text='Last 10 transactions',
        reply_markup=reply_markup
    )


def generate_address(bot, update):
    """Generate new address"""

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=_generate_address_view()
    )


def statistics(bot, update):
    """Get statistics Blockchain TRON"""

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=_statistics_view()
    )


@run_async
async def start(bot, update):
    """The first launch of the bot"""

    usr_name = update.message.from_user.first_name
    if update.message.from_user.last_name:
        usr_name += ' ' + update.message.from_user.last_name
    usr_chat_id = update.message.chat_id

    text_response = views.BASE_START_TEXT.format(
        user_name=usr_name
    )

    bot.send_message(
        usr_chat_id,
        text_response,
        parse_mode="Markdown",
        reply_markup=reply_markup_p1
    )


def help(bot, update):
    """Assistant when working with the bot"""

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=_manual(),
        reply_markup=reply_markup_p1
    )


def _manual():
    """Instructions and commands"""
    return views.HELP_VIEW


def _statistics_view():
    """TRON detailed statistics template"""

    base = requests.get(config.TRONSCAN_API + '/stats/overview?limit=1').json()
    nodes = requests.get(config.SERVER_TRON_API + '/node/nodemap?total=1').json()
    detail = base['data'][-1]

    text = views.STATS_VIEW.format(
        nodes=str(nodes['total']),
        height=str(detail['totalBlockCount']),
        total_tx=str(detail['totalTransaction']),
        total_accounts=str(detail['totalAddress']),
        new_block_height=str(detail['newBlockSeen']),
        new_accounts=str(detail['newAddressSeen']),
        new_tx=str(detail['newTransactionSeen']),
        time=helpers.date_format(detail['date'])
    )
    return text


def _generate_address_view():
    """Template for creating a new address"""

    result = tron.create_account
    text = views.CREATE_ACCOUNT.format(
        address=result.address.base58,
        privateKey=result.private_key,
        publicKey=result.public_key
    )

    return text


def _block_view(block_id):
    """Template for getting the details of the block

    Args:
        block_id (str): Block ID (example: latest, 123444, hash)

    """

    if not block_id:
        block_id = 'latest'

    try:
        result = tron.trx.get_block(block_id)

        header = result['block_header']['raw_data']
        text = views.BLOCK_VIEW.format(
            id=result['blockID'],
            height=str(header['number']),
            time=helpers.date_format(header['timestamp']),
            count=str(len(result['transactions'])),
            parent=header['parentHash'],
            version=str(header['version']),
            witness=tron.address.from_hex(header['witness_address']).decode("utf-8")
        )
        return text
    except Exception as e:
        return {
            'text': 'Sorry, block not found',
            'reply_markup': None
        }


def _accounts_view():
    """Template for getting information about TOP 10 addresses with large balances"""

    data = requests.get(
        config.API_TRONSCAN + '/account?sort=-balance&limit=10&start=0'
    ).json()['data']

    text = ""
    for account in data:
        if len(account['name']) == 0:
            account['name'] = 'NoName'

        text += views.ACCOUNTS_VIEW.format(
            name=account['name'],
            address=account['address'],
            balance=str("{:,}".format(account['balance']))
        )
    return text


def _price_view():
    """Template for get the current exchange rate and cryptocurrency volumes TRON"""

    data = requests.get(config.URL_COINMARKET_API_TRON).json()['data']
    data_usd = data['quotes']['USD']

    return views.PRICE_VIEW.format(
        price=round(data_usd['price'], 3),
        rank=data['rank'],
        market_cap=str("{:,}".format(data_usd["market_cap"])),
        volume_24h=str("{:,}".format(data_usd["volume_24h"]))
    )


def _tx_view(tx_id):
    """Template for obtaining transaction details

    Args:
        tx_id (str): Transaction ID

    """

    data = requests.get(config.API_TRONSCAN + "/transaction-info?hash=" + tx_id).json()
    text = "Sorry, the transaction could not be found."

    token = 'TRX'
    amount = 0
    contract_type = get_contract_type(data['contractType'])

    if data['contractType'] == 1:
        amount = tron.fromSun(data['contractData']['amount'])
    elif data['contractType'] == 44:
        amount = tron.fromSun(data['contractData']['quant'])
    elif data['contractType'] == 4:
        amount = tron.fromSun(data['contractData']['votes'][0]['vote_count'])
        token = 'TP'
    elif data['contractType'] == 11:
        amount = tron.fromSun(data['contractData']['frozen_balance'])
    else:
        if 'amount' in data['contractData']:
            amount = data['contractData']['amount']

    if data['contractType'] not in [4, 12, 31]:
        if 'token' in data['contractData']:
            token = data['contractData']['token']

    # Статус транзакции
    status = "UNCONFIRMED"
    if data['confirmed']:
        status = "CONFIRMED"

    text = views.TX_VIEW.format(
        hash=str(data['hash']),
        status=status,
        block=str(data['block']),
        time=helpers.date_format(data['timestamp']),
        owner_address=data['ownerAddress'],
        to_address=data['toAddress'],
        value=str("{:,}".format(amount)),
        contract_type=contract_type,
        token=token
    )

    return text


def callback_data(bot, update):
    query = update.callback_query

    if len(query.data) == 64:
        bot.edit_message_text(
            text=_tx_view(query.data),
            chat_id=query.message.chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            message_id=query.message.message_id
        )


@run_async
def filter_text_input(bot, update):
    usr_msg_text = update.effective_message.text
    usr_chat_id = update.message.chat_id

    dict_to_request = text_simple(usr_msg_text)

    # Get transaction information by ID
    if dict_to_request == 'transaction':
        return bot.send_message(
            chat_id=usr_chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_tx_view(usr_msg_text)
        )

    if dict_to_request == 'topaccounts':
        return bot.send_message(
            chat_id=usr_chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_accounts_view()
        )

    if dict_to_request == 'price':
        bot.send_message(
            chat_id=usr_chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_price_view()
        )

    if dict_to_request == 'generateaddress':
        bot.send_message(
            chat_id=usr_chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_generate_address_view()
        )

    if dict_to_request == 'stats':
        bot.send_message(
            chat_id=usr_chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_statistics_view()
        )


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text

    if text == 'To':
        update.message.reply_text('Specify the recipient\'s address in the format: ')
    elif text == 'Private key':
        update.message.reply_text('Enter private key: (A private key is required to sign a transaction.)')
    elif text == 'Amount':
        update.message.reply_text('Enter the transfer amount: ')

    return TYPING_REPLY


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def received_information(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text

    # In case the recipient’s address is entered incorrectly displays an error
    if 'To' in user_data and not tron.isAddress(user_data['To']):
        update.message.reply_text("Invalid To Address {}"
                                  .format(user_data['To']), reply_markup=reply_markup_send)
        return CHOOSING

    del user_data['choice']
    update.message.reply_text("Transaction Details {}"
                              .format(facts_to_str(user_data)), reply_markup=reply_markup_send)

    return CHOOSING


def submit_transaction(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    if 'Amount' not in user_data or 'Private key' not in user_data or 'To':
        update.message.reply_text(
            text='You did not fill out all the fields, try again. /send',
            reply_markup=None
        )
        return CHOOSING

    try:
        from_ = tron.address.from_private_key(user_data['Private key']).base58

        tron.private_key = user_data['Private key']
        tron.default_address = from_
        result = tron.trx.send(user_data['To'], float(user_data['Amount']))
        keyboard = [
            [InlineKeyboardButton("Transaction Detail", callback_data=result['transaction']['txID'])]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            text='Successful Transaction',
            reply_markup=reply_markup
        )

        user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=e
        )


def main():
    # Run the TRON bot

    # We create EventHandler and we transfer a token.
    updater = Updater(config.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # callback query
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_data))

    # commands
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('tx', tx, pass_args=True))
    dp.add_handler(CommandHandler("validate", validate, pass_args=True))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("block", block, pass_args=True))
    dp.add_handler(CommandHandler("balance", balance, pass_args=True))
    dp.add_handler(CommandHandler("accounts", accounts))
    dp.add_handler(CommandHandler("lasttransactions", last_transactions))
    dp.add_handler(CommandHandler("generateaddress", generate_address))
    dp.add_handler(CommandHandler("statistics", statistics))

    # Send Transaction
    transfer_handler = ConversationHandler(
        entry_points=[CommandHandler('send', send)],

        states={
            CHOOSING: [
                RegexHandler('^(To|Amount|Private key)$',
                             regular_choice,
                             pass_user_data=True),
            ],

            TYPING_CHOICE: [
                MessageHandler(Filters.text,
                               regular_choice,
                               pass_user_data=True),
            ],

            TYPING_REPLY: [
                MessageHandler(Filters.text,
                               received_information,
                               pass_user_data=True),
            ],
        },

        fallbacks=[
            RegexHandler('^Submit transaction$',
                         submit_transaction,
                         pass_user_data=True)
        ]
    )

    dp.add_handler(transfer_handler)

    # log all errors
    dp.add_error_handler(error)

    # Run the bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
