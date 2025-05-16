# Solana/Account Model/UTXO vs. Account-Based Models

Imagine you're dealing with two different types of banking systems: one is like a piggy bank, and the other is a traditional bank account. Both help you manage your assets, but the way they work is fundamentally different.

These two concepts have inspired two distinct design philosophies in the blockchain world: the **Unspent Transaction Output (UTXO) model** and the **Account-based model**.

## UTXO Model

The UTXO model was first introduced by Bitcoin and remains a core part of Bitcoin's architecture.

Picture a piggy bank filled with various coins of different denominations. Every time you receive money, it's added to your piggy bank as separate coins, each coin representing a specific amount you can spend. When you need to make a payment, you don't simply deduct money from a balance; instead, you pull out enough coins to cover the cost, and any leftover change goes back into the piggy bank as a new coin. In other words, each transaction splits or merges these coins.

In Bitcoin, these "coins" are UTXOs, unspent transaction outputs. Each output is a discrete unit of value that can only be spent once. When you spend one, new outputs are created. For example, if you've received 100 BTC in ten outputs of 10 BTC each, and you want to spend 45 BTC, you'd select five 10-BTC UTXOs to cover it. The remaining 5 BTC is returned to you as a new UTXO.

You can think of it like this: your piggy bank holds ten $10 bills. You need to pay $45, so you take out five $10 bills, give them to the merchant, and get $5 in change, which goes back into your piggy bank.

The characteristics of the UTXO model are similar to a coin jar:

- You can have multiple "coin jars" (addresses).
- Every transaction is like picking the right coins to pay, and returning change to yourself.
- Each coin is independent and unlinked, which offers some degree of privacy, others can't easily tell how much total money you own.
- High flexibility, since you can freely combine or split coins as needed.

## Account-Based Model

The account model is the more commonly adopted bookkeeping method in modern blockchains. It was first introduced by Ethereum and has since been widely used by other blockchain platforms to manage transactions and state changes. Unlike the coin jar metaphor, this is like having a traditional bank account. Every time you deposit or withdraw funds, the bank simply updates your account balance. You don't need to track specific coins, just the overall amount.

In this model, assets are directly stored in an account, not spread across multiple transaction outputs. When a transaction happens, the system simply updates the sender's and receiver's balances. It's like transferring money to a friend, you specify the amount, and the bank deducts it from your account and credits your friend's account.

Solana adopts this account-based model. When you send SOL to a friend, the system reduces your account balance and increases your friend's, without dealing with individual outputs.

The account model is more like a bank account:

- Transactions are straightforward, you only need to track balance changes.
- Compared to the UTXO model, it offers less privacy because balances are always visible and easy to trace.
- It's better suited for complex transaction logic, especially smart contracts, which essentially operate by managing balances between accounts.

## Reflection

From Bitcoin to Solana, both models have their strengths and weaknesses, shaped by different philosophies and use cases. From a personal perspective, the UTXO model used by Bitcoin has a certain elegance in design, though it's admittedly less user-friendly. What about you, the reader, how do you view these two approaches?
