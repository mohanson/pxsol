# Solana/Deploying Your Token on the Mainnet/Get Complete Repo from Github

I have packaged the source code and put it on github!

If you are too lazy to follow the code step by step (I understand you), you can go directly to the sample project I prepared. The address is here. Don't thank me unless you want to buy me a cup of milk tea.

I know many developers like coffee.

But for me, milk tea is always the best.

```sh
$ git clone https://github.com/mohanson/pxsol-spl
$ cd pxsol-spl
```

You can deploy the token and airdrop contract on your local development network:

```sh
$ python make.py deploy
# 2025/05/19 11:42:11 main: deploy mana pubkey="344HRAgWWiLuhUWTm9YNKWfhV5fWK26vx45vMxA9HyCE"
```

Generate a random account and send the airdrop:

```sh
$ python make.py genuser
# 2025/05/19 11:45:11 main: random user prikey="Dk5y9WDhMiX83VDPTfojkWgXt6KuBAYhQEgVRAKYGLYG"

$ python make.py --prikey Dk5y9WDhMiX83VDPTfojkWgXt6KuBAYhQEgVRAKYGLYG airdrop
# 2025/05/19 11:45:24 main: request spl airdrop done recv=5.0
```
