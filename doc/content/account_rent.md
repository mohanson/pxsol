# Solana/Account Model/Rent and Rent Exemption Mechanism

On Solana, every account consumes storage space, and this data is ultimately stored by validator nodes in the cluster. To account for this, Solana employs a rent mechanism: you must pay rent for every byte of data you store on-chain. However, to avoid the hassle of frequent rent renewals, Solana also implements a rent exemption system.

## Rent

Accounts on Solana are not free, they occupy storage resources, and validators must maintain this data. As a result, Solana requires each account to reserve a portion of SOL as prepaid rent for data storage.

Key rules of the rent system:

- The more data an account stores, the larger its footprint, and the more rent it requires.
- Rent is prepaid and is debited from your account on a regular basis.
- If the balance falls short and the account remains inactive, the system may reclaim it.

The rent is effectively a part of the account's balance, and the Solana runtime calculates the duration of storage based on current rent rates.

The core reason for this mechanism is to prevent account spamming, which could be caused by:

- Users creating many empty accounts without cleanup.
- Programs leaving behind unused data after deployment.
- Bugs leading to an accumulation of temporary accounts.

If account creation had no cost, the state size on-chain would grow unchecked, eventually degrading network performance and stability. The rent model forces users to be accountable for their on-chain state, using economic incentives to manage resources.

## Rent Exemption

To make things easier, Solana also offers a rent exemption mechanism: if an account holds enough SOL to meet a certain threshold, it's considered prepaid for permanent storage, and the account won't be reclaimed.

For example, if you create a data account that takes up 100 bytes, the system calculates the required rent exemption, say, 0.002 SOL. As long as you deposit at least that much into the account, it is marked as exempt and will never incur rent charges or be deleted.

This mechanism is practical and offers several benefits:

- Developers don't need to manage rent renewal logic.
- Users don't have to worry about account expiration.
- Programs can run more reliably without rent-related disruptions.

From the beginning, Solana supported both rent and rent exemption. However, in [SIMD-0084](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0084-disable-rent-fees-collection.md), the core team proposed removing periodic rent collection. According to discussions on Solana Stack Exchange, this change was deployed before December 6, 2023.

As a result, Solana has completely removed the logic for collecting rent. That means: although rent still exists conceptually within the network, the system no longer collects it or deletes accounts for insufficient balance. Effectively, all accounts are now treated as rent-exempt, once created, they persist indefinitely.

> In fact, I spent a lot of time verifying the accuracy of this change. Be aware that some official documentation and third-party blog posts may still contain outdated information. Always cross-reference with the proposal and community discussions.

## Rent Cycle

Technically, each account stores metadata about its last rent collection time and balance. Solana used to perform rent collection once per epoch (about every two days). If an account didn't meet the exemption threshold, hadn't been accessed for a long time, and lacked sufficient balance, it could be flagged as "cleanable", allowing nodes to purge its data and free up storage.

As a developer, if you mark a data account as rent-exempt during creation, you generally don't need to worry about it again.

> Note: The actual logic for periodic rent collection has been completely removed from the Solana network.

## Calculating Rent Exemption

You should calculate the exemption amount during account initialization. Estimate the account's data size and deposit sufficient SOL accordingly. The rent rate is dynamic and determined by the network. You can query the required exemption amount via the [get_minimum_balance_for_rent_exemption](https://solana.com/zh/docs/rpc/http/getminimumbalanceforrentexemption) RPC endpoint.

Q: How much rent exemption is needed if you wants to store 100 bytes of data in an account?

A: The current requirement is 1,586,880 lamports. Note that this value may change over time.

```py
import pxsol

print(pxsol.rpc.get_minimum_balance_for_rent_exemption(100, {}))
# 1586880
```

## Developer Considerations

Solana's rent mechanism exists to control the cost of state storage and discourage unbounded growth. At the same time, rent exemption simplifies development: by funding accounts with enough SOL, you ensure their data is retained permanently.

For developers, the most important task is to correctly fund accounts at initialization to meet the rent exemption threshold.
