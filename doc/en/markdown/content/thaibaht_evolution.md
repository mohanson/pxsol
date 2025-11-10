# Solana/Thai Baht Coin/Evolution

When we develop decentralized applications in the blockchain world, we often start with the simplest on-chain data storage system. About 8 years ago, when I first encountered the blockchain world, the first tutorial I came across taught how to write a data storage system on Ethereum. Today, as a new tutorial author, when I thought about which application to use as an example, I immediately thought of this one. I must admit, this is a continuation of the open-source spirit.

I love a saying: **Algorithm + Data Structures = Program**. I believe even decentralized applications follow this principle. Once you understand how to store arbitrary data on-chain, you can implement any program by adjusting the algorithms.

> Algorithms + Data Structures = Programs is a classic work by N. Wirth.

The essence of an on-chain data storage system is using a data account to store a user's arbitrary information on the chain.

If we want to develop it into a "Thai Baht Coin" program, we just need to make some changes in three aspects: data format, instruction interaction, and account management. Let's look at how it evolves step by step from a data storage system.

## Account Data: From Simple Data to Balance

In the initial version of the data storage system, the data account structure was very simple, allowing users to store data in any format or length. Each user had their own data account, and the program only needed to verify the PDA address and the user's signature to write data.

In the Thai Baht Coin program, we need to ensure that the data account is no longer just a personal space for arbitrary reading and writing but an actual balance account. We define that the data account can only store a 64-bit unsigned integer, encoded in big-endian format.

In this way, each user's data account is like a sub-account in the token program's ledger, clearly recording how much Thai Baht Coin the user holds.

## Two Instructions: Mint and Transfer

At the stage of the on-chain data storage system, the program had only one instruction for storing or updating data. Now, based on that instruction, we need to develop two new instructions:

0. Mint: Initiated by the minting authority (usually the program deployer), this instruction mints new Thai Baht Coin for the owner, i.e., increases the total currency supply.
0. Transfer: User "ada" transfers Thai Baht Coin to user "bob", requiring user "ada" to sign, and updates both parties' data accounts (balance accounts).

These two instructions need not only to read and write to balance accounts but also perform basic checks:

0. Mint: Can only be initiated by an authorized account.
0. Transfer: Verify that the sender has sufficient balance, and handle integer overflow issues carefully.

Design the data format for receiving these instructions. In short, the Thai Baht Coin program accepts just 9 bytes of data. The first byte distinguishes whether you want to mint or transfer, and the remaining bytes represent the amount of tokens to mint or transfer.

0. Mint: `0x00` + u64
0. Transfer: `0x01` + u64

## Account List

Each instruction must explicitly declare the accounts it uses (the accounts parameter), otherwise, it cannot run on Solana. An additional point to note is that if the user does not yet have a data account, we need to create one for them.

Here's the summary of the account list:

**Mint**

| Account Index |     Address     | Needs Signature | Writable | Permission(0-3) |                Role                |
| ------------- | --------------- | --------------- | -------- | --------------- | ---------------------------------- |
| 0             | ...             | Yes             | Yes      | 3               | Minting authority's wallet account |
| 1             | ...             | No              | Yes      | 1               | Minting authority's data account   |
| 2             | `1111111111...` | No              | No       | 0               | System                             |
| 3             | `SysvarRent...` | No              | No       | 0               | Sysvar rent                        |

**Transfer**

| Account Index |     Address     | Needs Signature | Writable | Permission(0-3) |           Role            |
| ------------- | --------------- | --------------- | -------- | --------------- | ------------------------- |
| 0             | ...             | Yes             | Yes      | 3               | Sender's wallet account   |
| 1             | ...             | No              | Yes      | 1               | Sender's data account     |
| 2             | ...             | No              | No       | 0               | Receiver's wallet account |
| 3             | ...             | No              | Yes      | 1               | Receiver's data account   |
| 4             | `1111111111...` | No              | No       | 0               | System                    |
| 5             | `SysvarRent...` | No              | No       | 0               | Sysvar rent               |

## Not the End

Unlike Ethereum's ERC20, Solana's program world is very flexible. We need to manage the minting authority. In this tutorial, we've chosen to hardcode the minting authority into the program, but you could also create a separate "authority account" to manage the minting permissions.

You can also add other functionalities, such as burning or bulk transferring. While these features may not be very commonly used, they are crucial for certain scenarios. For instance, if you want to perform airdrops to millions of users, without a bulk transfer function, the transaction fees and time required might be unbearable.

From the initial on-chain data storage system to a full-fledged Thai Baht Coin program, the key lies in:

- Evolution of the data format: From a simple byte string to a balance account structure.
- Evolution of instructions: From simple data storage and updates to minting and transferring.
- Evolution of the account list.

The world is yours to define. Witness the birth of your Thai Baht Coin!
