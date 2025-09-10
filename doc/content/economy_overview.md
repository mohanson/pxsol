## Solana/Economic System/Overview

The core goal of Solana's economic design is to incentivize **validators** and **stakers** to provide computing, storage, and security guarantees for the network through three major mechanisms: **inflation**, **staking**, and **transaction fees**.

Let's first discuss two core roles in the Solana system.

- Validators are servers running Solana software, responsible for processing transactions, validating blockchain state, and generating new blocks. They are the workers of the Solana network, maintaining network operations. Validators earn transaction fees and block rewards (from inflation rewards) by processing transactions. If stakers delegate SOL to the validator, the validator can also extract a certain percentage of commission from staking rewards (set by the validator themselves).
- Stakers are users who hold SOL tokens and delegate their SOL to a validator node to support network decentralization and security. Stakers can receive certain staking rewards.

Three core mechanisms maintain the entire system:

- Inflation: Used to continuously distribute rewards to validators and stakers, thereby maintaining node operation incentives.
- Staking mechanism: Allows token holders to participate in network security by delegating tokens to validators while earning returns, preventing excessive liquidity.
- Transaction fees: Both compensation for network resource usage and a defense mechanism against speculative attacks (such as spam transactions).

You can see that Solana's economic system design is very similar to the real-world USD/Treasury system: releasing liquidity through inflation and reclaiming liquidity through staking to maintain dynamic equilibrium. Through the coordinated operation of these mechanisms, Solana seeks to find a balance between unlimited token supply growth and token value stability, enabling the network to develop rapidly while maintaining economic sustainability.

This series of articles will take you deep into understanding the operational logic of Solana's economic system, from inflation curves to staking returns, from transaction fee allocation to long-term supply and demand relationships, helping you comprehensively understand this mechanism.
