# Solana/Private Key, Public Key and Address/A Cryptographic Explanation of Private Key (Part 4)

## Understanding Bitcoin Signing and Verification

In the digital world, how can we verify someone's identity without revealing their secret key? This has been a major challenge in cryptography. Traditional passwords and certificates are secure but easily cracked. Elliptic Curve Cryptography (ECC), like secp256k1 used by Bitcoin, offers a robust mathematical foundation for establishing trust.

The EDSA (Elliptic Curve Digital Signature Algorithm) signature process involves two main steps: signing and verification.

**Signing Process**

0. Use a hash function (e.g., SHA-256) to convert the message into a fixed-size string of bytes, called the message digest or hash m.
0. Select a random integer from the range [1, n-1], where n is the order of the elliptic curve..
0. Multiply the generator point g by k to get a new point on the curve, and then extract the x-coordinate of this point and label it as r. If r = 0, choose a different k and repeat the process.
0. Compute s = k⁻¹(m + r * prikey) mod n, where k⁻¹ is the modular inverse of k modulo n. If s = 0, choose a different k and repeat the process.
0. The signature consists of the pair (r, s).

**Verification Process**

0. Use the same hash function to compute the message digest m
0. Ensure that both r and s are within the range [1, n-1]. If not, the signature is invalid.
0. Calculate a = m * s⁻¹ mod n, where s⁻¹ is the modular inverse of s modulo n.
0. Calculate b = r * s⁻¹ mod n.
0. Use the values of a and b to compute a new point on the elliptic curve as R = g * a + pubkey * b. If this results in an invalid point (e.g., at infinity), the signature is invalid.
0. Check if the x-coordinate of the recomputed point R matches the original r. If it does, the signature is valid; otherwise, it is invalid.

The article also includes code implementation details for both signing and verification processes. Here’s a simplified version:

```py
import itertools
import random
import typing
import pabtc.secp256k1



def sign(prikey: pabtc.secp256k1.Fr, m: pabtc.secp256k1.Fr) -> typing.Tuple[pabtc.secp256k1.Fr, pabtc.secp256k1.Fr, int]:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.3 Signing Operation
    for _ in itertools.repeat(0):
        k = pabtc.secp256k1.Fr(random.randint(0, pabtc.secp256k1.N - 1))
        R = pabtc.secp256k1.G * k
        r = pabtc.secp256k1.Fr(R.x.x)
        if r.x == 0:
            continue
        s = (m + prikey * r) / k
        if s.x == 0:
            continue
        v = 0
        if R.y.x & 1 == 1:
            v |= 1
        if R.x.x >= pabtc.secp256k1.N:
            v |= 2
        return r, s, v


def verify(pubkey: pabtc.secp256k1.Pt, m: pabtc.secp256k1.Fr, r: pabtc.secp256k1.Fr, s: pabtc.secp256k1.Fr) -> bool:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.4 Verifying Operation
    a = m / s
    b = r / s
    R = pabtc.secp256k1.G * a + pubkey * b
    assert R != pabtc.secp256k1.I
    return r == pabtc.secp256k1.Fr(R.x.x)


def pubkey(m: pabtc.secp256k1.Fr, r: pabtc.secp256k1.Fr, s: pabtc.secp256k1.Fr, v: int) -> pabtc.secp256k1.Pt:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.6 Public Key Recovery Operation
    assert v in [0, 1, 2, 3]
    if v & 2 == 0:
        x = pabtc.secp256k1.Fq(r.x)
    else:
        x = pabtc.secp256k1.Fq(r.x + pabtc.secp256k1.N)
    z = x * x * x + pabtc.secp256k1.A * x + pabtc.secp256k1.B
    y = z ** ((pabtc.secp256k1.P + 1) // 4)
    if v & 1 != y.x & 1:
        y = -y
    R = pabtc.secp256k1.Pt(x, y)
    return (R * s - pabtc.secp256k1.G * m) / r
```

Example: There is a message 0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e, Please sign it using the private key 0x01 and verify the signature.

Answer:

```py
import pabtc

prikey = pabtc.secp256k1.Fr(1)
pubkey = pabtc.secp256k1.G * prikey
m = pabtc.secp256k1.Fr(0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e)

r, s, _ = pabtc.ecdsa.sign(prikey, m)
assert pabtc.ecdsa.verify(pubkey, m, r, s)
```

gain, please remind me of all the code that has appeared in this article. It is now publicly available on GitHub so you can check, refer to, and use it at any time. If you have any questions or need further assistance, please feel free to let me know!

- secp256k1: <https://github.com/mohanson/pabtc/blob/master/pabtc/secp256k1.py>
- ecdsa: <https://github.com/mohanson/pabtc/blob/master/pabtc/ecdsa.py>
