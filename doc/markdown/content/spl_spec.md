# Solana/SPL Token/History and Core Specification Overview

Let's rewind to 2017. The year when [ERC-20](https://github.com/ethereum/ercs/blob/master/ERCS/erc-20.md) officially became the token standard on Ethereum. It defined a standardized interface for smart contracts, greatly reducing the complexity of creating tokens. By adhering to this unified standard, developers could issue tokens quickly without reinventing the wheel.

This specification directly fueled two major crypto bull runs: the first in 2017, driven by ICOs (Initial Coin Offerings), which attracted massive capital and developers into the Ethereum ecosystem and established Ethereum as the leading smart contract platform; the second in 2021, led by DeFi (Decentralized Finance), where nearly all the now-familiar DeFi protocols (like Uniswap, Compound, Aave, etc.) relied on ERC-20 tokens for value transfer, liquidity provision, and on-chain governance.

We can say with confidence: tokens were the key driver behind Ethereum's ecosystem growth.

Now the question turns to Solana. As a young challenger in the space, how should Solana design and implement its own token standard?

## Breaking the Pattern

Unlike Ethereum, Solana's account model doesn't include built-in logic like "how much balance does this wallet have?" Developers must manually implement token storage, minting, and transfer logic using PDA data accounts. This approach is error-prone and leads to lots of redundant work. Users also face a major issue: different tokens may support different instruction sets.

To solve this, the Solana team introduced SPL Token which is a unified token standard. Inspired by Ethereum's ERC-20, it provides developers with a standardized interface to ensure compatibility across the ecosystem. This allows wallets, decentralized exchanges, DeFi apps, and more to universally recognize and interact with tokens.

Thanks to Solana's support for native programs, developers don't need to deploy the SPL Token code themselves. Instead, they simply create a special account which called a Mint Account to store the basic info of the token and thereby create their own SPL Token.

## Querying Some On-Chain Token Info

Let's take USDC, one of the most widely used tokens on Solana. Its Mint Account address is `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`. You can view it via the [Explorer](https://explorer.solana.com/address/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/metadata). Some key details like total supply, decimal precision, and name are shown below:

|    Overview    |       Value       |
| -------------- | ----------------- |
| Current Supply | 7761611891.221625 |
| Decimals       | 6                 |
| data.name      | USD Coin          |
| data.symbol    | USDC              |

According to [recent data](https://learn.backpack.exchange/articles/pump-fun-token-launch-2025-pump-airdrop-rumors-1b-raise-and-solana-market-impact), as of June 2025, there are approximately 13 million SPL tokens on the Solana network. Of those, [pump.fun](https://pump.fun/) alone minted over 11 million tokens. The all-time high was on October 24, 2024, when a staggering 36,000 new SPL tokens were created in a single day.

Creating a new token on Solana is virtually costless. Any moderately experienced developer can do it in under a second. Websites like pump.fun and let's bonk offer one-click token creation features that have also attracted many non-developer users, fueling the explosion in token count.

> No time to explain, let's just mint it!

## Historical Development

When Solana first launched, SPL Token debuted as a minimal viable product (v1). It supported only the basics: minting, burning, and transfers. The goal was simply to prove the token system worked, with no emphasis on advanced features.

With the emergence of decentralized exchanges like [Raydium](https://raydium.io/), SPL Token became the backbone for asset transfer on Solana (v2). This phase focused on wallet compatibility and introduced the concept of Token Metadata. Initially provided by Metaplex, this extension aimed to augment the limited v1 by allowing tokens to include human-readable fields like name, symbol, and image.

From 2023 onward, SPL Token v3 (also known as Token-2022) introduced more powerful features like account freezing and transfer hooks (supporting contract-style callbacks). However, this also meant that Token-2022 became partially incompatible with earlier SPL versions, and some older wallets or applications might not fully support it. Even so, if you're creating a new token today, starting with Token-2022 is the most hassle-free path, So this course will assume the Token-2022 standard.

## Core Specification Overview

Creating an SPL token involves two core components:

- **Token Program**: The main program that handles token creation, transfers, burns, etc. There are two versions:
    - `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`, the newer version, Token-2022.
    - `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`, the older version, now largely deprecated. You may still see it associated with early tokens in explorers.
- **Mint Account**: Stores base data like total supply and decimals. Each SPL token has a unique Mint Account. Starting from Token-2022, this account can also include "extension data," with the most common extension being Token Metadata for storing human-readable info like name, symbol, and logo URL.

The data structure of a typical Mint Account looks like this:

```text
┌─────────────────────────────────────┐
│            Mint Account             │
│-------------------------------------│
│      decimals:         u8           │
│      supply:           u64          │
│      mint_authority:   Pubkey       │
│      freeze_authority: Pubkey       │
│-------------------------------------│
│      ... ...                        │
│-------------------------------------│
│      name: "Thai Baht Coin"         │
│      symbol: "THB"                  │
│      uri: "http://accu.cc/..."      │
└─────────────────────────────────────┘
```

Due to historical reasons, SPL Token was designed in this way. If you dive into the source code, you'll notice it carries quite a bit of legacy baggage. Internally, a rather complex data structure is used to store token info within the Mint Account. The base data defines supply and permissions, while the metadata attached to maintain backward compatibility acts like a wrapper to provide human-readable info such as name and logo.

Solana has laid the tracks. All that's left is for you to start the engine.
