# Solana/Thai Baht Coin/Get Complete Repo from Github

I have packaged the source code and put it on github!

If you are too lazy to follow the code step by step (I understand you), you can go directly to the sample project I prepared. The address is here. Don't thank me unless you want to buy me a cup of milk tea.

I know many developers like coffee.

But for me, milk tea is always the best.

> Sometimes life is like a novel, it always has to give us some déjà vu surprises.

```sh
$ git clone https://github.com/mohanson/pxsol-thaibaht
$ cd pxsol-thaibaht
```

```sh
$ python make.py deploy
# 2025/05/20 16:06:38 main: deploy program pubkey="9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q"
```

Note that the program address will be saved in `res/info.json`, and subsequent operations will directly obtain the program address from this file.

```sh
# Mint 21000000 Thai Baht for Ada
$ python make.py mint 21000000

# Show ada's balance
$ python make.py balance 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
# 21000000

# Transfer 100 Thai Baht to Bob
$ python make.py transfer 100 8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH

# Show ada's balance
$ python make.py balance 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
# 20999900
# Show bob's balance
$ python make.py balance 8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH
# 100
```
