# Solana/Private Key, Public Key and Address/A Cryptographic Explanation of Private Key (Part 8)

This is a remarkable achievement: we spent eight chapters of time learning about Ed25519. We can be confident that no matter what challenges lie ahead, they will not deter us.

I'd like to discuss the advantages of Ed25519 with you, some of which are obvious, while others are hidden.

The main reason for inventing Ed25519 was to replace the American NIST elliptic curve series. Edwards himself evaluated it as follows:

0. Completely open design, algorithm parameters and choices are straightforward and transparent, without any suspicious points, compared to the currently widely used elliptic curves which use unexplained random seeds to generate their coefficients.
0. High security level, a elliptic curve encryption algorithm may be mathematically secure but is not necessarily so in practice, with high probability of being compromised by caching, timing, or malicious input; Ed25519 series elliptic curves were designed to minimize the probability of errors as much as possible, making it practically the most secure encryption algorithm. For example, any 32-bit random number can be a valid Ed25519 public key, so attacks based on malicious numbers are not possible. The algorithm deliberately avoids certain branches in design time to avoid code execution with different timing for different `if` branches, reducing the probability of such attacks. In contrast, American NIST elliptic curves have a high probability of error in practice and low immunity against theoretical attacks.

From the developer's perspective, Ed25519 has some additional hidden advantages:

0. The signing process of Ed25519 does not rely on a random number generator. Therefore we don't need to assume that there must be an secure random number generator.
0. The private key space of Ed25519 is 0 <= prikey <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, while secp256k1's private key space is 0 <= prikey <= 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141. You can see that Ed25519's private key space is unusual and regular, which can avoid many potential errors.
0. The public key of Ed25519 only has 32 bytes, while the non-compressed representation of secp256k1's public key is 64 bytes and the compressed representation is 33 bytes. There are some hidden benefits in system-level layers. For example, commonly used memory copy functions like memcpy() usually use a special small copy algorithm for byte arrays with length less than or equal to 32; typical examples can be seen in glibc's aarch64 code <https://github.com/bminor/glibc/blob/master/sysdeps/aarch64/memcpy.S>. Some higher-level languages also pay extra attention to such short byte array implementations, such as Rust which only implements clone() and copy() for them.
0. The point group operation on the Ed25519 curve is complete, meaning that for all points in any group, a calculation is performed without needing additional verification for external values, implying that no special point verification is needed during computation.
0. The signing mechanism of Ed25519 itself is not affected by hash collisions.
