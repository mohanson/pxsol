# Solana/More Developer Tools/The Anchor Testing Framework

The moment you write your first line of contract code, testing is the first thing it asks for. We want it to feel smooth at the framework level while still standing rigorous at the protocol level. Think of testing here as a short trip: first, we take the well-paved highway using Anchor's built-in TypeScript testing; then we hike a raw path using Python pxsol (constructing transaction bytes directly per protocol).

The goal is straightforward: on a local chain, initialize a data store, update it multiple times, then read it back to verify the data matches. All code lives under the repo's `tests/` directory.

## TypeScript

This path is the most ergonomic. You tell Anchor: which program, which instruction, what accounts and arguments. Anchor and the IDL handle encoding/decoding and account validation for you.

> Anchor's IDL is generated automatically when you first build the program. It records the program ID, each instruction's accounts and parameters, and the data structures of each account. Think of it as the bridge between your on-chain program and off-chain clients.

Our test does one `init` followed by two `update`s, each time with a different payload length. After each call, we fetch the account's data and assert correctness.

```ts
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PxsolSsAnchor } from "../target/types/pxsol_ss_anchor";

describe("pxsol-ss-anchor", () => {
  // Configure the client to use the local cluster.
  anchor.setProvider(anchor.AnchorProvider.env());
  const program = anchor.workspace.pxsolSsAnchor as Program<PxsolSsAnchor>;
  const provider = anchor.getProvider() as anchor.AnchorProvider;
  const wallet = provider.wallet as anchor.Wallet;
  const walletPda = anchor.web3.PublicKey.findProgramAddressSync(
    [Buffer.from("data"), wallet.publicKey.toBuffer()],
    program.programId
  )[0];

  it("Init with content and then update (grow and shrink)", async () => {
    // Airdrop SOL to fresh authority to fund rent and tx fees
    await provider.connection.confirmTransaction(await provider.connection.requestAirdrop(
      wallet.publicKey,
      2 * anchor.web3.LAMPORTS_PER_SOL
    ), "confirmed");

    const poemInitial = Buffer.from("");
    const poemEnglish = Buffer.from("The quick brown fox jumps over the lazy dog");
    const poemChinese = Buffer.from("片云天共远, 永夜月同孤.");
    const walletPdaData = async (): Promise<Buffer<ArrayBuffer>> => {
      let walletPdaData = await program.account.data.fetch(walletPda);
      return Buffer.from(walletPdaData.data);
    }

    await program.methods
      .init()
      .accounts({
        user: wallet.publicKey,
        userPda: walletPda,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([wallet.payer])
      .rpc();
    if (!(await walletPdaData()).equals(poemInitial)) throw new Error("mismatch");

    await program.methods
      .update(poemEnglish)
      .accounts({
        user: wallet.publicKey,
        userPda: walletPda,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([wallet.payer])
      .rpc();
    if (!(await walletPdaData()).equals(poemEnglish)) throw new Error("mismatch");

    await program.methods
      .update(poemChinese)
      .accounts({
        user: wallet.publicKey,
        userPda: walletPda,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([wallet.payer])
      .rpc();
    if (!(await walletPdaData()).equals(poemChinese)) throw new Error("mismatch");
  });
});
```

Run it:

```bash
# Automatically builds, deploys to the local cluster, and runs the TS tests
$ anchor test
```

## Python Pxsol

This path is closer to the protocol itself. We'll manually assemble the account metas, splice in the 8-byte method discriminators, then append a 4-byte little-endian length and raw bytes. It's suitable for cross-language integration or verifying each step in environments without an Anchor client.

Here's the code:

```py
import argparse
import base64
import pxsol


parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, default='11111111111111111111111111111112')
parser.add_argument('args', nargs='+')
args = parser.parse_args()

user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(args.prikey))
prog_pubkey = pxsol.core.PubKey.base58_decode('GS5XPyzsXRec4sQzxJSpeDYHaTnZyYt5BtpeNXYuH1SM')
data_pubkey = prog_pubkey.derive_pda(b'data' + user.pubkey.p)


def init():
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.data = bytearray().join([
        bytearray([220, 59, 207, 236, 108, 250, 47, 100]),
    ])
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


def update():
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.data = bytearray().join([
        bytearray([219, 200, 88, 176, 158, 63, 253, 127]),
        len(args.args[1].encode()).to_bytes(4, 'little'),
        args.args[1].encode(),
    ])
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


def load():
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    print(base64.b64decode(info['data'][0])[8 + 32 + 1 + 4:].decode())


if __name__ == '__main__':
    eval(f'{args.args[0]}()')
```

Run:

```bash
$ solana-test-validator -l /tmp/solana-ledger
$ anchor deploy
# Program Id: GS5XPyzsXRec4sQzxJSpeDYHaTnZyYt5BtpeNXYuH1SM

$ python tests/pxsol-ss-anchor.py update "The quick brown fox jumps over the lazy dog"
$ python tests/pxsol-ss-anchor.py load
# The quick brown fox jumps over the lazy dog

$ python tests/pxsol-ss-anchor.py update "片云天共远, 永夜月同孤."
$ python tests/pxsol-ss-anchor.py load
# 片云天共远, 永夜月同孤.
```
