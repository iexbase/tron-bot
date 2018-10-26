
BASE_START_TEXT = ("""
Hello {user_name}!. Welcome to TronBot

/help - Assistant to work with the bot
""")


HELP_VIEW = ("""
@iEXTronBot - telegram bot that helps you with send, find data in Blockchain TRON

*Commands*:
/start - Start Bot
/generateaddress - Generate new TRON address
/statistics - Substrate statistics
/lasttransactions - Last Transactions
/price - Actual course
/accounts - TOP 10 Accounts
/validate {address} - Validate address
/block {id|hash} - Get information about the block
/tx {hash} - Get information about the transaction
/balance {address} - Getting balance at
/send {from} {to} {amount} {private} - Send Transaction

*Supports*
- TRX: TRWBqiqoFZysoAeyR1J35ibuyc8EvhUAoY'

""")

PRICE_VIEW = ("""
*Price:* {price}
*Global Rank:* {rank} 
*Market Cap:* {market_cap}
*24h Volume:* {volume_24h}
""")


ACCOUNTS_VIEW = ("""
*Name:* {name}
*Address* {address}
*Balance TRX* {balance}
---------------------
""")


BLOCK_VIEW = ("""
*Hash:* {id}
*Height:* {height}
*Time:* {time}
*Transactions:* {count}
*Parent Hash:* {parent}

""")

STATS_VIEW = ("""
*Online Nodes:* {nodes}
*Block Height:* {height}
*Total Transactions:* {total_tx}
*Total Accounts:* {total_accounts}

*New Blocks height:* {new_block_height}
*New Accounts:* {new_accounts}
*New Transactions:* {new_tx}
------------
*Current time:* {time}

""")

TX_VIEW = ("""
*Hash:* {hash}
*Status:* {status}
*Block:* {block}
*Time:* {time}


*Owner Address:* {owner_address}
*Contract Address:* {to_address}
*Value:* {value} {token}

""")
