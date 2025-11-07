# Solana/Private Key, Public Key and Address/A Cryptographic Explanation of Private Key (Part 2)

Before diving into the private key used in Solana, we first need to understand a concept widely applied in modern information security known as "public-private key cryptography". This is not only the cornerstone for Solana's security but also forms the basis of its operations. Public-private key cryptography, or asymmetric encryption, is an encryption method based on mathematical algorithms that uses two keys: a public key and a private key.

**Public Key**

- The public key is an open key that can be widely distributed. Its main function is to encrypt data or verify signatures.
- With the public key in hand, others can safely encrypt messages or authenticate your data.

**Private Key**

- The private key is a securely held key that you alone possess. Its primary role is to decrypt information or create signatures.
- If someone uses your public key to encrypt a message, only you can use your private key to decode it and read the content.

The mathematical foundation of public-private key cryptography traces back to the 1970s. One of the earliest attempts was the "Diffie-Hellman Key Exchange Protocol" proposed by Diffie and Hellman in 1976, though it didn't gain widespread use at the time. RSA encryption algorithm came into prominence later in 1977, developed by Ron Rivest, Adi Shamir, and Len Adleman, and is considered a classic solution for asymmetric encryption due to its reliance on the difficulty of factoring large prime numbers. Elliptic Curve Cryptography (ECC) emerged as an alternative scheme with the advantage of using shorter key lengths while maintaining equivalent security levels. Its foundation lies in the discrete logarithm problem of elliptic curves.

The development of Bitcoin has significantly popularized certain cryptographic algorithms, including secp256k1 (an elliptic curve used by Bitcoin) and ECDSA (the Elliptic Curve Digital Signature Algorithm). These have had a profound impact globally, with projects like Ethereum and Cash adopting similar cryptographic algorithms. However, Solana takes a different approach in this domain, employing a novel elliptic curve digital signature algorithm known as ed25519, along with the eddsa signature scheme.

We can't help but think, what is the reason for Solana's change? Why is it different from Bitcoin?

To explain the reasons in this regard, in the next few sections, I will lead readers to learn in depth about Bitcoin's secp256k1 + ECDSA signature scheme, and more importantly: the huge security issues hidden behind this scheme.
