# Solana/Transactions/Transaction Detail

In the previous section, Ada transferred 1 SOL to Bob. We want to view the detailed content of this transaction. To do this, we use `pxsol.rpc.get_signatures_for_address` to query Ada's past transactions for a certain period of time. The interface returns serialized data about the transactions, which can be deserialized into a `pxsol.core.Transaction` object.

```py
import base64
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

for e in pxsol.rpc.get_signatures_for_address(ada.pubkey.base58(), {'limit': 32}):
    tx_meta = pxsol.rpc.get_transaction(e['signature'], {'encoding': 'base64'})
    tx_byte = base64.b64decode(tx_meta['transaction'][0])
    tx = pxsol.core.Transaction.serialize_decode(tx_byte)
    print(tx)
```

> If there are multiple transactions, they will be output in reverse chronological order of transaction time.

We retrieved Ada's original transactions, decoded them, formatted them, and viewed their contents. The result is as follows:

```json
{
    "signatures": [
        "3NPdLTf2Xp1XUu82VVVKgQoHfiUau3wGPTKAhbNzm8Rx5ebNQfHBzCGVsagXyQxRCeEiGr1jgr4Vn32UEAx1Aov3"
    ],
    "message": {
        "header": [
            1,
            0,
            1
        ],
        "account_keys": [
            "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
            "8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH",
            "11111111111111111111111111111111"
        ],
        "recent_blockhash": "6vAwzjtGMrN3mJ8o7iGVDjMM46e2AnctqmjvLbqtESrx",
        "instructions": [
            {
                "program": 2,
                "account": [
                    0,
                    1
                ],
                "data": "3Bxs3zzLZLuLQEYX"
            }
        ]
    }
}
```

The actual transaction looks different from what we expected. You may notice that the first two account keys in `account_keys` contain Ada and Bob's addresses, but the third key is a sequence of 1s again, which means what does this represent? Where did the input of 1 SOL from Ada go?

Don't worry, I'll explain each field in the transaction in the next section.
