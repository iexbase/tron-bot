from telegram import KeyboardButton, ReplyKeyboardMarkup

keyboard_p1 = [
    [
        KeyboardButton("TOP Accounts"),
        KeyboardButton("Price"),
        KeyboardButton("Stats")
    ],
    [KeyboardButton("Last Transactions")],
    [KeyboardButton("Generate Address")]
]
reply_markup_p1 = ReplyKeyboardMarkup(keyboard_p1, True, False)


reply_keyboard_send = [
    ['To', 'Amount'],
    ['Private key'],
    ['Submit transaction']
]

reply_markup_send = ReplyKeyboardMarkup(
    reply_keyboard_send,
    True,
    one_time_keyboard=True
)
