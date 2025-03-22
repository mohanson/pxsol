import argparse
import base64
import pxsol

# Shows the last transactions for a address.

parser = argparse.ArgumentParser()
parser.add_argument('--addr', type=str, help='address')
parser.add_argument('--limit', type=int, help='limit count', default=1)
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
args = parser.parse_args()

user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))

for e in pxsol.rpc.get_signatures_for_address(user.pubkey.base58(), {'limit': args.limit}):
    tx_meta = pxsol.rpc.get_transaction(e['signature'], {'encoding': 'base64'})
    tx_byte = base64.b64decode(tx_meta['transaction'][0])
    tx = pxsol.core.Transaction.serialize_decode(tx_byte)
    print(tx)
