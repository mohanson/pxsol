# Solana/Deploying Your Token on the Mainnet/Deploying Your Token on the Mainnet

Similar to the steps for deploying a token on the local network, we use the following code to deploy the token on the mainnet. Remember to switch the network using `pxsol.config.current = pxsol.config.mainnet`.

```py
import pxsol

# Switch to mainnet.
pxsol.config.current = pxsol.config.mainnet

you = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode('Put your private key here'))
spl = you.spl_create(
    'PXSOL',
    'PXS',
    'https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json',
    9,
)
print(spl) # 6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH
```

You can view the pxs token I just created in the [explorer](https://explorer.solana.com/address/6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH).

![img](../img/project_deploy/explorer.jpg)

After deploying the token, you can mint some initial tokens for yourself, such as 100 million tokens.

```py
import pxsol

pxsol.config.current = pxsol.config.mainnet
you = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode('Put your private key here'))
spl = pxsol.core.PubKey.base58_decode('6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH')
you.spl_mint(spl, you, 100000000 * 10 ** 9)
```

After completing the above steps, you can import your token using a wallet tool to verify if the token has been successfully issued. Open your wallet and check if your token is displayed correctly!

![img](../img/project_deploy/wallet.jpg)
