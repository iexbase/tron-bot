# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

BASE_START_TEXT = ("""
Hello {user_name}!. Welcome to TronBot

/help - Assistant to work with the bot
""")


HELP_VIEW = ("""
@iEXTronBot - Telegram bot that helps you with send, find data in Blockchain TRON

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

*Supports*
- TRX: TRWBqiqoFZysoAeyR1J35ibuyc8EvhUAoY'

""")

PRICE_VIEW = ("""
*Price:* {price}
*Price BTC: * {price_btc}
*Global Rank:* {rank} 
*Market Cap:* {market_cap}
*24h Volume:* {volume_24h}
""")


ACCOUNTS_VIEW = ("""
*Address* {address}
*Balance TRX* {balance} 
---------------------
""")


BLOCK_VIEW = ("""
*Hash:* {id}
-----------------------------
*Height:* {height}
*Time:* {time}
*Transactions:* {count} txs
*Parent Hash:* {parent}
*Version*: {version}
*Witness address*: {witness}


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
*Contract Type*: {contract_type}


*Owner Address:* {owner_address}
*Contract Address:* {to_address}
*Value:* {value} {token}

""")

CREATE_ACCOUNT = ("""

*Address:* {address}
--------------
*Private key:* {privateKey}
--------------
*Public key:* {publicKey}
""")


DAPP_PREVIEW = ("""
*Name:* {name}
*Tagline:* {tagline}
*Version:* {version}
*Developer:* {developer}
*Total transaction* {total}
-------------------------
""")


DAPP_STAT = ("""
*Dapp statistics*
Stats are updated daily. Check back often to see the progress and development of the DApp ecosystem.

*Total DApps:* {total}
*Daily active users:*: {dau}
*24 hr transactions:* {transactions}
*24 hr volume (TRX):* {volume}
*Smart contracts:* {smart_contract}

*Statistics by category:*
""")


DAPP_STAT_CAT = ("""
*Category:* {category}
*Total DApps:* {dapp_count}
*Daily active users:* {mau}
*24 hr transactions:* {transactions}
*Smart contract:* {smart_contract}
---------------------------------
""")
