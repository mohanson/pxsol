# Solana/Account Model/Data Accounts

On the Solana network, a program's executable code and its state are stored in separate accounts. This is similar to how operating systems typically separate programs and their data into different files.

If a stateful program wants to "settle down" on-chain, it needs a place to store its variables, state, or configuration data.

However, on Solana, a program cannot create data accounts by itself. Instead, it must rely on the transaction sender (i.e., the caller) to pre-sign and request the creation of a data account via a program instruction. The system program carries out the creation, and the ownership of the newly created data account must be assigned to your custom program. That way, your program can write to, update, or delete the data stored in the account.

## How to Manually Create a Data Account

If you're planning to create a data account, you need to define three things in advance:

- Who will own the data account (i.e., which program)?
- How much space should be allocated (i.e., how many bytes of data will be stored)?
- What should be the initial balance of the account?

To create an account, you'll use the `create_account` instruction from the Solana system program. Here's a simple example to demonstrate:

Q: Create a new random account with the following requirements:

- The owner is the system program (`11111111111111111111111111111111`).
- The data account should have 64 bytes of space.
- The initial balance is 1 SOL.

A: Code as follows:

```py
import base64
import json
import pxsol
import random

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
tmp = pxsol.wallet.Wallet(pxsol.core.PriKey.random())

rq = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
rq.account.append(pxsol.core.AccountMeta(ada.pubkey, 3)) # Funding account
rq.account.append(pxsol.core.AccountMeta(tmp.pubkey, 3)) # The new account
rq.data = pxsol.program.System.create_account(
    pxsol.denomination.sol, # Initial lamports
    64, # Data size for the new account
    pxsol.program.System.pubkey # Owner
)

tx = pxsol.core.Transaction.requisition_decode(ada.pubkey, [rq])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([ada.prikey, tmp.prikey])
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
pxsol.rpc.wait([txid]) # Waiting for the transaction to be processed

r = pxsol.rpc.get_account_info(tmp.pubkey.base58(), {})
print(json.dumps(r, indent=4))
# {
#     "data": [
#         "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==",
#         "base64"
#     ],
#     "executable": false,
#     "lamports": 1000000000,
#     "owner": "11111111111111111111111111111111",
#     "rentEpoch": 18446744073709551615,
#     "space": 64
# }
```

## Ada and the "Thai Baht Coin" Dilemma

Ada had a lovely vacation, though not without a minor annoyance.

While she could pay for food and entertainment with SOL, prices in the real world are usually denominated in fiat currency. So, each time she paid for something, she had to look up the current exchange rate for SOL to decide how much to send.

To simplify this, she wrote a program on Solana called "Thai Baht Coin". It's not a real token, but the program can record how much "Thai Baht Coin" each user owns.

She deployed the program and then created a data account using her own wallet to store her Thai Baht Coin balance. For instance, she created an account with the address `ThbAdaBalance111...`, which is controlled by her program (i.e., its owner is the program), and the data field holds her balance, say, 1,000 THB.

Ada told her friend Bob about the program and invited him to try it out. Bob created his own data account, then tried to send 100 THB to Ada. He looked up Ada's wallet address, opened the program excitedly, and was about to send the funds...

But then he paused.

"Wait, what's Ada's Thai Baht Coin account address? Isn't it just her wallet?"

Here's the problem: Solana data accounts can be arbitrarily created and have no direct link to wallet addresses! Ada might have used any address for her Thai Baht Coin account, as long as it was pre-created and owned by the program.

Now Bob was frustrated. He had to ask every recipient: "Hey, what's your data account address again?"

Ada thought, "Wouldn't it be great if I could deterministically derive the data account address from my regular wallet address?"

## Program Derived Addresses

To solve this problem, Solana introduces a special type of address called a PDA (Program Derived Address). A PDA is derived from a program's public key and a custom seed, often the user's regular wallet address. The resulting address is unique and deterministic.

In the example above, if Bob knows the Thai Baht Coin program's address and Ada's wallet address, he can compute Ada's Thai Baht Coin data account address, no need to ask her.

So, Ada upgraded her system. From now on, every user's Thai Baht Coin balance must be stored in a PDA.

Q: Suppose the program address for Thai Baht Coin is `F782pXBcfvHvb8eJfrDtyD7MBtQDfsrihSRjvzwuVoJU`. What's Ada's PDA for this program?

A: In pxsol, we can use the `derive_pda()` function to compute a program's PDA for a given user account.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
thb = pxsol.core.PubKey.base58_decode('F782pXBcfvHvb8eJfrDtyD7MBtQDfsrihSRjvzwuVoJU')
pda = thb.derive_pda(ada.pubkey.p)
print(pda) # HCPe787nPq7TfjeFivP9ZvZwejTAq1PGGzch93qUYeC3
```

## Summary

Data accounts are used by programs to store their internal state. In theory, any account can be a data account. However, on Solana, developers often prefer using PDAs to deterministically generate data accounts.

Did you know? The BPF bytecode for the `hello_solana_program.so` we deployed earlier is actually stored in a PDA account too. You can verify it with the following code:

```py
import pxsol

program = pxsol.core.PubKey.base58_decode('3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja')
program_data = pxsol.core.PubKey.hex_decode('aa9e796c79af00804caa1acdfca6ba5f17d346a5c4f96db97f9e969fb7d9dc4e')
assert pxsol.program.LoaderUpgradeable.pubkey.derive_pda(program.p) == program_data
```

With PDAs, life on-chain is just a little bit smoother!
