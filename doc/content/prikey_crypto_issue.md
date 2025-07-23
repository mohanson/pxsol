# Solana/Private Key, Public Key and Address/A Cryptographic Explanation of Private Key (Part 5)

Secp256k1 and ECDSA signing algorithms are now widely used in many systems. I know that elliptic curves have an advantage in cryptography because they can provide higher security at smaller key lengths. However, are they truly secure and perfect algorithms?

From recent news, it seems that they have some issues. The United States National Institute of Standards and Technology (NIST) has found some security risks in secp256k1 and no longer recommends its use. Instead, NIST suggests using another elliptic curve called secp256r1 as an alternative. On the other hand, Bitcoin itself is changing, introducing a signature algorithm called Schnorr in 2021 to try to replace ECDSA.

The underlying reason for these changes is due to problems with the ECDSA signing algorithm itself. It is extremely vulnerable to attacks and has caused many disastrous consequences. In this section, I will lead you through history and attempt to reenact those famous attacks.

## Random Number Reuse Attack

Because of Bitcoin's reasons, secp256k1 elliptic curves and ECDSA signature algorithms have become widely known. However, they were not unknown before Bitcoin. For example, in the PlayStation 3 era, Sony used a private key stored on their company premises to mark their PlayStation firmware as valid and unmodified. All they needed was one public key to verify if the signature came from Sony.

Unfortunately for Sony, their poor code implementation made them vulnerable to hackers, who could easily decrypt any system updates published by Sony in the future.

At the fail0verflow conference, a hacker demonstrated part of Sony's ECDSA code and found that they always kept the random number value at 4. This meant that the private key k in the ECDSA signing step would always get the same value. ECDSA signature requires a strictly random private key k; if you reuse k, it directly leads to private key exposure. This attack is not difficult, so let's challenge ourselves!

```py
def get_random_number():
  # Chosen by fair dice roll. Guaranteed to be random.
  return 4
```

Q: Given the following information, find the private key.

- Information m₁ and its signature (r₁, s₁).
- Information m₂ and its signature (r₂, s₂).
- Both m₁ and m₂ are signed using the same random number k, but k is unknown.

A:

```txt
s₁ = (m₁ + prikey * r₁) / k
s₂ = (m₂ + prikey * r₂) / k = (m₂ + prikey * r₁) / k
s₁ / s₂ = (m₁ + prikey * r₁) / (m₂ + prikey * r₁)
prikey = (s₁ * m₂ - s₂ * m₁) / (s₂ - s₁) / r₁
```

Here is a practical example to help everyone better understand how to recover the private key using two signatures that were generated with the same random number k:

```py
import pabtc

m1 = pabtc.secp256k1.Fr(0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e)
r1 = pabtc.secp256k1.Fr(0x741a1cc1db8aa02cff2e695905ed866e4e1f1e19b10e2b448bf01d4ef3cbd8ed)
s1 = pabtc.secp256k1.Fr(0x2222017d7d4b9886a19fe8da9234032e5e8dc5b5b1f27517b03ac8e1dd573c78)

m2 = pabtc.secp256k1.Fr(0x059aa1e67abe518ea1e09587f828264119e3cdae0b8fcaedb542d8c287c3d420)
r2 = pabtc.secp256k1.Fr(0x741a1cc1db8aa02cff2e695905ed866e4e1f1e19b10e2b448bf01d4ef3cbd8ed)
s2 = pabtc.secp256k1.Fr(0x5c907cdd9ac36fdaf4af60e2ccfb1469c7281c30eb219eca3eddf1f0ad804655)

prikey = (s1 * m2 - s2 * m1) / (s2 - s1) / r1
assert prikey.x == 0x5f6717883bef25f45a129c11fcac1567d74bda5a9ad4cbffc8203c0da2a1473c
```

## Invalid Curve Attacks

Invalid Curve Attacks refer to attacks where attackers generate a point that is not part of the standard curve, thereby circumventing signature verification, key generation, or other operations based on the curve.

During the signing process, attackers may construct an invalid public key in some way. This invalid public key has a mathematical relationship with the attacker's private key (for example, through forging an invalid public key during the signing process). This allows the attacker to produce a signature that appears valid. Normally, the verification algorithm checks whether the public key is within the valid range of the secp256k1 curve. If the public key is invalid, the system should reject the signature. However, if the system does not adequately check the validity of the elliptic curve points, an attacker may submit a request containing an invalid public key and a forged signature. In some cases, the system may erroneously accept this invalid signature as valid, leading to fraudulent transactions or operations being incorrectly deemed valid, enabling improper actions such as transferring funds or altering data.

A real-world example is the elliptic curve validation vulnerability in OpenSSL. In 2015, a version of OpenSSL (before 1.0.2) had an elliptic curve validation vulnerability (CVE-2015-1786). Attackers could exploit this by constructing an invalid elliptic curve point and using it as the public key to bypass verification through certain vulnerabilities in OpenSSL, subsequently attacking systems that use the library. Similar issues had occurred in the ecdsa library used by Bitcoin core, with earlier versions failing to adequately validate elliptic curve points.

