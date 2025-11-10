# Solana/Economic System/Staking

For users unable to independently bear the operational costs of validator nodes, Solana provides a staking mechanism that offers token holders opportunities to earn inflation income.

## What is Staking

Staking is essentially a form of delegated proof of stake. Since running validator nodes is quite challenging for ordinary users, many users choose to delegate their SOL to a validator. After validators receive inflation rewards, they distribute rewards to users based on the "proof of stake" they hold.

## Technical Implementation

As mentioned earlier, validators only need to record user stakes and distribute rewards, so there is no "official" staking program. Different validators can develop their own staking programs and adopt different underlying technical implementations.

The most intuitive approach is for users to deposit SOL into an on-chain program, which records user account addresses and deposited SOL. When validators receive rewards, they transfer rewards proportionally to users based on on-chain data. This method is less efficient but was widely adopted in early blockchain mining pools. Another issue is that transfers consume substantial transaction fees, and user earnings might not even cover a single transfer fee.

The current mainstream approach is: when users deposit SOL, the on-chain program issues a certain amount of "stake tokens." When validators receive inflation rewards, they deposit the earned SOL into the on-chain program's stake pool, causing the price of stake tokens held by users to rise. When users are ready to redeem their staked assets, they simply need to sell their stake tokens to retrieve their SOL principal plus interest. Users can not only sell stake tokens to the on-chain program but also transfer or sell them to other users. This mechanism is actually the world's most attention-grabbing financial innovation: tokenization of stakes.

## Choosing a Staking Pool

Solana supports multiple wallets, and most wallets support staking functionality. Common wallets include:

- Phantom: A very popular Solana wallet that supports staking and managing SOL tokens.
- Sollet: An open-source Solana wallet.
- Solflare: Another commonly used Solana wallet that supports staking and token management.
- ...

Generally, you only need to use the above wallets to find staking entry points on the main interface. The image below shows Phantom wallet's staking page, displaying an expected annual yield of 8.77%. However, I questions this data, as Solana's current nominal inflation rate is approximately 4.3%, with a network-wide staking rate of about 65%. Theoretically, the maximum inflation yield stakers can receive is `4.3% / 0.65 = 6.61%`. Even adding Phantom's additional rewards (such as fees, priority fees, and transaction reordering rewards, i.e., MEV), rough estimates suggest it can reach at most 7%, making it difficult to achieve 8.77%.

![img](../img/economy_stake/stake.jpg)

> MEV (Maximum Extractable Value) refers to additional profits that miners, validators, or other blockchain participants can obtain beyond block rewards and transaction fees by reordering, including, or excluding transactions within blocks. Originally called "Miner Extractable Value," it evolved into "Maximum Extractable Value" with its widespread application across different blockchain ecosystems.

In fact, I checked the yields of several current largest staking pools and found most are around 6%~7%. As of September 2, 2025, data from some major pools are as follows:

- [Binance](https://www.binance.com/de/solana-staking): Approximately 5.88%
- [Jito](https://jito.network/): Approximately 6.73%
- [Jpool](https://jpool.one/): Approximately 9%, this pool performs far above average
- [Marinade Finance](https://marinade.finance/): Approximately 7.04%
- [Phantom](https://phantom.app/): Approximately 8.77%
- [Solblaze](https://stake.solblaze.org/app/): Approximately 7.02%
- ... ...

Currently, I haven't found a reasonable explanation for Phantom wallet's above-average yield. I may attempt to analyze this 8.77% figure in detail when possible, but for now, let's focus on the content of this article.

## Risk Diversification

To reduce risk, it's recommended to diversify SOL staking across multiple validator pools. This not only reduces risk when a single validator node encounters problems but also minimizes yield volatility through rewards from different pools.

Please note that the security of your staked assets depends entirely on the staking program provided by validators. Staking programs may have vulnerabilities or even malicious backdoors, so choosing validators with good reputation and high transparency is very important.

If you're interested in Solana staking, it's recommended to start with small-scale testing, gradually accumulate experience, and then gradually expand staking scale. In blockchain networks, acting cautiously is always wise.
