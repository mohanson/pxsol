import argparse
import base64
import pxsol

# Apply for PXS airdrop on the mainnet.

pxsol.config.current = pxsol.config.mainnet
pxsol.config.current.log = 1

parser = argparse.ArgumentParser()
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(int(args.prikey, 0)))
pubkey_mint = pxsol.core.PubKey.base58_decode('6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH')
pubkey_mana = pxsol.core.PubKey.base58_decode('HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6')
pubkey_mana_seed = bytearray([])
pubkey_mana_auth = pubkey_mana.derive_pda(pubkey_mana_seed)
pubkey_mana_spla = pxsol.wallet.Wallet.view_only(pubkey_mana_auth).spl_account(pubkey_mint)
rq = pxsol.core.Requisition(pubkey_mana, [], bytearray())
rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
rq.account.append(pxsol.core.AccountMeta(user.spl_account(pubkey_mint), 1))
rq.account.append(pxsol.core.AccountMeta(pubkey_mana, 0))
rq.account.append(pxsol.core.AccountMeta(pubkey_mana_auth, 0))
rq.account.append(pxsol.core.AccountMeta(pubkey_mana_spla, 1))
rq.account.append(pxsol.core.AccountMeta(pubkey_mint, 0))
rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
rq.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
rq.account.append(pxsol.core.AccountMeta(pxsol.program.AssociatedTokenAccount.pubkey, 0))
rq.data = bytearray()
tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([user.prikey])
pxsol.log.debugln(f'main: request pxs airdrop')
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
pxsol.rpc.wait([txid])
tlog = pxsol.rpc.get_transaction(txid, {})
for e in tlog['meta']['logMessages']:
    pxsol.log.debugln(e)
pxsol.log.debugln(f'main: request pxs airdrop done')