Before the vulnerability was patched, attackers could exploit this issue to circumvent the system's validation of elliptic curve point validity, potentially causing rejection services or other security problems.

## Transaction Malleability Attack

Mt.Gox was once the world's largest Bitcoin exchange, headquartered in Tokyo and accounting for approximately 70% of global Bitcoin trading volume in 2013. In 2014, Mt.Gox suffered a major cyberattack that resulted in the loss of about 850,000 Bitcoin. During this incident, hackers employed what is known as a transaction malleability attack.

The specifics of the attack are as follows: Attackers initiated a withdrawal transaction "a" on Mt.Gox before it was confirmed. They then altered the transaction signature during the confirmation process to change the transaction hash value for a new transaction "b". Once transaction "b" was successfully confirmed by the blockchain, Mt.Gox mistakenly received notification that the withdrawal had failed and rescheduled a new withdrawal transaction in response.

To make this attack successful, the key requirement is that attackers must be able to modify certain parts of the signature (e.g., the input signature) or other non-critical fields while still maintaining the validity of the signature. This would allow them to alter the hash value of a transaction without altering its actual content.

Interestingly, when using the secp256k1 elliptic curve cryptography and ECDSA signature scheme, there exists an extremely convenient method that enables attackers to modify signature results while still passing the signature verification process. The ECDSA signing algorithm verifies a signature based on specific parameters. One important characteristic of this process is that it does not depend on the sign value "s" in any significant way. Below is an example script written in Python to demonstrate this concept:

```py
import pabtc

prikey = pabtc.secp256k1.Fr(1)
pubkey = pabtc.secp256k1.G * prikey
msg = pabtc.secp256k1.Fr(0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e)

r, s, _ = pabtc.ecdsa.sign(prikey, msg)
assert pabtc.ecdsa.verify(pubkey, msg, r, +s)
assert pabtc.ecdsa.verify(pubkey, msg, r, -s)
```

In the code above, we used a private key to sign a message and then took the negative value of the s in the signature. The modified signature still passes the ECDSA verification.

In early versions of Bitcoin, such an attack posed a risk. Attackers exploited this vulnerability by extending the transaction to break its **unforgeability**, leading to significant security issues. To address this problem, Bitcoin improved its handling during the segregated witness (segwit) upgrade. Segwit separated the signed part of the transaction from other data, ensuring that even if attackers modified the signature, the transaction hash remained unaffected and the extension issue was resolved.

This kind of issue also exists in other blockchain systems, prompting many projects to adopt similar solutions like segwit to ensure the integrity and traceability of transactions. Another solution is Ethereum's approach, where the s value in the signature is subjected to additional requirements: s must be less than `pabtc.secp256k1.N / 2` (see Appendix F. Signing Transactions in [Ethereum Yellow Paper](https://ethereum.github.io/yellowpaper/paper.pdf) for a detailed explanation of Ethereum's solution to the transaction extendability attack).

> In ancient times, if we knocked a gold coin into shape, although the shape changed, the quality did not change. In the market transaction, it would still be recognized as a gold coin. Even if you knocked the gold coin into a gold nugget, it would still be recognized. This characteristic is called "malleability" or "forgeability".

有诗云(This is a Chinese doggerel):

门头交易所, 用户真是多. (The Mt.Gox exchange has so many users)

比特币被盗, 大伙冷汗冒, (Bitcoins were stolen, and everyone was sweating)

黑客改哈希, 交易无踪兆, (Hackers changed the hash, and the transaction disappeared without a trace)

冷钱包空空, 财富随风飘. (The cold wallet was empty, and the wealth was blown away by the wind)

## Side-channel attack

I flew next to a big brother has been watching the stock, we talked a few stock. He said the market was bad this year, and asked me to guess how much he'd lost.

I said: "Just about a hundred thousand yuan." Brother froze, asked me: "How did you guess it?"

I said although you are wearing a shirt and pants, look very business, but your clothes are very ordinary, that means the income is very common.

Your shirt is old, but it's ironed properly, and the collar is clean, which your wife cleaned up for you. You have a little hellokitty charm on your bag, which your daughter must have hung for you.

Your stock picks are all 5G mobile chip stocks, you think you know a lot about it, you should be working in an Internet company. All things considered, your disposable capital is only 200-300 thousand yuan, combined with this year's market, a loss of about a hundred thousand yuan. And look at your dark circles under your eyes and thin hair in proportion to your age, it's a lot of pressure.

Your wife probably doesn't know you've lost so much money in stocks. I just saw that you have a cryptocurrency exchange app on your cell phone, last on the list, which means it's a recent download.

If you lose more money in stocks, you're going to go into cryptocurrency coins, but you're only going to lose more money. After that I clicked on his cell phone speculation software interface, it shows that the total investment of 280,000, the current loss of 102,000.

Brother silent, never said a word to me on the way, just occasionally look down with the index finger joints to rub a slightly red eyes, the airplane meal box lunch opened, but did not eat.

