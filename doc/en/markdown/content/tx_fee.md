# Solana/Transactions/Transaction Fee

If there's one major pain point for users in the blockchain world, transaction fees undoubtedly rank high on the list. Ethereum's high gas fees and Bitcoin's costly network congestion fees have deterred many users. So, how do transaction fees work on Solana, a blockchain platform that has garnered significant attention in recent years?

## Basic Components of Transaction Fees

Solana's transaction fees consist of two main parts:

- Base Fee: This is the minimum fee every transaction must pay to compensate network validators for processing costs.
- Priority Fee (Optional): Users can opt to pay an additional fee to increase the transaction's priority, ensuring faster inclusion and confirmation during network congestion.

Unlike Ethereum and similar blockchains, Solana's fee structure doesn't rely on a complex gas mechanism. Instead, it employs a simpler, more predictable pricing model. The base fee is fixed and extremely low, typically priced in Solana's native token, SOL.

Transaction fees are implicitly designated and, by default, paid by the first signing account in the transaction. The total base fee for a transaction is calculated as the base fee multiplied by the number of signatures.

## Actual cost

As of the writing of this article on March 28, 2025, Solana's base transaction fee is typically around 0.000005 SOL. Assuming a market price of 1 SOL = $137, the cost of a single transaction is approximately $0.0007. Even during peak network times, when users opt to pay a priority fee, the total cost rarely exceeds a few cents. In contrast, Ethereum's gas fees can soar to several dollars or even tens of dollars during busy periods, while Bitcoin's transfer fees often fluctuate between $1 and $5. Solana's cost advantage is clear.

Solana's ability to maintain such low fees stems from its unique technical architecture and design philosophy. One of its core innovations is the "Proof of History" mechanism, combined with the Tower Byzantine Fault Tolerance consensus algorithm, enabling the network to process tens of thousands of transactions per second. By comparison, Ethereum's current mainnet throughput is only 15-30 TPS. Higher throughput significantly dilutes the per-unit cost.

> This optimization comes at a trade-off: fundamentally, Solana sacrifices some decentralization to achieve higher transaction processing performance.

## Fee Distribution and Burning Mechanism

A portion of Solana's transaction fees is "burned", meaning it is permanently destroyed to reduce the total supply of SOL, potentially positively impacting the token's value over the long term. Specifically:

- 50% of the fees are burned, removed from circulation entirely.
- 50% of the fees are distributed to validators as a reward for maintaining network security.

## Adding Priority Fees

When a transaction is executed, it consumes computational resources measured in compute units. A transaction can use up to 1,400,000 compute units, with a default limit of 200,000 compute units per instruction. You can request a specific compute unit limit by including a `set_compute_unit_limit` instruction in the transaction.

```py
rq = pxsol.core.Requisition(pxsol.program.ComputeBudget.pubkey, [], bytearray())
rq.data = pxsol.program.ComputeBudget.set_compute_unit_limit(200000)
```

You can also pay a small priority fee per compute unit. To do so, include a `set_compute_unit_price` instruction in the transaction.

```py
rq = pxsol.core.Requisition(pxsol.program.ComputeBudget.pubkey, [], bytearray())
rq.data = pxsol.program.ComputeBudget.set_compute_unit_price(1)
```

Priority fees are priced in micro-lamports, with the conversion rule being 1,000,000 micro-lamports = 1 lamport.

> Top secret: Setting the priority fee to just 1 micro-lamport can easily prioritize your transaction over those without a priority fee! While some tools tracking Solana's priority fees in real-time might suggest fees in the thousands, you don't actually need to pay such exorbitant amounts!

## Exercise

Q: Ada prepares to transfer 1 SOL to Bob, but he notices the network is heavily congested. He decides to add a small priority fee to the transaction!

A:

```py
import base64
import pxsol

ada = pxsol.core.PriKey.int_decode(1)
bob = pxsol.core.PubKey.base58_decode('8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH')

r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(ada.pubkey(), 3))
r0.account.append(pxsol.core.AccountMeta(bob, 1))
r0.data = pxsol.program.System.transfer(1 * pxsol.denomination.sol)

r1 = pxsol.core.Requisition(pxsol.program.ComputeBudget.pubkey, [], bytearray())
r1.data = pxsol.program.ComputeBudget.set_compute_unit_price(1)

tx = pxsol.core.Transaction.requisition_decode(ada.pubkey(), [r0, r1])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([ada])
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
assert pxsol.base58.decode(txid) == tx.signatures[0]
pxsol.rpc.wait([txid])
```
