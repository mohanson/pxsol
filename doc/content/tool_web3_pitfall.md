# Solana/More Developer Tools/Common Pitfalls and Workarounds in web3.js

Here's a roundup of issues I commonly ran into while developing with solana/web3.js + Phantom and how I resolved them. These are real world problems that took some time to untangle.

## Phantom Wallet's Execution Context

Phantom only works in two contexts:

- `localhost` (both http/https)
- `https` (must be a secure origin)

On a remote non-https domain, Phantom won't inject into the browser environment and you won't be able to connect to the wallet.

## CORS/403 with the Official Public RPC

Directly requesting `https://api.mainnet-beta.solana.com` from the browser often results in 403 or CORS rejection. That's because the official public RPC restricts browser access by default. Two common solutions:

0. Use a provider RPC that allows browser access with an API key (I used Helius).
0. Or configure a reverse proxy on your dev server/backend so the frontend requests a same-origin path.

Example Vite proxy:

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/rpc': {
        target: 'https://your.provider.rpc/solana-mainnet?api-key=XXXX',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
```

Then use a relative endpoint in your frontend:

```ts
const RPC_ENDPOINT = import.meta.env.VITE_SOLANA_RPC || '/rpc'
```

## Transaction Size Limits

Solana transactions have a maximum size of 1232 bytes. After subtracting signatures and overhead, the usable space is even smaller. If you include large payloads, you may hit `Transaction too large`.
