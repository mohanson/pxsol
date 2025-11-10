# Solana/Transactions/Manually Constructing a Transaction

Transactions, crafted from digits, are the poetry of flowing wealth.

With the hands of a craftsman, bytes are wielded with precision, transforming chaos into order, as if sculpting jade into a refined artifact, its brilliance beyond words.

In this section, we'll learn how to manually construct a Solana transfer transaction. Through this process, I hope you'll gain a deeper understanding of Solana's transaction structure.

## Our Goal

Suppose Ada wants to pay Bob 2 SOL, while Bob wants to pay Cuc 1 SOL. Please implement both Ada's and Bob's requests within a single transaction.

## Defining the Transaction Participants

This transaction involves four participants, as follows:

- `ada`: Private key is `1`.
- `bob`: Private key is `2`.
- `cuc`: Public key is `HPYVwAQmskwT1qEEeRzhoomyfyupJGASQQtCXSNG8XS2`.

In Solana, transfers are facilitated by the System Program, which has a fixed address:

- `System Program`: `11111111111111111111111111111111`.

> Top secret: The private key corresponding to Cuc's address is 0x03.

## Constructing Instructions

Solana transactions consist of one or more instructions. For this transaction, we need to construct two transfer instructions.

In Solana transactions, instructions only store indices for programs and accounts, while the specific account information (public keys and permissions) is not included in the instructions themselves. This makes building transactions somewhat restrictive. To address this, pxsol provides two helper data structures:

- `pxsol.core.AccountMeta`. Contains an account's public key and its permissions. In this example, Ada and Bob should have permissions set to "signable and writable", while Cuc should be "non-signable and writable".
- `pxsol.core.Requisition`. Encapsulates all the data for a single transaction instruction and can later be "compiled" into an index-based instruction when assembling the transaction.

Here's the construction code:

```py
import pxsol

ada = pxsol.core.PriKey.int_decode(1)
bob = pxsol.core.PriKey.int_decode(2)
cuc = pxsol.core.PubKey.base58_decode('HPYVwAQmskwT1qEEeRzhoomyfyupJGASQQtCXSNG8XS2')

# Transfer from ada to bob, 2 sol
r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(ada.pubkey(), 3))
r0.account.append(pxsol.core.AccountMeta(bob.pubkey(), 1))
r0.data = pxsol.program.System.transfer(2 * pxsol.denomination.sol)

# Transfer from bob to cuc, 1 sol
r1 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(bob.pubkey(), 3))
r1.account.append(pxsol.core.AccountMeta(cuc, 1))
r1.data = pxsol.program.System.transfer(1 * pxsol.denomination.sol)
```

## Assembling the Transaction

Using the `pxsol.core.Transaction.requisition_decode` method, compile the two requisitions defined above into instructions and assemble them into a single transaction. The first parameter specifies who pays the transaction fee, and the second is a list of `Requisition` objects. In this example, we've decided that Ada will cover the transaction fee.

```py
tx = pxsol.core.Transaction.requisition_decode(ada.pubkey(), [r0, r1])
```

## Obtaining the Recent Block Hash

Use the RPC interface to fetch Solana's latest block hash.

```py
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
```

## Signing the Transaction

Once the transaction is assembled, Ada and Bob need to sign it with their private keys. Note that the order of signatures must match the order of accounts in the `tx.message.account_keys`. In this example, Ada's signature must come before Bob's. You can determine the signing order using these two simple rules:

0. The account paying the fee is always first in the signature list.
0. Writable accounts always come before read-only accounts.
0. The accounts are sorted in the order in which they appear in the transaction.

Here is the code:

```py
tx.sign([ada, bob])
```

## Final Transaction Structure

Using `print(tx)`, the complete transaction can be printed as follows:

```json
{
    "signatures": [
        "2DNYcExSuLB1BgkB7p3gSFEuWvwgnCbcBXtENBgU9tXGQdfknvST4c3U1uQ7AEAwbEc6D1qzxMQhjdiTQytE3A24",
        "42hH4QE2r9w4yRE9CQGZq7N16Pr4712sPU6myqQNAaaAxo8A8F7HB9d46By4EVXbmRJVYMNHSgdHfXmv9XY4TFud"
    ],
    "message": {
        "header": [
            2,
            0,
            1
        ],
        "account_keys": [
            "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
            "8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH",
            "HPYVwAQmskwT1qEEeRzhoomyfyupJGASQQtCXSNG8XS2",
            "11111111111111111111111111111111"
        ],
        "recent_blockhash": "FSLe6dD3NxjJacCSW9P3LSyzpZd6H4SHSUCcCFUaTQwj",
        "instructions": [
            {
                "program": 3,
                "account": [
                    0,
                    1
                ],
                "data": "3Bxs3zzLZLuLQEYX"
            },
            {
                "program": 3,
                "account": [
                    1,
                    2
                ],
                "data": "3Bxs3zvX19cRxrhM"
            }
        ]
    }
}
```

## Submitting the Transaction

Serialize the signed transaction into bytes and submit it to the network via Solana's RPC interface `send_transaction`. The network will verify the signatures, check balances, and execute the transfers.

```py
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
assert pxsol.base58.decode(txid) == tx.signatures[0]
pxsol.rpc.wait([txid])
```

A few seconds later, Bob's and Cuc's accounts will each have an additional 1 SOL!

## Complete Code

```py
import base64
import pxsol

ada = pxsol.core.PriKey.int_decode(1)
bob = pxsol.core.PriKey.int_decode(2)
cuc = pxsol.core.PubKey.base58_decode('HPYVwAQmskwT1qEEeRzhoomyfyupJGASQQtCXSNG8XS2')

r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(ada.pubkey(), 3))
r0.account.append(pxsol.core.AccountMeta(bob.pubkey(), 1))
r0.data = pxsol.program.System.transfer(2 * pxsol.denomination.sol)

r1 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(bob.pubkey(), 3))
r1.account.append(pxsol.core.AccountMeta(cuc, 1))
r1.data = pxsol.program.System.transfer(1 * pxsol.denomination.sol)

tx = pxsol.core.Transaction.requisition_decode(ada.pubkey(), [r0, r1])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([ada, bob])
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
assert pxsol.base58.decode(txid) == tx.signatures[0]
pxsol.rpc.wait([txid])
```

> Using the two helper data structures, pxsol.core.AccountMeta and pxsol.core.Requisition, makes manually constructing Solana transactions simple and enjoyable!
