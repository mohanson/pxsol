# Solana/Private Key, Public Key and Address/Address Spoofing Attack and Vanity Address

Solana, as a high-performance blockchain platform, has attracted a large number of users and developers due to its fast transactions and low fees. However, with its increasing popularity, the attack methods against users have also become more diverse. Since 2023, a type of "address spoofing transfer attack" has been widely appearing on the network.

## Address Spoofing Attack

The address spoofing attack is a hacking strategy that uses the similarity of addresses to mislead victims. Hackers generate an address with a similar prefix and suffix to the victim's existing address (usually referred to as a "vanity address") and then use this address to send a small amount of coin or assets to the victim.

For example, let's say the victim's wallet address is:

```text
7x9kPqM...XyZ3mN
```

The hacker may generate a vanity address like:

```text
7x9kaA2...QxZ3mN
```

The first two characters and last two characters of the addresses are almost identical, which can easily lead to confusion.

The attack's implementation is very simple. First, hackers use specialized tools to generate large amounts of Solana public-private key pairs until they find an address with a similar prefix and suffix to the target address. Solana addresses are 32-byte base58-encoded public keys, generating addresses with specific patterns requires more computational power but is not impossible. The hacker then sends a small amount of Sol or assets from the spoofed address to the victim, accompanied by a remark like "test transfer" or "refund". When the victim sees this transaction in their wallet, they may mistakenly believe it's coming from their recognized address and attempt to return the funds or unknowingly send large amounts of assets to the spoofed address. The hacker then monitors the blockchain for transactions and quickly transfers the received funds.

This attack has been reported multiple times on the Solana ecosystem, such as in 2023 when some users lost thousands of dollars after receiving small, unverified transfers from unknown addresses. Due to the irreversible nature of Solana transactions, once funds are transferred out, they can almost be impossible to retrieve.

> Carefully verify the full address: Don't rely solely on the first few characters; always check the entire string, especially when sending large amounts.

## Vanity Addresses

We attempted to generate a vanity address using pxsol. Our target was `6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt`, and we aimed to create a public-private key pair that would result in an address with the same prefix and suffix as the victim's address.

Here is the functional script:

```py
import pxsol
import random

target = '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'

for _ in range(1 << 32):
    prikey = pxsol.core.PriKey.random()
    pubkey = prikey.pubkey().base58()
    if pubkey[:2] == target[:2] and pubkey[-2:] == target[-2:]:
        print(prikey)
        print(pubkey)
        break
```

We ran this script on a home computer, spending approximately 6 hours to obtain a private key and public key that satisfied the requirements.

```text
prikey = D44NkELmJ6pQ13qDpA983i82iPDy9yi6VPJ3xRHv3v1R
pubkey = 6Ak9ou3WLs8uxme4vqMyNsUHiyY4inK3wLRtwgCC7uWt
```

Python is not ideal for performance; if you can use libraries like ed25519 in C, Rust, or Go to perform this task, believe me that the speed will be significantly improved by thousands of times.
