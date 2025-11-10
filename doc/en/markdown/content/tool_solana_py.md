# Solana/More Developer Tools/Using solana-py Together with the solders Library

The [solana-py](https://github.com/michaelhly/solana-py) tool is a Python library for Solana, used to interact with the Solana blockchain. It provides APIs to communicate with Solana nodes, making it suitable for quickly building applications that talk to the Solana network. Under the hood, it depends on the [solders](https://github.com/kevinheavey/solders) library. solders is a lower-level Solana library written in Rust that offers direct access to Solana protocols and data structures.

You can think of them as:

- solders: provides direct access to Solana protocols and data structures
- solana-py: built on top of solders, offering higher-level APIs for rapid development and network interactions

The following example shows how to use solana-py and solders to fetch all transaction history of a simple on-chain data program and print the data of all accounts owned by that program.

```py
"""
Fetch all transaction history for a Solana program and print stored data for each account owned by the program.

Network: mainnet-beta
Program: 9RctzLPHP58wrnoGCbb5FpFKbmQb6f53i5PsebQZSaQL

This script uses the JSON-RPC getSignaturesForAddress pagination to walk the full history of the program (within node's
retention), then fetches program-owned accounts and prints their data.
"""
import datetime
import itertools
import os
import solana.rpc.api
import solders
import solders.rpc.responses
import typing

DEFAULT_PROGRAM_ID = '9RctzLPHP58wrnoGCbb5FpFKbmQb6f53i5PsebQZSaQL'
DEFAULT_RPC = os.environ.get('SOLANA_RPC', 'https://api.mainnet-beta.solana.com')


def get_all_program_sigs(
    client: solana.rpc.api.Client,
    program: solders.pubkey.Pubkey,
) -> typing.Generator[solders.rpc.responses.RpcConfirmedTransactionStatusWithSignature, None, None]:
    cursor = None
    limits = 256
    for _ in itertools.repeat(0):
        resp = client.get_signatures_for_address(program, before=cursor, limit=limits)
        sigs = resp.value
        if not sigs:
            break
        for s in sigs:
            yield s
        cursor = sigs[-1].signature


def get_all_program_pdas(
    client: solana.rpc.api.Client,
    program: solders.pubkey.Pubkey,
) -> typing.List[solders.rpc.responses.RpcKeyedAccount]:
    resp = client.get_program_accounts(program, encoding='base64')
    pdas = resp.value
    return pdas


def main():
    program_key = solders.pubkey.Pubkey.from_string(DEFAULT_PROGRAM_ID)
    client = solana.rpc.api.Client(DEFAULT_RPC)
    print('main: get_all_program_sigs')
    for e in get_all_program_sigs(client, program_key):
        print(f'main: datetime={datetime.datetime.fromtimestamp(e.block_time)}, sig={e.signature}')
    print('main: get_all_program_pdas')
    for e in get_all_program_pdas(client, program_key):
        print('main:    owner:', e.account.owner)
        print('main:      pda:', e.pubkey)
        print('main: lamports:', e.account.lamports)
        print('main:     data:',  e.account.data.decode())
        print()


if __name__ == '__main__':
    main()
```

The output looks like this, successfully retrieving the author's data stored on-chain:

```txt
main: get_all_program_sigs
main: datetime=2025-10-13 14:42:45, sig=4k2rTsRW2s1GKxsaDmDx2sM9rRVTzGS7LgVnTphAPNQ4ZDpbhLeLLSrVLeRQLxBEpfWsTGFoAn3uuJDzr6eQ7y9X
main: datetime=2025-10-13 14:40:22, sig=5WduQv7NGXpnHUYWwrjhyzWtHHP6BRj2os4iuj8JpYCHGMeiT2wRzGzgm2yF5PdKcAuux7LhXkDe1B79oFj2q8fb
main: datetime=2025-10-13 14:33:51, sig=EPJQwvr3WpVHZ6Jdr4DWrx5sKVScb7yrz2YRfGHyPqTpjNL4WnmvoquA9HATsPCQrzpSsyPx5WUUQt7Ger6JLY2
main: datetime=2025-10-13 11:31:49, sig=3wXnUFazxCz5zbvMcptVXKNyjuP45zbuc5UzmpxwKzK8VaQzTsuwoMdXhJTBaowhJ5LWuVwuFghUDvG7pu7Ty7CG
main: get_all_program_pdas
main:    owner: 9RctzLPHP58wrnoGCbb5FpFKbmQb6f53i5PsebQZSaQL
main:      pda: Ep838PrgsVLKgCwab15hNkBB1EaFFBKKx6pNiE1bGD5G
main: lamports: 1120560
main:     data: 片云天共远, 永夜月同孤.
```

This example essentially uses the `get_signatures_for_address` and `get_program_accounts` RPC methods, together with the solders library to parse data, so we can print the information we've stored on-chain. With this approach, it's easy to inspect any Solana program's transaction history and account data.
