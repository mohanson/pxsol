# Solana/Deploying Your Token on the Mainnet/Designing Airdrop Rules

Running a token project on the mainnet always comes with the challenge of token distribution. Airdrops are a popular method to significantly increase the number of token holders, helping new projects attract users.

I have designed a simple airdrop mechanism for the PXS token, aimed at teaching and inspiring readers to design their own complex airdrop rules. Unlike traditional airdrops, the PXS token airdrop is planned to be distributed to anyone who has "completed this tutorial". The airdrop is automatically distributed through a smart contract, eliminating the need for manual token transfers. Readers only need to pay a very low Solana network transaction fee to receive a fixed amount of PXS tokens for free.

In the upcoming lessons, we will implement an airdrop program that will airdrop 5 PXS tokens to every user interacting with it, with no restrictions or limits.

However, please note that theoretically, anyone can claim an unlimited amount of PXS tokens, but the actual implicit limit is the Solana network transaction fee. In other words, the real value of 5 PXS tokens is equivalent to the transaction fee for one Solana transaction, which is approximately $0.001 today.
