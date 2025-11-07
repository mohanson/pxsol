# Solana/Private Key, Public Key and Address/Base58

Base58 is a encoding scheme to convert binary data into human-readable text. It was originally designed by Bitcoin's creator Satoshi Nakamoto for generating Bitcoin addresses and has since been applied to blockchain, cryptocurrency, and other technical fields.

## Base58 Origin

The origin of Base58 can be traced back to 2008 when Satoshi Nakamoto published the Bitcoin whitepaper and began developing the Bitcoin protocol. At that time, he needed a way to convert complex public key hashes into concise, user-friendly strings. Traditional base64 encoding was efficient but included characters that could easily be confused with each other (like 0 and O, I and l) as well as special symbols (+ and /), making it unsuitable for manual input or visual recognition.

To address this issue, Satoshi introduced the Base58 encoding scheme in 2009. He removed 0, O, I, and l from base64's 64 characters and also removed special symbols, defining a new set of 58 characters:

```text
123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
```

In addition, Satoshi introduced an enhanced version with checksums by adding an extra check digit to improve error detection capabilities.

## Base58 Working Principle

The process of encoding with Base58 is similar to converting a number from one base to another:

1. Treat binary data as a large integer.
2. Repeatedly divide the integer by 58, mapping the remainder to characters in the character set.
3. Repeat this process until the quotient becomes 0, generating the final string.

One extra thing to note, however, is that we need to convert every zero byte (0x00) at the beginning of the hexadecimal value to a 1 in base58. Placing a zero at the beginning of a number does not increase its size (e.g. 0x12 is the same as 0x0012), so when we convert to base58, any extra zeros at the beginning will not affect the result. To ensure that leading zeros have an effect on the result, base58 encoding includes a manual step to convert all leading zero byte to 1.

Q: given a hexadecimal string `ef5557e913d5e13e9390a2fb0eeca75d739eccd5249dc174587669db471ca1f2df10d7e17a`, converting it to Base58:

A:

```py
import pxsol

data = bytearray.fromhex('ef5557e913d5e13e9390a2fb0eeca75d739eccd5249dc174587669db471ca1f2df10d7e17a')
print(pxsol.base58.encode(data)) # 92EW9Qnnov7V3QLqToHsFNyEnQ6vvJdYiLgBTfLCv3J5XJjnh1K
```

## Base58 Implementation

You can find a simple Python implementation of Base58 at [pxsol.base58](https://github.com/mohanson/pxsol/blob/master/pxsol/base58.py).

```py
# Copyright (C) 2011 Sam Rushing
# Copyright (C) 2013-2014 The python-bitcoinlib developers
#
# This file is part of python-bitcoinlib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoinlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

# Base58 encoding and decoding

B58_DIGITS = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def encode(b: bytearray) -> str:
    # Encode bytes to a base58-encoded string
    assert isinstance(b, bytearray)
    # Convert big-endian bytes to integer
    n = int.from_bytes(b)
    # Divide that integer into bas58
    res = []
    while n > 0:
        n, r = divmod(n, 58)
        res.append(B58_DIGITS[r])
    res = ''.join(res[::-1])
    # Encode leading zeros as base58 zeros
    czero = 0
    pad = 0
    for c in b:
        if c == czero:
            pad += 1
        else:
            break
    return B58_DIGITS[0] * pad + res


def decode(s: str) -> bytearray:
    # Decode a base58-encoding string, returning bytes.
    if not s:
        return bytearray()
    # Convert the string to an integer
    n = 0
    for c in s:
        n *= 58
        assert c in B58_DIGITS
        digit = B58_DIGITS.index(c)
        n += digit
    # Convert the integer to bytes
    res = bytearray(n.to_bytes(max((n.bit_length() + 7) // 8, 1)))
    # Add padding back.
    pad = 0
    for c in s[:-1]:
        if c == B58_DIGITS[0]:
            pad += 1
        else:
            break
    return bytearray(pad) + res
```
