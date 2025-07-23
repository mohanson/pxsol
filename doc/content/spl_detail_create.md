# Solana/SPL Token/Instruction Deep Dive (Part 1)

In this lesson, we'll take a deep dive into the `spl_create()` method of the `pxsol.wallet.Wallet` class. This is a high-level interface for creating a new SPL token on the Solana blockchain, complete with metadata, permissions, and rent exemption settings.

## Source Code

> To save you from constantly switching pages, here's the full code we'll be analyzing.

```py
def spl_create(self, name: str, symbol: str, uri: str, decimals: int) -> pxsol.core.PubKey:
    # Create a new token.
    mint_prikey = pxsol.core.PriKey.random()
    mint_pubkey = mint_prikey.pubkey()
    mint_size = pxsol.program.Token.size_extensions_base + pxsol.program.Token.size_extensions_metadata_pointer
    # Helper function to tack on the size of an extension bytes if an account with extensions is exactly the size
    # of a multisig.
    assert mint_size != 355
    addi_size = pxsol.program.Token.size_extensions_metadata + len(name) + len(symbol) + len(uri)
    mint_lamports = pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size + addi_size, {})
    r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
    r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
    r0.account.append(pxsol.core.AccountMeta(mint_pubkey, 3))
    r0.data = pxsol.program.System.create_account(mint_lamports, mint_size, pxsol.program.Token.pubkey)
    r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
    r1.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
    r1.data = pxsol.program.Token.metadata_pointer_extension_initialize(self.pubkey, mint_pubkey)
    r2 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
    r2.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
    r2.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    r2.data = pxsol.program.Token.initialize_mint(decimals, self.pubkey, self.pubkey)
    r3 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
    r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
    r3.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
    r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 0))
    r3.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
    r3.data = pxsol.program.Token.metadata_initialize(name, symbol, uri)
    tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1, r2, r3])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([self.prikey, mint_prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    return mint_pubkey
```

## Breakdown of Implementation

Calling the `spl_create()` method essentially constructs and sends a transaction composed of four on-chain instructions. Each instruction is wrapped in a requisition and executed in sequence as follows.

**Instruction 1: Create Mint Account**

```py
r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
r0.account.append(pxsol.core.AccountMeta(mint_pubkey, 3))
r0.data = pxsol.program.System.create_account(mint_lamports, mint_size, pxsol.program.Token.pubkey)
```

This code allocates a rent-exempt account for the new SPL token. The account size includes both base and extension data. The `mint_lamports` value represents the minimum balance required for rent exemption, retrieved via an RPC call.

**Instruction 2: Initialize Metadata Pointer Extension**

```py
r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
r1.data = pxsol.program.Token.metadata_pointer_extension_initialize(self.pubkey, mint_pubkey)
```

This enables the Token-2022 extension: metadata pointer. It's a Token-2022 feature that allows additional metadata structures to be attached to the mint account. Later instructions will populate this metadata; this one merely declares its existence. Token-2022 actually supports dozens of such extensions, you can learn more [here](https://spl.solana.com/token-2022/extensions).

**Instruction 3: Initialize Mint Account**

```py
r2 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r2.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
r2.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
r2.data = pxsol.program.Token.initialize_mint(decimals, self.pubkey, self.pubkey)
```

This step sets the token's decimal precision and assigns both minting and freezing authority to the creator (typically the publisher). Once this is complete, minting tokens can begin.

**Instruction 4: Initialize Metadata**

```py
r3 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
r3.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 0))
r3.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
r3.data = pxsol.program.Token.metadata_initialize(name, symbol, uri)
```

This instruction writes metadata (name, symbol, URI) directly into the metadata extension field of the mint account.
