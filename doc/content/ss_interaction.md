# Solana/Program Development Basics/Program Interaction

Now, our on-chain data storage program is deployed at the address `DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E`. Let's try to write some data to this program.

## Writing Data to the Program

Writing data is done through a Solana transaction. Here's how you can write data:

```py
import base64
import pxsol

pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def save(user: pxsol.wallet.Wallet, data: bytearray) -> None:
    prog_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = data
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)

if __name__ == '__main__':
    save(ada, b'The quick brown fox jumps over the lazy dog')
```

```py
# 2025/05/27 10:17:23 pxsol: transaction send signature=oCF2esfLeM7iu8MsR5wgBPatVXGt9Dq7TSzLpwWuMjooeDBeHMtSc8ukuqmPcaMrzzHcdiLg7cPbPzsHi2vdv8j
# 2025/05/27 10:17:23 pxsol: transaction wait unconfirmed=1
# 2025/05/27 10:17:23 pxsol: transaction wait unconfirmed=0
# Program DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E invoke [1]
# Program DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E consumed 2903 of 200000 compute units
# Program DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E success
```

## Reading Data

To read data, simply query the PDA data account on-chain using the RPC interface, no need to build a transaction.

```py
import base64
import pxsol

pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def load(user: pxsol.wallet.Wallet) -> bytearray:
    prog_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return base64.b64decode(info['data'][0])


if __name__ == '__main__':
    print(load(ada).decode()) # The quick brown fox jumps over the lazy dog
```

## Updating Data

To update the data on-chain, simply call `save()` again with different data. This will overwrite the existing data and automatically handle the new rent-exemption status for the updated data size. Here's the complete example:

```py
import base64
import pxsol

pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def save(user: pxsol.wallet.Wallet, data: bytearray) -> None:
    prog_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = data
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


def load(user: pxsol.wallet.Wallet) -> bytearray:
    prog_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return base64.b64decode(info['data'][0])


if __name__ == '__main__':
    save(ada, b'The quick brown fox jumps over the lazy dog')
    print(load(ada).decode()) # The quick brown fox jumps over the lazy dog
    save(ada, '片云天共远, 永夜月同孤.'.encode())
    print(load(ada).decode()) # 片云天共远, 永夜月同孤.
```
