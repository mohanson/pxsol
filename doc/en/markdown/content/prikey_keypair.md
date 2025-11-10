# Solana/Private Key, Public Key and Address/Keypair

In the Solana ecosystem, a keypair refers to a pair of private and public keys that are used for cryptographic operations. In this article, we will explore how to work with keypairs in Solana.

## Keypair (id.json)

There is a command line wallet implementation in the official Solana distribution, which can be downloaded and installed from the source repository: <https://github.com/anza-xyz/agave>.

After installation, you should find a tool called solana-keygen, which we can use to generate a new wallet:

```sh
$ solana-keygen new
```

The tool generates a new keypair and saves the public and private keys in a json file (usually ~/.config/solana/id.json). You will see something like the following output.

```text
Wrote new keypair to /home/ubuntu/.config/solana/id.json
==============================================================================
pubkey: 6ASf...GWt
==============================================================================
Save this seed phrase and your BIP39 passphrase to recover your new keypair:
smart mutual resist shrimp fever parrot suit kidney public unhappy fringe kiwi
==============================================================================
```

The file contains an array of bytes of length 64. The first 32 bits of the array are the private key, and the last 32 bits are the public key for the private key.

```sh
$ cat ~/.config/solana/id.json

[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 76, 181, 171, 246, 173, 121, 251, 245, 171, 188, 202, 252, 194, 105, 216, 92, 210, 101, 30, 212, 184, 133, 181, 134, 159, 36, 26, 237, 240, 165, 186, 41]
```

Q: What is the private key associated with the above id.json? What is the account address?

A:

```py
import pxsol

idjson = bytearray([
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
    0x4c, 0xb5, 0xab, 0xf6, 0xad, 0x79, 0xfb, 0xf5, 0xab, 0xbc, 0xca, 0xfc, 0xc2, 0x69, 0xd8, 0x5c,
    0xd2, 0x65, 0x1e, 0xd4, 0xb8, 0x85, 0xb5, 0x86, 0x9f, 0x24, 0x1a, 0xed, 0xf0, 0xa5, 0xba, 0x29,
])

prikey = pxsol.core.PriKey(idjson[:32])
pubkey = pxsol.core.PubKey(idjson[32:])
assert prikey.pubkey() == pubkey
print(prikey) # 11111111111111111111111111111112
print(pubkey) # 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
```

## Keypair in Base58

In the solana ecosystem, regular users are likely to make more use of browser wallets, such as the popular phantom wallet. A common feature of these wallets is the ability to import and export private key.

But most of these browser wallets make a mistake: they actually import or export keypair, not private key, even though you see the term private key on the page.

As far as the author has observed in several wallets, when you try to import a "private key", what should be copied into the input box is the base58 representation of the keypair; and the "private key" exported by the wallet is actually the base58 representation of the keypair.

Q: Ming used solana-keygen to generate a new wallet, how should he import the wallet into phantom wallet?

A: Encode the data in ~/.config/solana/id.json file with base58, get the string, and copy it into the "Private Key" box of phantom wallet. The code is as follows.

```py
import pxsol

idjson = bytearray([
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
    0x4c, 0xb5, 0xab, 0xf6, 0xad, 0x79, 0xfb, 0xf5, 0xab, 0xbc, 0xca, 0xfc, 0xc2, 0x69, 0xd8, 0x5c,
    0xd2, 0x65, 0x1e, 0xd4, 0xb8, 0x85, 0xb5, 0x86, 0x9f, 0x24, 0x1a, 0xed, 0xf0, 0xa5, 0xba, 0x29,
])
print(pxsol.base58.encode(idjson)) # 1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA
```

Q: Have a private key `111111111111111111111111111112`, how should I import it into phantom wallet?

A: We generate the keypair from the private key.

```py
import pxsol

prikey = pxsol.core.PriKey.base58_decode('11111111111111111111111111111112')
pubkey = prikey.pubkey()
print(pxsol.base58.encode(prikey.p + pubkey.p))
# 1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA
```

## Keypair in Base64

Solana has historically also had a base64 format for the keypair, which encodes them in base64.

Reminder: encoded in **base64**.

You should be especially wary of this format when using applications in the solana ecosystem. When I was using a solana wallet, I tried several times to import the private key to no avail, so I looked into the source code in a fit of rage and realized that it was encoded in this format.

Fortunately, I have verified that this format was only used on a small scale in the very early days of solana, and it is very difficult to come across it again at this point in time, unless one is an archaeologist.
