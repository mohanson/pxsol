# Solana/Deploying Your Token on the Mainnet/Migrating from Testnet to Mainnet

After several days of hard work, our Thai Baht Coin, Bubble Coin, Cat Coin, and Turtle Coin are finally running smoothly on the local network, with features like minting and trading all functioning as expected. Now, it's time to consider deploying your token on the mainnet!

Migrating from localnet to mainnet is usually as simple as switching a URL. While this process seems straightforward, there are some important considerations to keep in mind.

## Common Environment Comparison

On Solana, we typically work with three different environments:

|   Network    |              Features              |                     Use Case                      |
| ------------ | ---------------------------------- | ------------------------------------------------- |
| Localnet     | Local node, fastest speed          | Single-node testing, early development validation |
| Devnet       | Public testnet, stable             | Contract testing, token experiments               |
| Mainnet Beta | Mainnet, where all real assets run | Real assets and transactions happen here          |

In pxsol, use the following code to switch between these three environments.

```py
import pxsol

pxsol.config.current = pxsol.config.develop  # Localnet, default
pxsol.config.current = pxsol.config.testnet  # Devnet
pxsol.config.current = pxsol.config.mainnet  # Mainnet Beta
```

Although the interfaces are mostly consistent, there are several key differences that must be noted.

- Sol on the local node and public testnet is free, but on the mainnet, Sol is valuable. You need to purchase Sol with real money.
- Many black hat and white hat hackers are keeping an eye on your contract: Permission issues missed during testing could turn into rug pulls once on the mainnet.
- Node rate limits: Mainnet nodes generally have higher RPC request limits, and frequent calls may result in your IP being banned.

## Estimated Costs

Deploying a complete token system typically involves the following operations:

|            Operation            |          Estimated Cost          |
| ------------------------------- | -------------------------------- |
| Create mint account             | Around 0.002 SOL                 |
| Create metadata account         | Around 0.01 SOL (higher storage) |
| Create initial token account    | Around 0.002 SOL                 |
| Initialize pool (e.g., Raydium) | Between 0.01 SOL to 0.05 SOL     |
| Airdrop contract deployment     | Over 0.5 SOL                     |

Therefore, preparing a budget of at least 1 SOL is a good baseline. As of July 2025, this is approximately $200.

## Rate Limiting

When sending high-frequency transaction requests on the mainnet, RPC rate limiting could be your biggest obstacle. By default, pxsol uses a public RPC, which has a relatively high rate limit. Therefore, you may notice significant performance degradation when switching pxsol to the mainnet: this is due to pxsol's efforts to avoid the rate limit imposed by public RPC.

You can customize the RPC request URL and the cooldown time between each RPC request with the following code:

```py
import pxsol

pxsol.config.current = pxsol.config.mainnet
pxsol.config.current.rpc.qps = 8
pxsol.config.current.rpc.url = 'https://api.mainnet-beta.solana.com'
```

You can also use paid RPC nodes, such as those provided by service providers like [Helius](https://www.helius.dev/) or [Triton One](https://triton.one/), or even set up your own full node on the mainnet. While this is more costly, it offers complete freedom.

## Image and Metadata Hosting Recommendations

Nobody wants their token logo to point to a 404. When running on the mainnet, metadata hosting is especially important. The recommended practice is to use Arweave or IPFS for storing images. You can also use GitHub, but occasionally it may fail.

> You successfully summoned the GitHub unicorn!

![img](../img/project_mainnet/unicorn.jpg)
