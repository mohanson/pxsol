# Solana/Private Key, Public Key and Address/Private Key

Solana is a high-performance blockchain platform that naturally cannot be ignored in terms of security. The privkey is a crucial part used to sign transactions and ensure secure funding. It's a large number, specifically between 0 and 2²⁵⁶ (excluding the latter). In memory, a 32-byte array is typically used to store it.

The privkey identifies a user's all assets. In transactions, through the privkey creation of signatures, it proves that the user has control over the coins, in order to transfer them to others. Therefore, users must always keep their privkeys safe, forgetting a privkey means losing control over one's own coins, and leaking a privkey means sharing coin control with others.

Most modern blockchain wallets, hide operations on privkeys, letting users operate on privkeys themselves, especially for non-tech-savvy users, the result is often disastrous. Modern wallets are more popular using a private key variant called mnemonic words. When you see mnemonic words, you should understand that it's still a privkey at its core.

In our course, if you want to generate your own privkey, the only thing you need to do is generating a 32-byte array. The data in the array can be anything, so it's common practice to find a secure random source to fill the array. Below are some examples of ways to generate Solana privkeys.

**Python**

When using code to generate privkeys, one important point is that you cannot use pseudorandom number generation algorithms. Pseudorandom numbers are reproducible, which makes them unsafe. Instead, you should use cryptography-safe true randomness. Assuming the operation system always provides high-quality, encryption-safe random data, ideally supported by hardware entropy sources, we can use the following code to generate a privkey.

```py
import secrets

prikey = bytearray(secrets.token_bytes(32))
```

**Golang**

```go
package main

import (
    "crypto/rand"
)

func main() {
    prikey := make([]byte, 32)
    rand.Read(prikey)
}
```

**Rust**

```rs
fn main() {
    let mut prikey = [0u8; 32];
    getrandom::fill(&mut prikey).unwrap();
}
```

The privkey is an indispensable part of the Solana ecosystem. Do not use unknown or unverified privkeys, and do not store your privkeys on the internet (e.g., cloud storage or online note-taking tools). By following proper generation and storage procedures, you can effectively manage and protect your digital assets. Always remember: security first!
