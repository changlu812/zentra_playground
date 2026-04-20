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

    # Block 1: 混合 limit 和 market orders
    print('=== Block 1: 创建 5 个 Limit + 2 个 Market Orders ===')
    for i in range(5):
        price = random.randint(65000, 68000)
        amount = random.randint(100, 500) * 10**18
        call = f'{{"p": "zen", "f": "trade_limit_order", "a": ["BTC", -{amount}, "USDC", {price * amount}]}}'
        print(f'Limit Order {i+1}: price={price}, amount={amount}')
        tx_hash = transaction(accounts[random.randint(0, 2)], call)
        print(f'  tx: {tx_hash}')

    for i in range(2):
        amount = random.randint(10, 50) * 10**18
        call = f'{{"p": "zen", "f": "trade_market_order", "a": ["BTC", -{amount}, "USDC", null]}}'
        print(f'Market Order {i+1}: amount={amount}')
        tx_hash = transaction(accounts[random.randint(0, 2)], call)
        print(f'  tx: {tx_hash}')

    print('\n=== next block ===')
    result = next_block()
    print('result:', result)

    # Block 2: 更多混合订单
    print('\n=== Block 2: 创建 3 个 Limit + 3 个 Market Orders ===')
    for i in range(3):
        price = random.randint(62000, 64000)
        amount = random.randint(100, 500) * 10**18
        call = f'{{"p": "zen", "f": "trade_limit_order", "a": ["BTC", {amount}, "USDC", -{price * amount}]}}'
        print(f'Limit Order {i+1}: price={price}, amount={amount}')
        tx_hash = transaction(accounts[random.randint(0, 2)], call)
        print(f'  tx: {tx_hash}')

    for i in range(3):
        amount = random.randint(10, 50) * 10**6
        call = f'{{"p": "zen", "f": "trade_market_order", "a": ["BTC", null, "USDC", -{amount}]}}'
        print(f'Market Order {i+1}: amount={amount}')
        tx_hash = transaction(accounts[random.randint(0, 2)], call)
        print(f'  tx: {tx_hash}')

    print('\n=== next block ===')
    result = next_block()
    print('result:', result)

    print('\n=== 完成 ===')