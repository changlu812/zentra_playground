import sys
import hashlib
import json

import web3

import setting

from test_rpc_init import *
from setting import accounts

if __name__ == '__main__':
    to = accounts[1].address.lower()
    call = '{"p": "zen", "f": "token_transfer", "a": ["USDC", "%s", 500000000]}' % to
    print(call)
    tx_hash = transaction(accounts[0], call)
    print(tx_hash)

    call = '{"p": "zen", "f": "token_transfer", "a": ["BTC", "%s", 50000000000000000000]}' % to
    print(call)
    tx_hash = transaction(accounts[0], call)
    print(tx_hash)
