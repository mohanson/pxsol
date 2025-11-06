# Solana/SPL Token/Instruction Deep Dive (Part 2)

In the previous lesson, we learned how to use `spl_create()` to create an SPL token with metadata. In this lesson, we'll dive into another essential operation: how does `spl_mint()` mint tokens and distribute them to a target address (or to yourself)?

## Source Code

> To save you from constantly switching pages, here's the full code we'll be analyzing.

```py
def spl_mint(self, mint: pxsol.core.PubKey, recv: pxsol.core.PubKey, amount: int) -> None:
    # Mint a specified number of tokens and distribute them to self. Note that amount refers to the smallest unit
    # of count, For example, when the decimals of token is 2, you should use 100 to represent 1 token. If the
    # token account does not exist, it will be created automatically.
    recv_ata_pubkey = Wallet.view_only(recv).spl_account(mint)
    r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
    r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
    r0.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
    r0.account.append(pxsol.core.AccountMeta(recv, 0))
    r0.account.append(pxsol.core.AccountMeta(mint, 0))
    r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
    r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
    r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
    r1.account.append(pxsol.core.AccountMeta(mint, 1))
    r1.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
    r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
    r1.data = pxsol.program.Token.mint_to(amount)
    tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([self.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
```

## Breakdown of Implementation

The `spl_mint()` method assembles a transaction consisting of two on-chain instructions.

**Instruction 1: Create Associated Token Account**

```py
r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
r0.account.append(pxsol.core.AccountMeta(recv_account_pubkey, 1))
r0.account.append(pxsol.core.AccountMeta(recv, 0))
r0.account.append(pxsol.core.AccountMeta(mint, 0))
r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
```

This code automatically creates an associated token account for the recipient. The use of `create_idempotent()` ensures that the transaction won't fail even if the account already exists. This is the key difference between `AssociatedTokenAccount.create_idempotent()` and `AssociatedTokenAccount.create()`. You can think of this instruction as:

- If the target associated token account already exists, exit normally.
- If it doesn't exist, create it and exit normally.

> As the name suggests, create_idempotent() is idempotent. In math and computer science, idempotency means that performing the same operation multiple times yields the same result, no side effects from repeated execution.

**Instruction 2: Mint Tokens**

```py
r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(mint, 1))
r1.account.append(pxsol.core.AccountMeta(recv_account_pubkey, 1))
r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
r1.data = pxsol.program.Token.mint_to(amount)
```

This code mints a specified amount of tokens to the recipient's account. Minting requires mint authority, and in the `pxsol.wallet.Wallet` design, the token's mint authority is, by default, the token creator.

Minting increases the total supply of the token.
