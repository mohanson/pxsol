# Solana/SPL Token/Analyzing the Mint Account

The Mint Account is the core account type used to define and manage a token. It stores essential information about the token, such as supply, decimal precision, mint authority, and freeze authority. With the Token-2022 upgrade, the Mint Account can also include extension fields to support additional features like token metadata and transfer fees. Currently, the two most widely used extensions are the metadata pointer extension and the metadata extension.

Let's use the following code to inspect the token we created in the previous section.

```py
import base64
import pxsol

info = pxsol.rpc.get_account_info('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF', {})
data = bytearray(base64.b64decode(info['data'][0]))
mint = pxsol.core.TokenMint.serialize_decode(data)
print(mint)
# {
#     "auth_mint": "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
#     "supply": 0,
#     "decimals": 9,
#     "inited": true,
#     "auth_freeze": "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
#     "extensions": {
#         "metadata_pointer": {
#             "auth": "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
#             "hold": "2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF"
#         },
#         "metadata": [
#             {
#                 "auth_update": "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
#                 "mint": "2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF",
#                 "name": "PXSOL",
#                 "symbol": "PXS",
#                 "uri": "https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json",
#                 "addition": {}
#             }
#         ]
#     }
# }
```

## Interpreting Core Fields

- `auth_mint`: Mint authority. This is the account address authorized to mint (issue) new tokens. It can call on-chain instructions to increase the token supply. In this example, the mint authority is `6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt`.
- `supply`: Current total supply of the token. A value of 0 indicates that no tokens have been minted yet.
- `decimals`: The token's decimal precision, which defines its smallest unit. For example, decimals = 9 means the smallest unit is 1/10⁹ (i.e., 0.000000001). This is similar to the decimals field in Ethereum's ERC-20 tokens.
- `inited`: Indicates whether the mint account has been properly initialized. Only initialized mint accounts can be used in token operations.
- `auth_freeze`: Freeze authority, representing the address that can freeze or unfreeze token accounts. Freezing is useful for compliance or security purposes. In this example, the freeze authority is the same as the mint authority: `6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt`.

## Interpreting Extension Fields

One of the key features of the Token-2022 program is its support for extensions, which are managed under the `extensions` field. In this example, the mint account includes two extensions: `metadata_pointer` and `metadata`.

The `metadata_pointer` extension acts as a pointer to where the token's metadata is stored. The `auth` field specifies who has the authority to modify the pointer, and the `hold` field specifies the account address where the metadata is actually stored. Metadata can be stored within the mint account itself or in a separate account. In practice, however, separating metadata from the mint account is largely for backward compatibility, and it's generally not recommended.

The `metadata` extension stores the actual metadata. Most fields are self-explanatory, such as name, symbol, and uri. One field worth noting is addition, which is a key-value map used to include extra identification details for the token. This helps improve token presentation in wallets and decentralized applications.
