import sys
import hashlib
import json
import random
import requests

import web3

import setting
from test_rpc_init import transaction, next_block

if __name__ == '__main__':
    accounts = setting.accounts

    # Block 1: 先创建一些挂单（不成交）
    print('=== Block 1: 创建卖单挂单 ===')
    for i in range(3):
        price = 660 + i * 10
        amount = 1 * 10**18
        quote = price * 10**6
        call = f'{{"p": "zen", "f": "trade_limit_order", "a": ["BTC", -{amount}, "USDC", {quote}]}}'
        print(f'Sell Limit {i+1}: price={price}, amount={amount // 10**18}')
        tx_hash = transaction(accounts[0], call)
        print(f'  tx: {tx_hash}')

    print('\n=== next block ===')
    next_block()

    print('\n=== Block 2: 创建买单挂单（不成交） ===')
    for i in range(3):
        price = 640 - i * 10
        amount = 1 * 10**18
        quote = price * 10**6
        call = f'{{"p": "zen", "f": "trade_limit_order", "a": ["BTC", {amount}, "USDC", -{quote}]}}'
        print(f'Buy Limit {i+1}: price={price}, amount={amount // 10**18}')
        tx_hash = transaction(accounts[1], call)
        print(f'  tx: {tx_hash}')

    print('\n=== next block ===')
    next_block()

    # Block 3: 卖单，价格低于买方最高价，会成交
    print('\n=== Block 3: 卖出（价格64500，会与买方成交）===')
    price = 645
    amount = 1 * 10**18
    quote = price * 10**6
    call = f'{{"p": "zen", "f": "trade_limit_order", "a": ["BTC", -{amount}, "USDC", {quote}]}}'
    print(f'Sell Limit: price={price}, amount={amount // 10**18}')
    tx_hash = transaction(accounts[2], call)
    print(f'  tx: {tx_hash}')

    price2 = 643
    amount2 = 1 * 10**18
    quote2 = price2 * 10**6
    call2 = f'{{"p": "zen", "f": "trade_limit_order", "a": ["BTC", -{amount2}, "USDC", {quote2}]}}'
    print(f'Sell Limit: price={price2}, amount={amount2 // 10**18}')
    tx_hash2 = transaction(accounts[0], call2)
    print(f'  tx: {tx_hash2}')

    print('\n=== next block ===')
    next_block()

    # Block 4: 买入，价格高于卖方最低价，会成交
    print('\n=== Block 4: 买入（价格66500，会与卖方成交）===')
    price = 665
    amount = 1 * 10**18
    quote = price * 10**6
    call = f'{{"p": "zen", "f": "trade_limit_order", "a": ["BTC", {amount}, "USDC", -{quote}]}}'
    print(f'Buy Limit: price={price}, amount={amount // 10**18}')
    tx_hash = transaction(accounts[1], call)
    print(f'  tx: {tx_hash}')

    print('\n=== next block ===')
    next_block()

    # Block 5: Market order卖出，会与买方成交
    print('\n=== Block 5: Market卖出（与买方成交）===')
    amount = 1 * 10**18
    call = f'{{"p": "zen", "f": "trade_market_order", "a": ["BTC", -{amount}, "USDC", null]}}'
    print(f'Market Sell: amount={amount // 10**18}')
    tx_hash = transaction(accounts[2], call)
    print(f'  tx: {tx_hash}')

    print('\n=== next block ===')
    next_block()

    # Block 6: Market order买入，会与卖方成交
    print('\n=== Block 6: Market买入（与卖方成交）===')
    amount = 1 * 10**18
    call = f'{{"p": "zen", "f": "trade_market_order", "a": ["BTC", null, "USDC", -{amount}]}}'
    print(f'Market Buy: amount={amount // 10**18}')
    tx_hash = transaction(accounts[0], call)
    print(f'  tx: {tx_hash}')

    print('\n=== next block ===')
    next_block()

    print('\n=== 完成 ===')
    print('现在 history API 应该能返回 price > 0 的成交记录')