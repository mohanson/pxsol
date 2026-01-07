# Solana/SPL Token/Create Your Token

Pxsol's built-in wallet provides a simple and universal interface for creating your own SPL token (as well as performing standard SPL operations).

## Creating a Token

The process of creating a new token is straightforward. Here's an example:

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
spl = ada.spl_create(9, {
    'metadata': {
        'name': 'PXSOL',
        'symbol': 'PXS',
        'uri': 'https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json',
    }
})
print(spl) # 2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF
```

After running the code above, a new token will be created at the address `2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF`. This account is commonly referred to as the token's **Mint Account**. The function `spl_create()` accepts two parameters:

- `decimals`: The number of decimal places. For example, if decimals=9, then 1000000000 represents 1 full token.
- `extension`: Additional extensions for the token, the most common being metadata.
    - `metadata.name`: The name of the token.
    - `metadata.symbol`: The token symbol, usually a short version of the name, like BTC for Bitcoin.
    - `metadata.uri`: A URL pointing to a JSON file containing the token's metadata.

The token metadata JSON file typically has the following structure. You need to upload this JSON to a publicly accessible server, such as Arweave or IPFS, and pass its URL as the `uri` parameter when creating the token. The `image` field is especially important, it determines how your token is displayed in wallets, decentralized exchanges, and other applications.

```json
{
    "name": "PXSOL",
    "symbol": "PXS",
    "description": "Proof of study https://github.com/mohanson/pxsol",
    "image": "https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.png"
}
```

## Transaction Fees

Creating a new SPL token requires approximately 0.004 SOL in rent and 0.00001 SOL in transaction fees. As of June 2025, this amounts to around $0.60 USD, basically free!
