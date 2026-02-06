# Solana/Private Key, Public Key and Address/How to Securely Protect Your Private Key

Private keys are the most critical asset credentials in the blockchain world. The phrase "not your keys, not your coins" precisely captures their importance. Once a private key is leaked or lost, your digital assets will be permanently lost or stolen.

Here, I'll briefly discuss private key security, including warnings from real-world cases, cryptographic perspectives, and practical security measures.

## Case Studies

### Trust Wallet Supply Chain Attack

This incident occurred at the end of 2025 and is the first case that comes to mind.

On December 25, 2025, community security analyst akinator issued an alert warning that the Trust Wallet browser extension may have suffered a supply chain attack, advising users not to import seed phrases or use the extension. The tweet claimed that over $2 million had been stolen, with attackers using multiple addresses for fund transfers.

<https://x.com/0xakinator/status/2004273944694587785>

The tweet referenced December 24, 2025, when Trust Wallet Chrome extension v2.68 was released. However, this version had been injected with malicious code, causing seed phrases to be stolen and sent to attackers when users imported them.

By December 27, 2025, losses had escalated to $7 million. Officials subsequently released a statement acknowledging the extension had been compromised and advising users to immediately stop using it. Three days had passed since the attack began, yet losses continued to mount.

What's most shocking about this attack is that victims didn't click on phishing links or download fake apps—they used the extension updated through official channels. In other words, the infrastructure we thought was secure.

**Most systems today rely on complete access to user information: viewing all data, storing all data, and then having users pray that everything will be fine.**

> Reflection: Is storing private keys in wallets truly safe? While this was an attack, it also exposed how users have no defense if the wallet provider decides to act maliciously. This is why I've always believed that private key security is not just a technical issue but also a trust issue.

### Clipboard Attacks

Some malware monitors clipboard content and sends data to remote servers when it detects strings resembling private keys or seed phrases. Even legitimate software often logs clipboard content to files or sends it to remote servers, which can also lead to private key leaks.

There have been numerous reports of such attacks, with similar warnings appearing in the blockchain community at regular intervals.

### New Threat: Coding Agents

A new type of attack is currently trending online: exploiting AI code generation tools (such as GitHub Copilot, Claude, etc.) to steal users' source code, which may contain private keys.

The root cause is similar to the previous example: coding agents have complete access to your code repository, can view and modify all files, and are allowed to access the network or send data over the network. If you use a paid AI service, all contents of your code repository are uploaded to the cloud for processing and storage. In August 2025, GitHub Copilot experienced a data breach where the AI mistakenly leaked responses intended for user A to user B. The root cause was a bug in Google Cloud Platform's proxy infrastructure that caused erroneous routing during request processing. While this incident didn't directly result in private key leaks, it exposed the potential risks of AI services handling user data: your AI service provider can see all your code, including sensitive information.

Related disclosure: <https://docs.cloud.google.com/support/bulletins#gcp-2025-059>.

Even using locally deployed AI isn't completely safe. Suppose you clone a project from GitHub that happens to contain a file meant for AI to read, and the prompts in that file instruct the AI to call curl to upload the user's local files to a specified server. When you open that project in your editor, your configured local AI might automatically execute that command. This vulnerability exploits human trust in AI, and there are currently no effective protective measures.

## Private Key Security from a Cryptographic Perspective

### Private Key Generation

A private key is essentially a random large integer. Taking Solana's ED25519 as an example, a private key is a 256-bit random number ranging from 0 to 2^256 - 1. How large is this number? The number of observable atoms in the universe is approximately 10^80. Brute-forcing a private key is computationally infeasible.

During private key generation, a high-quality random number generator must be used to ensure unpredictability. We typically use hardware entropy sources (such as `/dev/random`) and ensure the generation environment is secure to prevent malware from stealing entropy source data.

If you're simply storing a small amount of funds, using an official wallet to generate private keys is usually secure enough. However, if you hold significant assets, stricter measures are needed. I only recommend one approach: flip a coin 256 times, record heads and tails on an offline computer, then convert the result into a 256-bit number—that's your private key.

> There was once an attack where a well-known wallet application used a low-quality random number generator when generating private keys. Attackers were able to guess all private keys generated within a certain time period.

> There was once an attack where a well-known wallet application's official team intentionally planted malicious code, sending generated private keys to a remote server.

### Private Key Storage

**Paper Wallets**

![img](../img/prikey_security/paper_wallet.jpg)

**Metal Wallets**

![img](../img/prikey_security/metal_wallet.jpg)

Current mainstream cryptographic schemes are secure enough to resist brute-force attacks (considering current technology levels). The real threat to private keys isn't cracking but improper storage.

Modern wallets typically use password-encrypted storage for private keys, with encryption schemes usually choosing AES or ChaCha20, then using key derivation algorithms: PBKDF2, Argon2, Scrypt, etc. Typical encryption workflow:

1. User sets a password.
2. Use KDF (Key Derivation Function) to convert the password into an encryption key.
3. Use the encryption key to encrypt the private key.
4. Store the encrypted key file.

However, this approach also has risks, as the strength of the user-set password becomes the weak link in the entire chain.

1. Weak passwords can theoretically be easily brute-forced. For example, common passwords like `123456` and `qwerty` can be cracked in seconds, leading to private key leaks.
2. However, the computational cost of KDF makes brute-forcing more difficult. The core of this algorithm is to increase the computational cost of password attempts, for example, by performing millions of hash iterations on the input password, making each password attempt take a considerable amount of time.

Regardless, one thing must be ensured: the plaintext of private keys should never appear on publicly networked services, such as online notes or cloud storage. Here are several common private key storage schemes and their pros and cons.

**Off-chain Multi-signature (Naive Version)**

