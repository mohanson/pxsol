# Solana/More Developer Tools/web3.js Quick Start

We built a simple dApp to show how to use `solana/web3.js` to provide frontend interactions for our on-chain program. You can reference it and adapt it to your own project. The example uses a React + Vite frontend, connects to the Phantom wallet, and reads/writes PDA data via the Pinocchio-based data storage program introduced earlier.

The project lives at <https://github.com/mohanson/pxsol-ss-pinocchio>.

To make learning easier, I've deployed the program on Solana mainnet at `9RctzLPHP58wrnoGCbb5FpFKbmQb6f53i5PsebQZSaQL`. You can test with it directly.

> While deploying, the author made several mistakes and ended up paying ~1.5 SOL in fees (~$300). Please be cautious with mainnet operations to avoid unnecessary losses.

## A Few Personal Notes

I'm not a frontend engineer, I can just about produce a small demo. But I found web3.js has a gentle learning curve: with some frontend basics and a grasp of Solana fundamentals, you can get productive quickly.

Also, modern AI is powerful. I relied heavily on GitHub Copilot and ChatGPT to write the frontend here. These tools can massively boost productivity, but can also produce incorrect code, so you need judgment to correct mistakes. My advice: don't rely on them entirely, combine them with your own understanding and experience.

Below I'll only show the core snippets and a few gotchas. For full details, check the source.

## Establish a Connection

```ts
import { Connection, PublicKey } from '@solana/web3.js'

export const PROGRAM_ID = new PublicKey('9RctzLPHP58wrnoGCbb5FpFKbmQb6f53i5PsebQZSaQL')
export const RPC_ENDPOINT = import.meta.env.VITE_SOLANA_RPC
  || 'https://api.mainnet-beta.solana.com'

export const connection = new Connection(RPC_ENDPOINT, 'confirmed')
```

## Connect to the Phantom Wallet in the Browser

```ts
import type { Transaction } from '@solana/web3.js'

type PhantomProvider = {
  isPhantom?: boolean
  publicKey?: PublicKey
  connect(opts?: { onlyIfTrusted?: boolean }): Promise<{ publicKey: PublicKey }>
  disconnect(): Promise<void>
  signTransaction(tx: Transaction): Promise<Transaction>
}

declare global { interface Window { solana?: PhantomProvider } }

export async function connectPhantom(): Promise<PublicKey> {
  if (!window.solana?.isPhantom) throw new Error('Phantom not found')
  return (await window.solana.connect()).publicKey
}
```

## Derive the Program-Derived Account

The frontend must derive the same PDA seeds as the on-chain program:

```ts
import { PublicKey } from '@solana/web3.js'

export async function deriveDataPda(user: PublicKey): Promise<[PublicKey, number]> {
  return PublicKey.findProgramAddress([user.toBuffer()], PROGRAM_ID)
}
```

## Read Account Data

```ts
import { Connection, PublicKey } from '@solana/web3.js'

export async function fetchUserData(conn: Connection, user: PublicKey): Promise<Uint8Array | null> {
  const [pda] = await deriveDataPda(user)
  const info = await conn.getAccountInfo(pda, { commitment: 'confirmed' })
  return info ? info.data : null
}

export function decodeUtf8(data: Uint8Array | null): string {
  return data ? new TextDecoder().decode(data) : ''
}
```

## Build the Write Instruction

```ts
import { TransactionInstruction, PublicKey, SystemProgram } from '@solana/web3.js'

export async function buildWriteIx(user: PublicKey, payload: Uint8Array): Promise<TransactionInstruction> {
  const [pda] = await deriveDataPda(user)
  return new TransactionInstruction({
    programId: PROGRAM_ID,
    keys: [
      { pubkey: user, isSigner: true, isWritable: true },
      { pubkey: pda, isSigner: false, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    data: payload,
  })
}
```

Note: If you need `Buffer` in your project, use `data: Buffer.from(payload)` and `import { Buffer } from 'buffer'`.

## Send and Confirm a Transaction

```ts
import { Connection, Transaction, TransactionInstruction, PublicKey } from '@solana/web3.js'

type PhantomProvider = { signTransaction(tx: Transaction): Promise<Transaction> }

export async function sendAndConfirm(
  conn: Connection,
  user: PublicKey,
  ix: TransactionInstruction,
  wallet: PhantomProvider,
) {
  const tx = new Transaction().add(ix)
  tx.feePayer = user
  const { blockhash, lastValidBlockHeight } = await conn.getLatestBlockhash('finalized')
  tx.recentBlockhash = blockhash

  const signed = await wallet.signTransaction(tx)
  const sig = await conn.sendRawTransaction(signed.serialize(), { preflightCommitment: 'finalized' })
  await conn.confirmTransaction({ signature: sig, blockhash, lastValidBlockHeight }, 'finalized')
  return sig
}
```

## Run

You can run the frontend project locally:

```sh
$ npm run dev
# Open http://localhost:5173
# Connect Phantom wallet and save/load data.
```

Or directly access our deployed online version: <https://pxsol-ss-pinocchio.vercel.app/>.

First click "connect" to link your wallet, then type any string into the input box and click "save" to write it on-chain. Refresh the page and you should be able to read back the data you saved.

![img](../img/tool_web3/web.jpg)
