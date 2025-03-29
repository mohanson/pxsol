# Solana/Transactions/Using Built-in Wallet for Transfers

Pxsol's built-in wallet allows readers to manage Solana accounts directly in Python, by deriving a public key (wallet address) from a private key.

## Creating Your Private Key

To use Pxsol's built-in wallet, you first need a private key object. There are several ways to initialize your private key:

**From Byte Array**

```python
import pxsol

prikey = pxsol.core.PriKey(bytearray([0x00] * 31 + [0x01]))
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

**From Base58 String**

```python
import pxsol

prikey = pxsol.core.PriKey.base58_decode('11111111111111111111111111111112')
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

**From Hex String**

```python
import pxsol

prikey = pxsol.core.PriKey.hex_decode('0000000000000000000000000000000000000000000000000000000000000001')
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

**From Integer**

```python
import pxsol

prikey = pxsol.core.PriKey.int_decode(0x01)
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

**From Keypair (Base58)**

```python
import pxsol

prikey = pxsol.core.PriKey.wif_decode('1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA')
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

All of these methods are equivalent.

## Using Built-in Wallet for Transfers

Pxsol's sub-module `pxsol.wallet` implements a simple but powerful built-in wallet.

Ada is on vacation in Thailand, enjoying a seafood restaurant. He notices that the restaurant allows customers to pay with Solana. Ada decides to try it out and now needs to send 1 SOL to Bob. To achieve this process, Ada first initializes his own wallet using his private key. To complete the transaction, Ada needs to perform two steps:

- Fill in Bob's Solana public key.
- The amount to be sent, expressed in lamports.

```python
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
bob = pxsol.core.PubKey.base58_decode('8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH')
ada.sol_transfer(bob, 1 * pxsol.denomination.sol)
```

> Top secret: Bob's address corresponds to a private key of 0x02.

Running the code, Ada's transaction will be sent to the Solana network, and any errors will be irreversible. Therefore, Ada carefully checks the address and amount, ensuring no mistakes are made. Pxsol's wallet constructs a transaction, gets 1 SOL from Ada's funds and sends it to Bob's address, signed by Ada's private key.

After completing the transaction, Ada checks his own wallet balance.

```python
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
print(f'ada: {ada.sol_balance() / pxsol.denomination.sol} sol')
# ada: 499999998.999995 sol
```

Ada notices that his balance decreases by a small amount compared to 1 SOL, which is the transaction fee.

Solana has unparalleled transaction confirmation speed: typically in seconds after you send a transaction, it will be confirmed. Therefore, Pxsol's built-in wallet uses synchronous transaction confirmation: only when a transaction is confirmed on the network will `sol_transfer()` return.
