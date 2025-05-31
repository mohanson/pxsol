# Solana/Program Development Basics/Get Complete Repo from Github

I have packaged the source code and put it on github!

If you are too lazy to follow the code step by step (I understand you), you can go directly to the sample project I prepared. The address is here. Don't thank me unless you want to buy me a cup of milk tea.

I know many developers like coffee.

But for me, milk tea is always the best.

```sh
$ git clone https://github.com/mohanson/pxsol-ss
$ cd pxsol-ss
```

```sh
$ python make.py deploy
# 2025/05/20 16:06:38 main: deploy program pubkey="T6vZUAQyiFfX6968XoJVmXxpbZwtnKfQbNNBYrcxkcp"
```

Note that the program address will be saved in `res/info.json`, and subsequent operations will directly obtain the program address from this file.

```sh
# Save some data.
$ python make.py save "The quick brown fox jumps over the lazy dog"

# Load data.
$ python make.py load
# The quick brown fox jumps over the lazy dog.

# Save some data and overwrite the old data.
$ python make.py save "片云天共远, 永夜月同孤."
# Load data.
$ python make.py load
# 片云天共远, 永夜月同孤.
```
