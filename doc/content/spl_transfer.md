# Solana/SPL Token/Transfers

Solana is the ultimate engine for token movement in the blockchain world. With its lightning-fast transaction finality and near-zero fees, token transfers on Solana are as smooth as silk.

## Transfers

You can use `spl_transfer()` to send any SPL token to any user. Just be sure to account for the token's decimal precision. This function will automatically check if the recipient has an associated token account (ATA); if not, it will create one on their behalf.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
bob = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(2))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')

print(ada.spl_balance(spl)) # [100000000000000000, 9]
ada.spl_transfer(spl, bob.pubkey, 100 * 10 ** 9)
print(ada.spl_balance(spl)) # [99999900000000000, 9]
print(bob.spl_balance(spl)) # [100000000000, 9]
```

## Become the Airdrop King

On the Solana network, you'll often find strangers sending you SPL tokens. This practice, commonly known as an "airdrop", involves distributing tokens freely to specific or random wallet addresses. Airdrops are popular among projects or individuals in ecosystems like Solana and Ethereum to promote awareness or boost token circulation.

> Airdrops are especially common in meme coin projects. Some retail traders gauge a token's activity or potential by the number of holders. Projects use airdrops to quickly inflate that number.

Q: Airdrop your token to 1,000 random addresses and become the Airdrop King!

A:

```py
import pxsol
import random

pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')

for _ in range(1000):
    dst = pxsol.core.PriKey.random().pubkey()
    ada.spl_transfer(spl, dst, 100 * 10 ** 9)
```
