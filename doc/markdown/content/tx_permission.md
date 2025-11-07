# Solana/Transactions/Account and Permission

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

## Account List

In a Solana transaction, `tx.message.account_keys` is the list of all participating accounts. Let's take a look at our example:

```json
"account_keys": [
    "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
    "8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH",
    "11111111111111111111111111111111"
]
```

In this example, the transaction involves a total of three accounts:

0. `6ASf5Ec...`: Ada, the initiator of the transfer and the one paying the transaction fee.
0. `8pM1DN3...`: Bob, the recipient of the transfer.
0. `1111111...`: The Solana System Program, used to handle basic operations like transfers.

The account list defines who is involved in this transaction. You can interpret this simple transaction as follows:

0. Ada transfers 1 SOL to Bob. This operation changes the balances of both accounts, so naturally, their accounts are involved in the transaction.
0. The transfer operation requires calling the transfer function in the Solana System Program, which involves reading the program's code. Thus, the System Program is considered indirectly involved.

The order of the account list is not arbitrary, let's dive deeper.

## Permissions

In Solana's transaction structure, accounts are not just participants; they also define permissions and roles. Whether an account **needs to sign** or **can be modified** directly impacts the transaction's execution logic. These permissions are closely tied to the `tx.message.header` field.

**Does it need to sign?**

Signing accounts are the "authorizers" of the transaction, typically responsible for paying fees or approving operations. In our example, Ada needs to sign the transaction, while Bob and the Solana System Program do not.

**Is it writable?**

Whether an account is writable determines if it can be modified during the transaction. Read-only accounts can only be accessed, not altered. In our example, Ada and Bob are writable, but the Solana System Program is read-only.

We can use two bits to represent account permissions. Bit 0 indicates whether the account is writable, and Bit 1 indicates whether it needs to sign. This way, account permissions can be represented as a number between 0 and 3. The account list must be sorted by permissions in descending order:

| Account Index |   Address    | Needs Signature | Writable | Permission(0-3) |      Role       |
| ------------- | ------------ | --------------- | -------- | --------------- | --------------- |
| 0             | `6ASf5Ec...` | Yes             | Yes      | 3               | Ada (Initiator) |
| 1             | `8pM1DN3...` | No              | Yes      | 1               | Bob (Recipient) |
| 2             | `1111111...` | No              | No       | 0               | System Program  |

The permissions of the account list are stored in a compact form within `tx.message.header`.

```json
"header": [1, 0, 1]
```

These numbers, combined with the `tx.message.account_keys` list, determine each account's permission status. The header is a list of three numbers, representing:

- Number of signable accounts: Here, it's 1, indicating 1 signature is required, consistent with the length of the `tx.signatures` list.
- Number of signable, read-only accounts: Here, it's 0.
- Number of non-signable, read-only accounts: Here, it's 1.

In programmatic terms, the logic can be described as follows:

- `tx.header[0]`: Number of accounts with permission >= 2.
- `tx.header[1]`: Number of accounts with permission == 2.
- `tx.header[2]`: Number of accounts with permission == 0.

Read-only accounts do not require state changes, enabling Solana to leverage parallel processing capabilities and significantly increase transaction throughput. Parallel execution of transactions has long been a major challenge in the blockchain industry, as transactions typically modify account states, and different execution orders can lead to varying outcomes. To ensure consistency and correctness, traditional blockchain systems generally adopt a single-core, single-threaded approach, processing transactions sequentially one by one. While this method is simple and reliable, it severely limits performance scalability, particularly under high-load conditions. By identifying read-only accounts and optimizing state management, Solana breaks through this bottleneck, achieving a more efficient transaction processing mechanism.

Many public blockchains also have attempted to address this issue to achieve higher QPS (queries per second). For example, Ethereum introduced a patch in [EIP-2930]((https://eips.ethereum.org/EIPS/eip-2930)), allowing users to explicitly specify which account data a transaction accesses, enabling nodes to process unrelated transactions in parallel. However, from the author's perspective, this patch has been largely unsuccessful. As of the writing of this book, this approach has not been widely adopted in the Ethereum ecosystem. In contrast, Solana's permission system for accounts appears to be a more advanced and elegant design.
