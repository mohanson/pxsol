# Solana/Transactions/Serialization and Deserialization

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

## Serialization and Deserialization

When Solana transactions are signed, propagated, and stored, they are serialized. Serialization is the process of converting a data structure into a byte stream for transmission over a network or storage. Deserialization is the reverse process, parsing the byte stream back into the original data structure. Solana uses an efficient binary format for serialization and deserialization, striking a balance between performance and data compactness.

Solana's serialization process is based on a custom binary encoding format designed to be efficient and unambiguous. This serialization method has no official name but is distinctive and straightforward. Broadly speaking, it relies on two fundamental rules:

- Compact Encoding: Solana uses variable-length integers (compact-u16) to represent length fields. For example, the number of accounts or signatures is dynamically encoded based on the actual value's size, rather than always occupying 2 bytes. This approach reduces unnecessary space waste.
- Sequential Storage: The various parts of a transaction are arranged in a fixed order, such as the number of signatures, followed by signature data, and then the message content. This sequential structure simplifies deserialization logic.

For instance, a simple transfer transaction might look like this when serialized into a byte stream:

1.  Number of signatures (1 byte or more, variable-length encoded).
2.  Signature data (64 bytes each, stored sequentially).
3.  Message header (3 bytes).
4.  Number of accounts (1 byte or more, variable-length encoded).
5.  Account addresses (32 bytes each, stored sequentially).
6.  Recent blockhash (32 bytes).
7.  Number of instructions (1 byte or more, variable-length encoded).
8.  Instruction content.
    1. Program index (1 byte).
    2. Number of accounts (1 byte or more, variable-length encoded).
    3. Account indices (1 byte each, stored sequentially).
    4. Data length (1 byte or more, variable-length encoded).
    5. Data content.

## Using Compact-u16 to Represent Length

The variable-length integer encoding used in Solana's serialization algorithm is called compact-u16. The core idea of this algorithm is to represent a 16-bit integer (maximum value 65535) using 1 to 3 bytes, depending on the value's size. Its encoding rules are similar to traditional VLQ (variable-length quantity) encoding, utilizing 7 bits per byte for actual data and the highest bit (8th bit) as a "continuation bit" to indicate whether additional bytes need to be read.

The specific encoding process is as follows:

- For values less than 128 (0x7f), only 1 byte is needed. The highest bit is set to 0, indicating no subsequent bytes, and the remaining 7 bits store the value.

Q: What is the encoding of the value 5 (binary 00000101)?

A:

```py
import pxsol

assert pxsol.core.compact_u16_encode(5) == bytearray([0x05])
```

- For values between 128 and 16383 (0x3fff), 2 bytes are required. The first byte's highest bit is set to 1, indicating a subsequent byte; the lower 7 bits store the lower 7 bits of the value. The second byte's highest bit is set to 0, indicating the end; its lower 7 bits store the remaining portion of the value.

Q: What is the encoding of the value 132 (binary 10000100)?

A: First byte: 0x84 (10000100, continuation bit 1, data 0000100). Second byte: 0x01 (00000001, continuation bit 0, data 0000001).

```py
import pxsol

assert pxsol.core.compact_u16_encode(132) == bytearray([0x84, 0x01])
```

- For values greater than 16383, 3 bytes are needed. The continuation bits of the first two bytes are set to 1, storing the lower 14 bits. The third byte's continuation bit is set to 0, storing the remaining portion.

Q: What is the encoding of the value 65535 (binary 11111111 11111111)?

A:

```py
import pxsol

assert pxsol.core.compact_u16_encode(65535) == bytearray([0xff, 0xff, 0x03])
```

In Solana, the data inside a transaction is usually small, and the length is usually less than 128. Using compact-u16, these values can be represented with a single byte instead of a fixed 2 bytes, reducing transmission and storage costs.

## Exercise

Q: Can you manually decode Ada's transaction from its serialized hexadecimal form? The transaction data is as follows:

```
01767ae26660c142941a5961f6dec7237cae733edfe6517c37fbb8481f46bbb53ce300e714b4784
0142c93a4e6600c50fda97560ab641db0ce19559b251d66df04010001034cb5abf6ad79fbf5abbc
cafcc269d85cd2651ed4b885b5869f241aedf0a5ba297422b9887598068e32c4448a949adb290d0
f4e35b9e01b0ee5f1a1e600fe267400000000000000000000000000000000000000000000000000
0000000000000057e9774a3cad5c33f1fb6b37a03d4f009a31098118d2ceaebf430af301ad250d0
1020200010c0200000000ca9a3b00000000
```

A:

```
01                                                               tx.signatures.length
767ae26660c142941a5961f6dec723....7560ab641db0ce19559b251d66df04 tx.signatures[0]
01                                                               tx.message.header[0]
00                                                               tx.message.header[1]
01                                                               tx.message.header[2]
03                                                               tx.message.account_keys.length
4cb5abf6ad79fbf5abbccafcc269d85cd2651ed4b885b5869f241aedf0a5ba29 tx.message.account_keys[0]
7422b9887598068e32c4448a949adb290d0f4e35b9e01b0ee5f1a1e600fe2674 tx.message.account_keys[1]
0000000000000000000000000000000000000000000000000000000000000000 tx.message.account_keys[2]
57e9774a3cad5c33f1fb6b37a03d4f009a31098118d2ceaebf430af301ad250d tx.message.recent_blockhash
01                                                               tx.message.instructions.length
02                                                               tx.message.instructions[0].program
02                                                               tx.message.instructions[0].account.length
00                                                               tx.message.instructions[0].account[0]
01                                                               tx.message.instructions[0].account[1]
0c                                                               tx.message.instructions[0].data.length
0200000000ca9a3b00000000                                         tx.message.instructions[0].data
```

## Note

- The variable-length encoding compact-u16 is only used to represent lengths. Program indices and account indices in transactions are directly represented using u8.
