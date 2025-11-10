# Solana/Transaction/Currency Denomination

The native cryptocurrency of the Solana network is called SOL. It is similar to other blockchain's tokens, such as Bitcoin's BTC and Ethereum's ETH, used for paying transaction fees, participating in network governance, and serving as a store of value.

The smallest unit of measurement on the Solana network is called "Lamport". Like Bitcoin's "Satoshi", Solana also needs a smaller unit to accurately represent very small transaction amounts. 1 SOL equals 10⁹ Lamports, which prevents precision loss issues when handling micro-transactions.

Q: How many Lamports is 0.33 SOL?

A: 0.33 * 10⁹ = 330,000,000 Lamports. The `pxsol.denomination` library defines the values of SOL and Lamport, which can be used for conversion with the following code:

```python
import pxsol

print(int(0.33 * pxsol.denomination.sol))
# 330,000,000
```

Lamport is a subunit of SOL, similar to the relationship between dollars and cents (1 dollar = 100 cents). On the Solana network, all balances and transaction amounts are expressed in Lamports, but users typically interact with the network using SOL as a unit. When performing transactions or transferring funds, SOL is displayed as the user interface unit.

The origin of the name "Lamport" comes from Anatoly Yakovenko, the creator of Solana. Yakovenko decided to use the name "Lamport" in tribute to [Leslie Lamport](https://en.wikipedia.org/wiki/Leslie_Lamport), a renowned computer scientist in the field of distributed systems and concurrent computing. Leslie Lamport's work has had significant impacts on modern blockchain technology, particularly in the areas of distributed system synchronization and consensus mechanisms.

As for why SOL was chosen as the token's name, there is no concrete evidence, but it can be speculated:

1. Blockchain projects often use three-letter names, which was a convenient choice during Solana's development phase.
2. The name "SOL" implies a connection to "Solar", symbolizing an energetic and growing future.

In closing, I will give you some advice. You should pay special attention to all activities in the Solana network:

1. Lamport is the actual smallest unit of measurement on the Solana network, while SOL is more of a symbolic representation.
2. As a developer, you should always operate in Lamports, but display SOL only when necessary for user interface purposes.