A classic counterexample in the cryptographic community: simply splitting the private key string into several parts and storing them in different locations. For example, splitting a 64-character hexadecimal private key into 4 segments of 16 characters each, storing them in different physical locations (such as home safe, bank safety deposit box, friends' places, etc.). Suppose you want to protect private key e, you might split it like this:

```py
e = "1ec580e8913d9d2874bde4585eba9ae9aca20b80e40c114ec0b230dc4431bd71"

a = "1ec580e8913d9d28"
b = "74bde4585eba9ae9"
c = "aca20b80e40c114e"
d = "c0b230dc4431bd71"
assert a + b + c + d == e
```

This method is widely considered the most insecure practice because it cannot provide true threshold protection. Threshold protection means that only when a certain number of fragments are combined can the complete private key be recovered. With this simple splitting method, if any single fragment is leaked, it's enough for an attacker to obtain partial information and use brute force to try all possible combinations to recover the private key. For example, if an attacker obtains a and b, they only need to try all possible c and d combinations to recover the complete private key. At this point, the attacker only needs to try 2^128 combinations, far less than the 2^256 combinations required to brute-force the entire private key.

Core issue: Partial fragments leak partial information about the private key.

**Off-chain Multi-signature (Elder Version)**

A scheme not recommended by the cryptographic community but relatively secure and simple. The scheme still involves splitting, but instead of simple concatenation, it uses addition operations for protection. Treat the private key you want to protect as a large integer, then randomly generate a batch of large integers such that the sum of all randomly generated large integers modulo a large prime equals the original private key. This way, only when an attacker obtains all fragments can they recover the complete private key. For example, for private key c, you could split it like this:

```py
import pabtc

c = 0xf108bf1b32f3eb50da02419afe6caee4f8385fe7df364f8af27e05757ba2ad04

a = 0x01d487c418d34e79760f835f8fb7309d3b0c6a0ab32f7bca2eebb7090bb1e9d3
b = 0xef3437571a209cd763f2be3b6eb57e47bd2bf5dd2c06d3c0c3924e6c6ff0c331
assert (a + b) % pabtc.secp256k1.N == c
```

With this method, even if fragment a or b is leaked, no information about the complete private key c is revealed, because an attacker cannot deduce the value of c from only a or b. However, the drawback of this method is that all fragments must be carefully stored; if any fragment is lost, the complete private key cannot be recovered.

**Off-chain Threshold Signature (Shamir's Secret Sharing)**

A scheme widely discussed in the Bitcoin community and my personal recommendation. This scheme is based on Shamir's Secret Sharing (SSS) algorithm, which allows a private key to be split into n fragments and sets a threshold k, where the complete private key can only be recovered when at least k fragments are combined. This way, even if an attacker obtains fewer than k fragments, they cannot recover the complete private key. Its advantage is avoiding single points of failure: even if a fragment is lost, as long as the remaining number of fragments reaches the threshold k, the complete private key can still be recovered.

Common splitting methods are 2-of-3, 3-of-5, etc. For example, in a 3-of-5 scheme, the private key is split into 5 fragments, and any 3 fragments can be combined to recover the complete private key.

Related reading: <https://en.wikipedia.org/wiki/Shamir%27s_secret_sharing>

Brief introduction to the algorithm principle:

0. k points on a plane can uniquely determine a curve of degree k-1. Treat the private key secret as a point at `(0, secret)`, then randomly generate `k - 1` random points to determine a curve on the plane.
1. Randomly select n points on the curve that do not include `(0, secret)`, and save the coordinates of these points as fragments.
2. When you need to recover the private key, simply substitute the coordinates of any k fragments into the Lagrange interpolation formula to recover the original polynomial, then substitute x=0 to obtain the private key secret. This is a simple k-of-n threshold scheme.

Advantages:

- The algorithm is open-source with widespread application and research support. Additionally, you don't need to depend on specific software or third-party libraries to implement the algorithm; any skilled programmer can implement the code based on the public algorithm.
- Even if all fragments are leaked, attackers may not necessarily know you're using the SSS algorithm to protect your private key. They might think these fragments are multiple private keys, increasing the difficulty of the attacker's guessing. You can even actually use the fragments as private keys, storing small amounts of funds in them to create a honeypot deception layer. Attackers might be attracted to these small funds and overlook the real private key. Once an attacker transfers funds from a fragment, you'll receive an early warning: one of your fragments has been leaked.

**Summary**

Two principles:

1. The plaintext of private keys should never appear on networked devices. You should write it on paper or engrave it on a metal plate.
2. Use some method to split the private key into multiple parts and store these parts according to the first principle.

## Quantum Attacks

The emergence of quantum computers poses a threat to existing public key cryptography. For example, Shor's algorithm can crack encryption algorithms based on integer factorization and discrete logarithm problems in polynomial time. The ECDSA used by Bitcoin and Ethereum and the ED25519 used by Solana are both based on discrete logarithm problems, which happen to be within Shor's algorithm's attack range.

The Bitcoin community has begun discussing the adoption of quantum-resistant signature algorithms, but there is currently no widely supported solution. For Bitcoin users, the current best practice is to create a new address to receive funds and never use this address to sign any transactions. This way, even if quantum computers emerge, they cannot crack this address's private key. The principle behind this is that for Bitcoin, signing transactions exposes the public key, and quantum computers can use the public key to crack the private key. As long as no transactions are signed, the public key won't be exposed, and thus the private key won't be cracked.

For Solana users, there is currently no clear quantum-resistant solution, nor can they adopt Bitcoin's approach because Solana's address is the public key itself. Therefore, Solana users need to more closely monitor quantum computer development dynamics.

True practical quantum computers may still require several years, according to Google researchers, 5 to 10 years. We must face the threat of quantum computers now. It's not something that will only happen in the distant future.
