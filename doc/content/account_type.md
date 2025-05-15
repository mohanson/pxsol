# Solana/Account Model/Account Data Structure

In Solana, each account essentially acts as a "data storage unit". These accounts are not only used to store SOL (Solana's native token), but can also hold additional data such as smart contract code and state information.

Based on the type of data they store, Solana accounts can be broadly classified into three categories:

- **Regular accounts**: These are the typical wallet accounts used to store and transfer SOL balances.
- **Program accounts**: These store the logic code of smart contracts.
- **Data accounts**: These store the state data produced by smart contracts during execution.

It's worth noting that SOL, the native token, is managed by a special system program account. Because of this, we can also say that regular accounts are a special kind of data account.

Solana accounts have a relatively simple data structure. We can query detailed information about any account via RPC. All you need is the wallet address, and you can retrieve its data using an RPC call.

For example, let's say the wallet address we want to inspect is `6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt`. We can use Solana's [`get_account_info`](https://solana.com/zh/docs/rpc/http/getaccountinfo) RPC method to retrieve the account info. Here's how you might do it using `pxsol`:

```py
import json
import pxsol

prikey = pxsol.core.PriKey.int_decode(1)
pubkey = prikey.pubkey()  # 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
result = pxsol.rpc.get_account_info(pubkey.base58(), {})
print(json.dumps(result, indent=4))
```

Alternatively, you can use `curl` to make a raw HTTP request directly. The result will be the same:

```sh
curl -X POST http://127.0.0.1:8899 \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": ["6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt"]
    }'
```

Both methods return data like this:

```json
{
    "data": [
        "",
        "base64"
    ],
    "executable": false,
    "lamports": 500000000000000000,
    "owner": "11111111111111111111111111111111",
    "rentEpoch": 0,
    "space": 0
}
```

What do these fields mean? Let's break them down one by one:

- `data`: This field contains the actual data stored in the account, returned as a Base64-encoded string. You'll need to decode it to view the raw content.
    - For regular accounts, this field is usually empty or contains minimal metadata, such as the account's state.
    - For program accounts, this field stores the smart contract's code.
    - For data accounts, this field holds the state data of the smart contract during execution.
- `executable`: A boolean indicating whether the account is a smart contract (program account). If true, the account can execute code. For regular and data accounts, this is usually false, since they only store data and don't execute anything.
- `lamports`: The account's balance. The smallest unit in Solana is a lamport. 1 SOL = 10⁹ lamports. In this example, 500000000000000000 lamports equals 500000000 SOL. This field shows the account's current SOL balance.
- owner: The program that controls this account. For regular accounts, this is typically `11111111111111111111111111111111`, which refers to the Solana system program. For data accounts, this will be the address of the associated program account.
- `rentEpoch`: A legacy field from an older mechanism where Solana used to deduct lamports periodically as rent. While this field still exists, Solana deprecated rent collection entirely starting from version 1.14.
- `space`: Indicates the length of the data field in bytes. An account can store up to 10MB of data.

As you can see, all account types share the same underlying data structure. The differences lie in their functionality. Compared to other blockchains, Solana's account model removes much of the complexity found in traditional state management mechanisms (although, admittedly, it introduces some new challenges of its own, which take a bit more time to fully explain...).
