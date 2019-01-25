# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

import logging
from decimal import Decimal

import requests
import telegram

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

from tronapi_bot import (
    constants,
    views,
    helpers
)
from tronapi_bot.helpers import (
    text_simple,
    get_contract_type,
    currency
)
from tronapi_bot.keyboards import (
    reply_markup_p1
)

# initial tron-api-python
tron = Tron(
    full_node=constants.TRON_FULL_NODE,
    solidity_node=constants.TRON_SOLIDITY_NODE
)

# Enabled logging
logging.basicConfig(
    level=logging.DEBUG,
    format=constants.LOG_FORMATTER
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

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=_accounts_view()
    )


def block(bot, update, args):
    """Get information on the block"""

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=telegram.ParseMode.MARKDOWN,
        text=_block_view(' '.join(args))
    )


def balance(bot, update, args):
    """Get a balance at"""

    data = ' '.join(args).split(' ')
    try:
        info = currency(tron.trx.get_balance(data[0], True))
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
        constants.API_TRONSCAN + '/transaction?sort=-timestamp&count=true&limit=10&start=0'
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


def dapps(bot, update):
    keyboard = [
        [InlineKeyboardButton("TRONAccelerator Winners", callback_data='dapps_0')],
        [InlineKeyboardButton("Games", callback_data='dapps_games')],
        [InlineKeyboardButton("Exchangers", callback_data='dapps_exchangers')],
        [InlineKeyboardButton("Gambling", callback_data='dapps_gambling')],
        [InlineKeyboardButton("Collectibles", callback_data='dapps_collectibles')],
        [InlineKeyboardButton("Other", callback_data='dapps_other')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        parse_mode=telegram.ParseMode.MARKDOWN,
        text='Select a category',
        reply_markup=reply_markup
    )


@run_async
def start(bot, update):
    """The first launch of the bot"""

    usr_name = update.message.from_user.first_name
    if update.message.from_user.last_name:
        usr_name += ' ' + update.message.from_user.last_name

    text_response = views.BASE_START_TEXT.format(
        user_name=usr_name
    )

    update.message.reply_text(
        text_response,
        parse_mode="Markdown",
        reply_markup=reply_markup_p1
    )

    return CHOOSING


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

    base = requests.get(constants.API_TRONSCAN + '/stats/overview?limit=1').json()
    nodes = requests.get(constants.SERVER_TRON_API + '/node/nodemap?total=1').json()
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

    # If no block number is specified
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
    except Exception:
        return {
            'text': 'Sorry, block not found',
            'reply_markup': None
        }


def _accounts_view():
    """Template for getting information about TOP 10 addresses with large balances"""

    data = requests.get(
        constants.API_TRONSCAN + '/account/list?sort=-balance&limit=10&start=0'
    ).json()['data']

    text = ''
    for account in data:
        text += views.ACCOUNTS_VIEW.format(
            address=account['address'],
            balance=currency(tron.fromSun(account['balance']))
        )
    return text


def _price_view():
    """Template for get the current exchange rate and cryptocurrency volumes TRON"""

    data = requests.get(constants.URL_COINMARKET_API_TRON).json()['data']
    data_usd = data['quotes']['USD']
    data_btc = data['quotes']['BTC']

    return views.PRICE_VIEW.format(
        price='{:.3f}'.format(data_usd['price']),
        price_btc='{:.8f}'.format(data_btc['price']),
        rank=data['rank'],
        market_cap=currency(data_usd["market_cap"]),
        volume_24h=currency(data_usd["volume_24h"])
    )


def _tx_view(tx_id):
    """Template for obtaining transaction details

    Args:
        tx_id (str): Transaction ID

    """

    data = requests.get(constants.API_TRONSCAN + "/transaction-info?hash=" + tx_id).json()
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
        value=currency(amount),
        contract_type=contract_type,
        token=token
    )

    return text


def callback_data(bot, update):
    query = update.callback_query

    if query.data in constants.DAPPS_CAT:
        result = requests.get(helpers.dapps_category(query.data)).json()

        text = ''
        for item in result['data']['data']:

            text += views.DAPP_PREVIEW.format(
                name=helpers.format_html(item['name']),
                tagline=helpers.format_html(item['tagline']),
                version=str(item['ver']),
                developer=helpers.format_html(item['developer']),
                total=str(item['totalTransaction'])
            )

        bot.send_message(
            text=text,
            chat_id=query.message.chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN
        )

    if len(query.data) == 64:
        bot.edit_message_text(
            text=_tx_view(query.data),
            chat_id=query.message.chat_id,
            parse_mode=telegram.ParseMode.MARKDOWN,
            message_id=query.message.message_id
        )


@run_async
def filter_text_input(bot, update):
    usr_msg_text = update.message.text
    dict_to_request = text_simple(usr_msg_text)

    # Get transaction information by ID
    if dict_to_request == 'transaction':
        update.message.reply_text(
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_tx_view(usr_msg_text)
        )
    # Get last transactions
    elif dict_to_request == 'lasttransactions':
        update.message.reply_text(
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_generate_address_view()
        )
    # Get top 10 accounts
    elif dict_to_request == 'topaccounts':
        update.message.reply_text(
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_accounts_view()
        )
    # Get lasted TRON course
    elif dict_to_request == 'price':
        update.message.reply_text(
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_price_view()
        )
    # Create new account
    elif dict_to_request == 'generateaddress':
        update.message.reply_text(
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_generate_address_view()
        )
    # Create transaction
    elif dict_to_request == 'createtransaction':
        update.message.reply_text(
            "To send a transaction, call the command /send",
            parse_mode=telegram.ParseMode.MARKDOWN,
        )
    # Get stats
    elif dict_to_request == 'stats':
        update.message.reply_text(
            parse_mode=telegram.ParseMode.MARKDOWN,
            text=_statistics_view()
        )
    else:
        update.message.reply_text(
            text='You did not fill out all the fields, try again. /help',
            reply_markup=None
        )

    return CHOOSING


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Run the TRON bot

    # We create EventHandler and we transfer a token.
    updater = Updater(constants.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # callback query
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_data))

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [
                RegexHandler(
                    '^(Generate Address|Price|Stats|Top Accounts)$',
                    filter_text_input
                ),

                RegexHandler(
                    '^(Last Transactions)$',
                    last_transactions
                ),

                RegexHandler(
                    '^[0-9a-zA-Z]{64}$',
                    filter_text_input
                ),
            ]
        },

        fallbacks=[
            RegexHandler('^Help', help)
        ]
    )

    # commands
    dp.add_handler(start_handler)
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
    dp.add_handler(CommandHandler('dapps', dapps))

    # messages
    # dp.add_handler(MessageHandler(Filters.text, filter_text_input))

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
