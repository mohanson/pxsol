# Solana/Economic System/Transaction Fees and Fee Burning

Solana's fee structure adopts a two-tier system, primarily consisting of base fees and priority fees, supplemented by a storage rent mechanism to support efficient network operation and anti-spam transaction capabilities.

## Base Fees

Every Solana transaction requires payment of a base fee to compensate validators for the computational resources needed to process transactions. The base fee is fixed at 5000 lamports per signature. Using 2025's SOL price of approximately $200 as an example, 5000 lamports equals about $0.001, or one thousandth of a dollar. This fixed fee rate design ensures that Solana's transaction costs remain stable even during network congestion, forming a stark contrast to auction-based fee models like Ethereum.

Solana's fee burning mechanism is an important component of its economic model, aimed at supporting the long-term value of the token by reducing SOL's circulating supply. 50% of the base fee (i.e., 2500 lamports per signature) is burned and permanently removed from circulation, while the remaining 50% is allocated to the validator that processes the transaction.

At the time of writing, according to data from [Solana Compass](https://solanacompass.com/statistics/fees), users paid a total of 1675.48 SOL in base fees over the past 24 hours, meaning 837.74 SOL was simultaneously burned and destroyed. Based on this estimate, the annual burn amount is approximately 305775 SOL. Calculated at 2025's SOL price of $200, the annual burn value is approximately $61155000.

This burning mechanism is similar to Ethereum's [EIP-1559](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md), enhancing SOL's potential as a store of value by reducing token supply.

## Priority Fees

Priority fees are optional additional fees that users can pay to increase the probability of their transactions being prioritized by the current leader (i.e., validator). The priority fee calculation formula is `compute unit limit × compute unit price`.

The compute unit limit is the maximum computational resources a transaction can use, with an upper limit of 1.4 million compute units and a default of 200000. The compute unit price is specified by the user. According to [SIMD-0096](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0096-reward-collected-priority-fee-in-entirety.md), priority fees are entirely collected by the validator processing the transaction and are not burned.

At the time of writing, according to data from [Solana Compass](https://solanacompass.com/statistics/fees), users paid a total of 3268.76 SOL in priority fees over the past 24 hours, with 66.42% of transaction users paying priority fees.

## Storage Rent

On Solana, storing account data requires payment of rent, with fees proportional to the space occupied by the account. Rent fees are refundable when accounts are closed, designed to incentivize users to clean up unnecessary on-chain data. 50% of rent fees are burned, while the remaining 50% is allocated to validators.

Rent fees effectively remove half of the SOL permanently from the liquidity pool and **temporarily** remove the other half from the liquidity pool. Unless users decide to delete their accounts, this portion of rent will never participate in circulation. According to [CoinLaw's report](https://coinlaw.io/solana-statistics/), Solana currently adds approximately 200000 new wallets each week, averaging about 28571 new accounts per day.

> More than 200,000 new wallets are created on Solana each week, indicating robust organic adoption.

Assuming an average account data size of 165 bytes (typical size for SPL token accounts), we can use the following code to estimate that daily new rent consumption is approximately 83 SOL.

```py
import pxsol

pxsol.config.current = pxsol.config.mainnet

lamport = pxsol.rpc.get_minimum_balance_for_rent_exemption(128 + 165, {}) * 28571
sol = lamport / pxsol.denomination.sol
print(sol) # 83.71760136
```

However, in reality, if a developer wants to deploy program accounts on the Solana network, the rent they need to pay is far greater than that of a regular user account. Therefore, this 83 SOL figure is extremely underestimated.

## Summary

Solana's fee rules achieve a low-cost, predictable, and highly efficient transaction experience through a combination of fixed base fees, optional priority fees, and storage rent. Theoretically, the fee burning mechanism can effectively reduce SOL's circulating supply and enhance the token's economic value. However, based on actual data, the SOL burned represents only a tiny fraction of annual inflationary issuance (refer to data from the previous chapter), meaning that relying on fee burning to turn inflation into deflation is impossible in the short term.
