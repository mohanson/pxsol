# Solana/Economic System/Validator Costs and Expected Returns

Becoming a Solana validator is an important way to participate in the Solana network. Validators can earn tokens from Solana's inflationary issuance and collect priority fees from user transactions. In this article, we will discuss the costs involved in becoming a Solana validator and the expected returns.

## Validator Responsibilities

Solana uses a Proof of History consensus mechanism. You may know that "Bitcoin miners" maintain the operation of Bitcoin nodes. In the Solana network, this role of maintaining node operations is called a "validator." The main responsibilities of validators in the Solana network include:

- Transaction validation: Validators check and confirm the validity of transactions and blocks.
- Block generation: Validators participate in voting to reach consensus and generate new blocks.
- Network security: Validators ensure network integrity and prevent malicious tampering by participating in consensus.

## Validator Hardware Costs

At the time of writing, the Solana network has 1029 validators. You can check <https://solana.com/validators> to track the number of validators in real-time. Becoming a Solana validator requires some technical preparation and hardware configuration.

For technical details, the official comprehensive tutorial is located at <https://docs.anza.xyz/operations/>, but in this article we primarily focus on the economic behavior of validators, so let's first assess approximately how much investment is needed to become a validator. According to official requirements, validator hardware requirements are:

- High-speed internet connection: At least 100 Mbps or higher network bandwidth to handle large volumes of transactions.
- Reliable power supply: Ensure servers are online 24/7.
- Processor: 12 cores or more, at least 3.0 GHz
- Memory: 256 GB or more
- Storage: NVMe SSD, at least 1TB storage

This configuration requirement already far exceeds ordinary home computers. Additionally, the Solana network has requirements for node uptime: if a node goes offline:

- Solana validators confirm blocks and earn rewards through voting. If a node goes offline or cannot vote in time, the validator will miss corresponding voting rewards.
- Validator staking rewards are directly related to the node's activity and performance. Downtime will cause the node's voting success rate to decline, thereby reducing staking rewards allocated to that node.
- The Solana network's validator ranking and selection mechanism partly depends on node performance metrics. Frequently offline nodes may decline in rankings, affecting their ability to attract more stake. This has indirect effects on validators' long-term returns and network status.

**We can draw an approximately correct conclusion**. To become a Solana validator, we only have two choices: build our own data center or purchase cloud servers. It's difficult for me to assess the cost of building our own data center, so here I only consider purchasing cloud servers.

Based on hardware requirements, suitable instance types on [Amazon](https://aws.amazon.com/ec2/instance-types/) for running Solana validator nodes, the most suitable and low-cost option is `m8g.16xlarge`, which costs approximately $3.15955 per hour, or $1498.78 per month. The above prices do not include storage. Solana validators require high-speed NVMe SSD storage, with at least 1TB recommended, but may actually need 2TB or more. Amazon's EBS (Elastic Block Store) storage costs are as follows: gp3 volumes (general purpose SSD) cost $0.08 per GB per month. So 2TB (2000GB) storage would cost 2000 × $0.08 = $160/month. If higher throughput is needed (such as io2 volumes), costs may increase to $200-$300/month.

Solana validator nodes have very large data transfer volumes, potentially averaging 60-100TB per month (mainly outbound traffic, inbound traffic is usually free). Amazon's data transfer costs are typically $0.09 per GB (US region). Assuming 80TB outbound traffic per month, the traffic cost would be 80000 × $0.09 = $7200. Bandwidth costs are the main expense of running Solana validator nodes. Amazon's traffic costs are relatively cheap from a global perspective. In mainland China, traffic costs per GB could be several times or even dozens of times more than Amazon's.

Thus, we estimate total hardware costs at $9000 per month, and this expense is merely the minimum configuration requirement for becoming a Solana validator.

## Validator Voting Costs

An important job for Solana validators is voting, and validators must pay fees for each vote transaction. The voting cost per epoch (about 2 days) is approximately 2.16 SOL (each vote transaction costs 0.000005 SOL in fees, 432000 slots/epoch). Calculated at a SOL price of $200: approximately 1.1 SOL per day × $200 = $220/day, which equals about $4950 per month.

The Solana Foundation Delegation Program (SFDP) may cover part of the voting costs for new validators in the first year (100% reimbursement in the first quarter, then gradually decreasing), which can significantly reduce initial costs.

## Staking

The Solana network itself does not have strict regulations on the minimum staking amount for validators, but to obtain voting rights and effectively participate in the network, validators typically need to stake a certain amount of SOL. Generally speaking, the amount of staked SOL affects the validator's voting weight, which in turn affects their probability of being selected to validate transactions. Validators can only receive inflation rewards when selected. Therefore, to break even, validators must stake enough SOL to increase their chances of being selected and earn sufficient inflation rewards to cover hardware costs and voting fees.

Fortunately, validators can not only stake their own SOL but also accept delegated stakes from other users. This means that even if you don't have large amounts of SOL yourself, you can increase your validator node's total stake by attracting stakes from others.

Solana inflation rewards are distributed to validators and their delegators at the end of each epoch based on validators' stake weight and voting performance. Currently (as of September 2025), Solana's annualized inflation rate is approximately 4.4%, equivalent to a monthly inflation rate of 0.366%. Solana's current total supply is 608 million, meaning approximately 2228052 new SOL are added monthly. To cover hardware costs and voting fees, validators need to earn approximately 75 SOL, which represents `75 / 2228052 = 0.00336%` of newly inflated tokens. Currently, there are 400 million SOL staked in the Solana network, so validators need to stake (or have delegated to them) at least `400000000 × 0.0000336 = 13440` SOL.

Opening <https://solscan.io/validator> and analyzing all validators' staking amounts, statistics show that approximately 80% of validators have staking amounts higher than this figure. Therefore, I estimate that **80% of Solana validators are profitable, while the remaining 20% of validators are currently breaking even or possibly operating at a loss**. There is some other data that can support this view that some validators are operating at losses. The most direct evidence is that the number of validators is gradually decreasing. Over the past year, the number of validators has decreased from over 1300 to the current 1029, which happens to be approximately 20% of validators eliminated over the course of a year.

Note that part of validator revenue has not yet been accounted for, namely fee income. But we have already proven in previous articles that fees represent an extremely small proportion of inflation, so I directly ignored this portion when calculating validator returns. Whether to include this revenue in statistics will not significantly affect the above conclusions.

## Conclusion

Similar to Bitcoin miners, Solana validators also follow a "strong get stronger" pattern. The difference is that Bitcoin competes on hash power, while Solana competes on SOL staking amounts. Both are fully competitive markets. Over the past decade or so, Bitcoin's hash power has become increasingly concentrated in a few large mining farms. Currently, Solana's staking is also beginning to concentrate among a few large validator nodes. Whether this centralization is an ideal state still deserves further observation.

For users hoping to support the Solana network and earn rewards, becoming a validator is an attractive option, but it also means you need to invest huge initial capital: $15,000/month in hardware costs and at least 13,440 SOL in staking. In subsequent articles, we will try using an alternative method that allows you to earn Solana inflation rewards without paying such enormous costs.
