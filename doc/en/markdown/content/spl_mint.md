# Solana/SPL Token/Minting Tokens and Querying Balances

In this lesson, we'll talk about minting tokens.

## Minting Tokens and Querying Balances

You can easily mint additional tokens for any user with a simple piece of code. Note: only the token creator has the authority to mint new tokens!

The amount minted via the `spl_mint()` method must take into account the decimal places. For example, if `decimals=9`, then `1000000000` represents 1 full token.

Likewise, when querying your token balance using the `spl_balance()` method, the function returns an array: the first element is the token amount you hold, and the second is the token's decimal precision.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')

ada.spl_mint(spl, ada.pubkey, 100000000 * 10 ** 9)
print(ada.spl_balance(spl)) # [100000000000000000, 9]
```

## Associated Token Account

Just like the Thai Baht Coin program we previously wrote, your tokens are essentially stored in a PDA account. This account is commonly referred to as an Associated Token Account (ATA), a special account for holding and managing SPL tokens on behalf of a user.

- Each ATA uniquely corresponds to a wallet address and a token's mint address.
- It is programmatically generated following deterministic rules, ensuring the same wallet-token pair always derives the same ATA address.
- It stores the token balance of a user.

When you use the `spl_mint()` method from Pxsol to mint tokens, Pxsol will automatically create an ATA for the recipient if it doesn't already exist.

Let's use the RPC interface to query the data stored in an ATA and inspect the result.

```py
import base64
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')
ata = ada.spl_account(spl)

info = pxsol.rpc.get_account_info(ata.base58(), {})
data = base64.b64decode(info['data'][0])
print(data.hex())
```

The returned data is 170 bytes in length. Here's a breakdown of the contents:

```txt
11c447d79a76ef38a896d72fe54b373bab14dcba868425645a1670180e656780 Token Mint Address
4cb5abf6ad79fbf5abbccafcc269d85cd2651ed4b885b5869f241aedf0a5ba29 User Wallet Address
00008a5d78456301                                                 Balance in little-endian, equals 100000000 * 10 ** 9
00000000                                                         Delegate flag: 0 = no delegate set
0000000000000000000000000000000000000000000000000000000000000000 Delegate Address
01                                                               Account state (1 = initialized)
00000000                                                         Native token flag: 0 = non-native (expected)
0000000000000000                                                 Rent exemption amount (if native)
0000000000000000                                                 Delegated amount
00000000                                                         Close authority flag
0000000000000000000000000000000000000000000000000000000000000000 Close authority address
02                                                               Account type (2 = token account)
0700                                                             Token extension (7 = immutable ownership)
0000                                                             Token extension (padding, unused)
```

You can refer to the following source links to deepen your understanding of associated token accounts:

- [Basic Account Types](https://github.com/solana-program/token-2022/blob/a2ddae7f39d6bb182b0595fa3f48e38e94e7c684/program/src/pod.rs#L64-L85)
- [Account Types and Extension Fields](https://github.com/solana-program/token-2022/blob/a2ddae7f39d6bb182b0595fa3f48e38e94e7c684/program/src/extension/mod.rs#L1036-L1137)

In most scenarios, we only care about the first three fields: the token mint address, the user's wallet address, and the token balance.

## Exercise

Q: Is Bob allowed to mint new tokens? Try it with code.

A: No, he can't.

```py
import pxsol

bob = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(2))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')

bob.spl_mint(spl, bob.pubkey, 100000000 * 10 ** 9)
# Exception: {
#     'code': -32002,
#     'message': 'Transaction simulation failed: Attempt to debit an account but found no record of a prior credit.',
#     'data': {
#         'accounts': None,
#         'err': 'AccountNotFound',
#         'innerInstructions': None,
#         'logs': [],
#         'replacementBlockhash': None,
#         'returnData': None,
#         'unitsConsumed': 0
#     }
# }
```
