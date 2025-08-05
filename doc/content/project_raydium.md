# Solana/Deploying Your Token on the Mainnet/Listing on a Decentralized Exchange

In the blockchain world, a Decentralized Exchange (DEX) is a place where users can trade directly without a trusted intermediary. In traditional centralized exchanges (such as Binance, Coinbase), all transactions are matched by the exchange's central server, and the exchange is responsible for asset custody and transfer. However, such centralized exchanges come with trust risks. If the exchange is attacked or experiences operational issues, users' funds may be at risk.

A decentralized exchange, on the other hand, operates based on blockchain technology. It allows users to trade tokens directly without an intermediary, using smart contracts and automated market maker (AMM) algorithms. Users' funds are no longer stored on a centralized platform but are managed by smart contracts on the blockchain.

In the Solana ecosystem, [Raydium](https://raydium.io/) is one of the most popular DEXs. This section will guide you step by step on how to list your token on Raydium and provide liquidity for it.

## Listing Your Token on Raydium

To enable users to trade your token, you first need to create a liquidity pool for it. A liquidity pool consists of two tokens, and Raydium uses an automated market maker (AMM) model to provide liquidity.

In the previous section, we deployed the pxs token on the mainnet. Now, I'm ready to allow it to trade with SOL, so I need to create a pool for these two tokens. The process on the website is quite simple:

1. Go to <https://raydium.io/liquidity-pools/>
2. Click the "Create" button in the top right corner.
3. Select the pxs token and SOL token, then set the trading fee rate.
4. Set the initial price for the pxs token.
5. Done!

Since I provided liquidity for my token, Raydium will issue LP tokens to me. These tokens represent my share in the liquidity pool. You should keep these LP tokens safe, as you will need them to withdraw liquidity and reclaim your funds.

![img](../img/project_raydium/lptoken.jpg)

## Trading PXS on Raydium

Once the liquidity pool is created, users can trade through Raydium. Raydium uses the AMM model, where tokens are swapped via the pool without a traditional order book. Users can select a trading pair on Raydium's interface, input the amount they want to trade, and complete the transaction with a simple swap operation.

You can trade PXS through [this link](https://raydium.io/swap/?inputMint=6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH&outputMint=sol). I have created a small trading pool for PXS, where you can buy and sell PXS. Due to the low liquidity, trading may incur a significant slippage, which can cause the price to differ from expectations.

![img](../img/project_raydium/swap.jpg)

In the upcoming sections, I will implement an airdrop contract for the PXS token. You will be able to claim free PXS airdrops and sell them in this pool to exchange for SOL.

Stay tuned.
