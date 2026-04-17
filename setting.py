import hashlib

import eth_account

accounts = []
for i in range(10):
    private_key = hashlib.sha256(('brownie%s' % i).encode('utf8')).digest()
    account = eth_account.Account.from_key(private_key)
    accounts.append(account)
    # print(f'{account.address} < 0x{private_key.hex()}')


CHAIN_ID = 31337
