# Solana/Economic System/Genesis Block (Part 1)

The Solana blockchain officially launched on March 16, 2020, with its genesis block being the first block of the blockchain, marking the network's launch. The genesis block itself does not contain source code, but rather serves as a snapshot of the initial state, defining the network's initial parameters, account states, and token distribution. Solana's genesis block can be viewed through blockchain explorers, but to specifically examine the transactions or accounts in the genesis block, queries must be made through nodes or related tools.

In Solana, calling the genesis block a "block" is somewhat misleading, it's more appropriate to think of it as a configuration file.

You can "query" the genesis block through blockchain explorers, but aside from the most basic data, you cannot obtain more meaningful information from the browser: <https://explorer.solana.com/block/0>.

## Genesis Block Token Distribution

Solana's initial token distribution was completed through the genesis block at network launch. According to the Solana whitepaper, SOL tokens in the genesis block were primarily allocated to the following categories of participants:

1. Seed round and early investors: Including venture capital firms (such as a16z, Multicoin Capital, etc.) and early supporters.
2. Team and foundation: Solana Labs team and Solana Foundation retained a portion of tokens for development and ecosystem building.
3. Community and rewards: Some tokens were allocated for community incentives, validator rewards, etc.

According to **unofficial sources** from public information and community discussions, Solana's initial token distribution was roughly as follows:

1. Seed round and private sale: Approximately 25-30% allocated to early investors.
2. Team: Approximately 12.5%.
3. Foundation/ecosystem: Approximately 10-15%.
4. Community/rewards: The remaining portion for validator rewards, airdrops, and other community incentives.

We should view the above information with caution.

## Obtaining Genesis Block Data

To more accurately study Solana's economic system, I decided to directly analyze the data in the genesis block. Fortunately, genesis block information is **semi-public**. You can obtain genesis block data from the network, but at the same time, there's a lack of tutorials online to teach you how to analyze it, and no websites or charts display it, which is why I call it semi-public. This article will attempt to change that.

First, we download and extract the compressed archive of genesis block data to obtain the `genesis.bin` file.

```sh
$ mkdir ledger
$ cd ledger
$ wget https://api.mainnet-beta.solana.com/genesis.tar.bz2
$ tar -jxvf genesis.tar.bz2
$ ll

# drwxrwxr-x   2 ubuntu ubuntu   4096 Aug  8 18:24 ./
# drwxrwxrwt 101 ubuntu ubuntu  65536 Aug  8 18:28 ../
# rw-r--r--    1 ubuntu ubuntu 132347 Mar 16  2020 genesis.bin
```

This file uses bincode encoding for a list of accounts. We need to compile a tool to analyze the `genesis.bin` file. Download the Solana source repository and compile the `ledger-tool` utility within it.

```sh
$ git clone https://github.com/anza-xyz/agave
$ cd ledger-tool
$ cargo build
```

Execute the compiled `agave-ledger-tool` and specify the directory where we saved `genesis.bin` in the parameters:

```sh
$ agave-ledger-tool genesis --ledger ledger --accounts --output json
```

We obtained a list of all accounts that received initial allocation in the genesis block. This list contains a total of 431 accounts. Here, we only show the first and last two accounts as excerpts.

```json
{
  "accounts": [
    {
      "pubkey": "13LeFbG6m2EP1fqCj9k66fcXsoTHMMtgr7c78AivUrYD",
      "account": {
        "lamports": 153333633390909120,
        "data": [
          "AQAAAIDVIgAAAAAAEz9W2TmIqMRgQ0rrgC89RndskM9PojDPkwTMSiLZq/lkVvBa571/bSeULSeR8aaRDAXCdHyD8RGsnvQTimS4AgAAAAAAAAAAAAAAAAAAAAAFR0dn5PH8Rp6b7RVvpNOHD2ek8+95bZYJHcoJ866WowAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
          "base64"
        ],
        "owner": "Stake11111111111111111111111111111111111111",
        "executable": false,
        "rentEpoch": 0,
        "space": 200
      }
    },
    ... ...
    {
      "pubkey": "JCo7ptMT38iZdjXXdxD8Ye79dGBBkMi2nttnv965k3pE",
      "account": {
        "lamports": 104166666268940,
        "data": [
          "AQAAAIDVIgAAAAAAHo5ufv6LXJUFQplRqRqFRQY4YFx4p81H20CZkWDY9q37k5kcYLD2AC8789vlnsUxaVMBz0/FeathVFoOL2wFSwAAAAAAAAAAigoAAAAAAAAFR0dn5PH8Rp6b7RVvpNOHD2ek8+95bZYJHcoJ866WowAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
          "base64"
        ],
        "owner": "Stake11111111111111111111111111111111111111",
        "executable": false,
        "rentEpoch": 0,
        "space": 200
      }
    },
}
```

You can directly download the pre-parsed JSON file I prepared at: <https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/genesis.json>.

```sh
$ wget https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/genesis.json
```
