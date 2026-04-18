import sys
import hashlib
import json

import web3

import setting

from test_rpc_init import *
from setting import accounts

if __name__ == '__main__':
    # Buy order: spend USDC to get BTC (base_amount negative means buying)
    # [base_token, base_amount, quote_token, quote_amount]
    # Buy: base_amount is negative (selling quote to get base)
    # Sell: quote_amount is negative (selling base to get quote)
    
    # Buy 0.1 BTC at price 50000 USDC (spend 5000 USDC)
    # base_amount = -0.1 BTC, quote_amount = 5000 USDC
    call = '{"p": "zentest3", "f": "trade_limit_order", "a": ["BTC", -100000000000000000, "USDC", 5000000000]}'
    print(call)
    tx_hash = transaction(accounts[0], call)
    print(tx_hash)

    # Sell 0.05 BTC at price 50000 USDC (get 2500 USDC)
    # base_amount = 0.05 BTC, quote_amount = -2500 USDC
    call = '{"p": "zentest3", "f": "trade_limit_order", "a": ["BTC", 50000000000000000, "USDC", -2500000000]}'
    print(call)
    tx_hash = transaction(accounts[0], call)
    print(tx_hash)