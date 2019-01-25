# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

from telegram import KeyboardButton, ReplyKeyboardMarkup

keyboard_p1 = [
    [
        KeyboardButton("Top Accounts"),
        KeyboardButton("Price"),
        KeyboardButton("Stats")
    ],
    [KeyboardButton("Last Transactions")],
    [KeyboardButton("Generate Address")]
]
reply_markup_p1 = ReplyKeyboardMarkup(keyboard_p1, True, False)