The above story is from the Chinese Internet, first appeared in 2015, and has been republished so many times that its author is unknown. In this story, "I" launched a side-channel attack on big brother". Although big brother did not disclose any information about his investments to me, since big brother's return on assets affects what big brother wears, we can reverse engineer big brother's return on assets by what big brother wears.

In the field of cryptography, **side-channel attacks** are techniques that exploit information gained from the physical or behavioral characteristics of a device during the execution of cryptographic operations. These attacks can include analyzing factors such as execution time, power consumption patterns, and electromagnetic radiation.

In Ecdsa, the signature process involves generating a random number k, which is then used to compute part of the signature. The security of this random number is crucial, as it allows an attacker to recover the private key if k is compromised.

Q: For the following information, please calculate the private key for secp256k1.

- `m = 0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e`
- `k = 0x1058387903e128125f2715d7de954f53686172b78c3f919521ae4664f30b00ca`
- `r = 0x75ee776c554b1dd5e1680a4cc9a3d0e8cb11400742d8af0222ce383e642f98db`
- `s = 0x35fd48c9157256558184e20c9392ff3c9517f9753e3745aede06cab285f4bc0d`

A: According to the ecdsa signature algorithm, it is easy to get the formula for calculating the private key as `prikey = (s * k - m) / r`, and substituting it into the numerical calculation, we get the private key as 1. The authentication code is as follows:

```py
import pabtc

m = pabtc.secp256k1.Fr(0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e)
k = pabtc.secp256k1.Fr(0x1058387903e128125f2715d7de954f53686172b78c3f919521ae4664f30b00ca)
r = pabtc.secp256k1.Fr(0x75ee776c554b1dd5e1680a4cc9a3d0e8cb11400742d8af0222ce383e642f98db)
s = pabtc.secp256k1.Fr(0x35fd48c9157256558184e20c9392ff3c9517f9753e3745aede06cab285f4bc0d)

prikey = (s * k - m) / r
assert prikey == pabtc.secp256k1.Fr(1)
```

The computation of a random number k involves elliptic curve dot product and inverse element operations (usually implemented by extending Euclid's algorithm). The time of these operations can be correlated with k, and a bypass attacker can measure the difference in execution time to extract k. To reveal the principle, I will try to simplify the attack.

Q: There is an unknown random number k, and now a hacker can somehow detect the execution time of g * k. Try to find out if it is possible to get some information about the random number k.

A: Looking at the multiplication algorithm for points on an elliptic curve, we can see that different operations are performed when the bits of k are different. When the bit is 0, it is less computationally intensive than when the bit is 1. We take two different values of k, one with a majority of 0 and the other with a majority of 1, and calculate the difference between their execution times. When a new unknown k is computed, its execution time is detected and compared with the previous two values to approximate the number of unknown k's with bit 1. The experimental code is as follows. Note that in order to simplify the attack, we assume in the experimental code that the first bit of all the k's involved in the computation is always 1.

```py
import pabtc
import secrets
import timeit

k_one = pabtc.secp256k1.Fr(0x8000000000000000000000000000000000000000000000000000000000000000)  # Has one '1' bits
k_255 = pabtc.secp256k1.Fr(0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff)  # Has 255 '1' bits
k_unknown = pabtc.secp256k1.Fr(max(1, secrets.randbelow(pabtc.secp256k1.N)) | k_one.x)  # The unknown k

a = timeit.timeit(lambda: pabtc.secp256k1.G * k_one, number=1024)
b = timeit.timeit(lambda: pabtc.secp256k1.G * k_255, number=1024)
c = timeit.timeit(lambda: pabtc.secp256k1.G * k_unknown, number=1024)

d = (c - a) / ((b - a) / 254)
print(d)
```

The above attack process is a timing attacks in bypass attacks, if you want to protect against this attack, you can introduce constant-time operations in the code to avoid leaking information. For example, using fixed-time addition and multiplication prevents time differences from being exploited. As an after-class exercise, we hope that you will try to modify the implementation of the multiplication algorithm on elliptic curves to avoid the time attack mentioned above.

In practical applications, in order to avoid side-channel attacks in cryptographic algorithms, it is necessary to make multiple security optimizations at the algorithm, hardware, and software levels. However, since the secp256k1 and ecdsa schemes did not fully consider this attack method when they were designed, it is very difficult and complicated to protect against such attacks.

## Summary

In conclusion, although secp256k1 and ecdsa are widely used in many applications and are quite secure when implemented and used correctly, their potential vulnerabilities cannot be ignored. Thanks to the growth of Bitcoin, secp256k1 and ecdsa have gained notoriety and attracted more cryptographers and unsuspecting hackers. In the future, more attacks on sepc256k1 may be discovered and exploited. Therefore, it is important to be vigilant, up-to-date and follow the latest security best practices to ensure the security of your system. As the field of cryptography continues to advance, more secure and efficient alternatives are available, but it is still the responsibility and challenge of every developer to understand and address the current risks.
