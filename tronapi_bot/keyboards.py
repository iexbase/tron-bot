from telegram import KeyboardButton, ReplyKeyboardMarkup

keyboard_p1 = [[KeyboardButton("TOP Accounts"), KeyboardButton("Price"), KeyboardButton("Stats")],
               [KeyboardButton("Last Transactions")], [KeyboardButton("Generate Address")]]
reply_markup_p1 = ReplyKeyboardMarkup(keyboard_p1, True, False)
