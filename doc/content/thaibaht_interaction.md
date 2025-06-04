# Solana/Thai Baht Coin/Program Interaction

## Compile and Deploy the Program

In previous articles, we have already demonstrated how to compile and deploy a program. Here, we will **again** provide the relevant steps and code.

Use the following command to compile the program code:

```sh
$ cargo build-sbf -- -Znext-lockfile-bump
```

Use the following Python code to deploy the target program to the blockchain:

```py
import pathlib
import pxsol

# Enable log
pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

program_data = pathlib.Path('target/deploy/pxsol_thaibaht.so').read_bytes()
program_pubkey = ada.program_deploy(bytearray(program_data))
print(program_pubkey) # 9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q
```

The deployment address of the Thai Baht Coin is `9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q`.

## Mint Tokens

The process of minting new Thai Baht Coins is completed via a Solana transaction. Ada can mint 100 new Thai Baht Coins for themselves with the following code. Pay attention to how the `data` is constructed: its length is 9 bytes, with the first byte being 0, representing a minting operation.

Also note, only Ada has the authority to mint new tokens, and this privilege is hardcoded into the Thai Baht Coin's on-chain program.

```py
import base64
import pxsol


def mint(user: pxsol.wallet.Wallet, amount: int) -> None:
    assert user.pubkey.base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt' # Is ada?
    prog_pubkey = pxsol.core.PubKey.base58_decode('9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = bytearray([0x00]) + bytearray(amount.to_bytes(8))
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


if __name__ == '__main__':
    ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    mint(ada, 100)
```

## Check Balance

Use the RPC interface to query the data in your data account and convert it to a 64-bit unsigned integer, which represents the user's Thai Baht Coin balance.

```py
import base64
import pxsol

def balance(user: pxsol.core.PubKey) -> int:
    prog_pubkey = pxsol.core.PubKey.base58_decode('9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q')
    data_pubkey = prog_pubkey.derive_pda(user.p)
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return int.from_bytes(base64.b64decode(info['data'][0]))

if __name__ == '__main__':
    ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    print(balance(ada.pubkey))
```

## Transfer

Ada transfers 50 Thai Baht Coins to Bob. After the transfer, both parties' balances are queried.

```py
import base64
import pxsol


def balance(user: pxsol.core.PubKey) -> int:
    prog_pubkey = pxsol.core.PubKey.base58_decode('9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q')
    data_pubkey = prog_pubkey.derive_pda(user.p)
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return int.from_bytes(base64.b64decode(info['data'][0]))


def transfer(user: pxsol.wallet.Wallet, into: pxsol.core.PubKey, amount: int) -> None:
    prog_pubkey = pxsol.core.PubKey.base58_decode('9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q')
    upda_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    into_pubkey = into
    ipda_pubkey = prog_pubkey.derive_pda(into_pubkey.p)
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(upda_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(into_pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(ipda_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = bytearray([0x01]) + bytearray(amount.to_bytes(8))
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


if __name__ == '__main__':
    ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    bob = pxsol.core.PriKey.int_decode(2).pubkey()
    transfer(ada, bob, 50)
    print(balance(ada.pubkey))
    print(balance(bob))
```
