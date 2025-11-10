# Solana/SPL Token/Instruction Deep Dive (Part 3)

This section takes you deep into the on-chain logic behind SPL token transfers, helping you master the correct way to securely and automatically transfer SPL tokens on Solana. The `spl_transfer()` method primarily does two things:

- Ensures the recipient's associated token account exists. If it doesn't, it creates one automatically.
- Transfers the specified amount of tokens from the sender's associated token account to the recipient's.

## Source Code

> To save you from constantly switching pages, here's the full code we'll be analyzing.

```py
def spl_transfer(self, mint: pxsol.core.PubKey, recv: pxsol.core.PubKey, amount: int) -> None:
    # Transfers tokens to the target. Note that amount refers to the smallest unit of count, For example, when the
    # decimals of token is 2, you should use 100 to represent 1 token. If the token account does not exist, it will
    # be created automatically.
    self_ata_pubkey = self.spl_account(mint)
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
    r1.account.append(pxsol.core.AccountMeta(self_ata_pubkey, 1))
    r1.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
    r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
    r1.data = pxsol.program.Token.transfer(amount)
    tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([self.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
```

## Breakdown of Implementation

The `spl_transfer()` method assembles and sends a transaction that contains two on-chain instructions.

**Instruction 1: Create Associated Token Account**

```py
r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
r0.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
r0.account.append(pxsol.core.AccountMeta(recv, 0))
r0.account.append(pxsol.core.AccountMeta(mint, 0))
r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
```

This code serves the same purpose and function as the first instruction in `spl_mint()`, ensuring the recipient's associated token account exists.

**Instruction 2: Transfer Tokens**

```py
r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(self_ata_pubkey, 1))
r1.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
r1.data = pxsol.program.Token.transfer(amount)
```

This code transfers the specified amount of tokens from the sender's account to the recipient's account. The transfer is ultimately verified and accounted for by the Token-2022 program, which updates both parties' balances accordingly.
