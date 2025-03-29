# Solana/Transactions/Instruction

## Example Transaction

> To avoid readers constantly switching pages, I will paste the analyzed transaction at the beginning of each section.

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

## Instructions in Transactions

A Solana transaction is like an envelope, and the instructions are the contents inside it. Each instruction tells the Solana network how to process the transaction. Think of it as putting a letter into an envelope: afterward, we seal it with wax, stamp it with our personal seal, and don't forget, you still need to pay postage!

![img](../img/tx_instruction/letter.jpg)

- Just as you can put multiple letters in an envelope, a transaction can contain multiple instructions.
- The transaction's signature is like the wax seal.
- The transaction fee is akin to the postage for the letter.

Each instruction in a Solana transaction performs a specific function. In the example transaction, Ada sends a SOL transfer, and behind this transaction lies a single transfer instruction. This instruction tells Solana to move a specified amount from one account to another.

Solana transactions support various types of instructions, with the transfer instruction being one of them. Each instruction is executed by a program (essentially a smart contract). Every instruction consists of three components:

- Program: The index of the target program (corresponding to a position in account_keys).
- Account: A list of account indices involved (corresponding to positions in account_keys).
- Data: Binary data passed to the program.

In the example:

- `"program": 2`: Indicates calling `tx.message.account_keys[2]`, which is the System Program `1111111...`.
- `"account": [0, 1]`: This means that two accounts are involved, `tx.message.account_keys[0]` and `tx.message.account_keys[1]`.
- `"data": "3Bxs3zzLZLuLQEYX"`: This specifies the operation.

When we decode the data field from Base58, we get the hexadecimal representation `0200000000ca9a3b00000000`. The System Program `1111111...` parses this data: the first 4 bytes are interpreted as an internal function index, and the next 8 bytes represent the transfer amount. In this case, the internal function index is 2 (indicating a transfer), and the amount is 1,000,000,000 lamports.

```py
import pxsol

data = pxsol.base58.decode('3Bxs3zzLZLuLQEYX')
assert data.hex() == '0200000000ca9a3b00000000'

assert int.from_bytes(data[:4], 'little') == 2
assert int.from_bytes(data[4:], 'little') == 1 * pxsol.denomination.sol
```

Different instructions have varying requirements for account and data, which you'll need to pay special attention to when using instructions other than transfers. In the next section, I'll briefly introduce the Solana System Program and the internal functions it includes.
