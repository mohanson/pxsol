# Solana/Account Model/Program Accounts

A program account on Solana is an account that has a deployed Solana program (smart contract). Once deployed, it has a **program account address** that others can call. Solana programs are typically written in Rust and compiled into BPF bytecode. We will discuss Solana smart contracts in detail in later chapters. For now, let's focus on the container that stores the program, the program account.

## Deploying a Program

As an experienced developer, you've likely written and run many "Hello World" programs before. Today is no exception; we will try deploying and running a simple program on the Solana network. Luckily, pxsol's resource directory includes a [Hello World program](https://github.com/mohanson/pxsol/blob/master/res/hello_solana_program.so), which you can download with:

```sh
$ wget https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/hello_solana_program.so
```

This `hello_solana_program.so` file is your program code, which will be uploaded to the Solana blockchain.

```py
import pathlib
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

program_data = pathlib.Path('hello_solana_program.so').read_bytes()
program_pubkey = ada.program_deploy(bytearray(program_data))
print(program_pubkey) # 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja
print(pxsol.rpc.get_account_info(program_pubkey.base58(), {}))
# {
#     "data": [
#         "AgAAAKqeeWx5rwCATKoazfymul8X00alxPltuX+elp+32dxO",
#         "base64"
#     ],
#     "executable": true,
#     "lamports": 1141440,
#     "owner": "BPFLoaderUpgradeab1e11111111111111111111111",
#     "rentEpoch": 18446744073709551615,
#     "space": 36
# }
```

In the code above, calling `program_deploy()` deploys the program to the Solana network. In this example, the program is deployed to the program account at address `3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja`.

## Permissions and State of Program Accounts

The deployed program account is owned by the [BPF upgradeable loader](https://docs.anza.xyz/runtime/programs#bpf-loader), identified as `BPFLoaderUpgradeab1e11111111111111111111111`, which controls whether the program can be upgraded.

The account info's `executable: true` flag indicates it is a program account capable of executing code.

Solana has several native programs essential for validator operations. Unlike third-party programs, native programs are part of the Solana network itself. The Solana system program for SOL transfers and the BPF upgradeable loader are examples of native programs.

You can find a list of all current native programs on [this page](https://docs.anza.xyz/runtime/programs).

## Invoking a Program

Programs on Solana act like on-chain workers; if you send them a valid instruction, they perform predefined tasks for you!

Every time you want to invoke an on-chain program, you send a transaction containing an instruction targeting that program, telling it what you want it to do.

Our `hello_solana_program.so` simply sends a "Hello" message to any user who calls it. Let's try calling it!

```py
import base64
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

rq = pxsol.core.Requisition(pxsol.core.PubKey.base58_decode('3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja'), [], bytearray())
tx = pxsol.core.Transaction.requisition_decode(ada.pubkey, [rq])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([ada.prikey])
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
pxsol.rpc.wait([txid])
r = pxsol.rpc.get_transaction(txid, {})
for e in r['meta']['logMessages']:
    print(e)

# Program 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja invoke [1]
# Program log: Hello, Solana!
# Program log: Our program's Program ID: 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja
# Program 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja consumed 11759 of 200000 compute units
# Program 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja success
```

On the second line of output, we receive the program's message: `Hello, Solana!`.

Hello, Solana!

## Wait, Where Is the Program?

Right after deploying, we queried the program account info; the JSON-RPC returned:

```json
{
    "data": [
        "AgAAAKqeeWx5rwCATKoazfymul8X00alxPltuX+elp+32dxO",
        "base64"
    ],
    "executable": true,
    "lamports": 1141440,
    "owner": "BPFLoaderUpgradeab1e11111111111111111111111",
    "rentEpoch": 18446744073709551615,
    "space": 36
}
```

Something seems off, the data stored in the program account looks... quite small. But our program's actual bytecode is 38,936 bytes!

```sh
$ ls hello_solana_program.so
# -rwxrwxr-x  1 ubuntu ubuntu 38936 Sep 13  2024 hello_solana_program.so
```

Actually, in this example, the program account stores program metadata, not the full program code.

Due to historical reasons, Solana supports two deployment models:

| Deployment Type |         Owner          |                                       Description                                        |
| --------------- | ---------------------- | ---------------------------------------------------------------------------------------- |
| Non-upgradeable | BPF Loader             | Bytecode is stored directly in the program account's data field                          |
| Upgradeable     | BPF Upgradeable Loader | Program account is a shell; the real bytecode is stored in a program data account's data |

Non-upgradeable programs are effectively deprecated on Solana, so pxsol no longer supports them. That's why your deployment is an upgradeable Solana program. Here, the program account (the deployed address) does **not** store the full BPF bytecode directly but acts as a pointer to the program data account.

We decode the base64 data string `AgAAAKqeeWx5rwCATKoazfymul8X00alxPltuX+elp+32dxO` as follows:

```py
import base64

data = base64.b64decode('AgAAAKqeeWx5rwCATKoazfymul8X00alxPltuX+elp+32dxO')
print(data.hex())
# 02000000aa9e796c79af00804caa1acdfca6ba5f17d346a5c4f96db97f9e969fb7d9dc4e
```

This structure is managed by the BPF upgradeable loader and roughly corresponds to:

```rs
pub enum UpgradeableLoaderState {
    /// Account is not initialized.
    Uninitialized,
    /// A Buffer account.
    Buffer {
        /// Authority address
        authority_address: Option<Pubkey>,
        // The raw program data follows this serialized structure in the
        // account's data.
    },
    /// An Program account.
    Program {
        /// Address of the ProgramData account.
        programdata_address: Pubkey,
    },
    // A ProgramData account.
    ProgramData {
        /// Slot that the program was last modified.
        slot: u64,
        /// Address of the Program's upgrade authority.
        upgrade_authority_address: Option<Pubkey>,
        // The raw program data follows this serialized structure in the
        // account's data.
    },
}
```

- `02000000` indicates the enum variant index (Program).
- `aa9e796c79af00804caa1acdfca6ba5f17d346a5c4f96db97f9e969fb7d9dc4e` is the address of the program data account.

Now, querying this program data account returns:

```py
import pxsol

program_data_pubkey_byte = bytearray.fromhex('aa9e796c79af00804caa1acdfca6ba5f17d346a5c4f96db97f9e969fb7d9dc4e')
program_data_pubkey = pxsol.core.PubKey(program_data_pubkey_byte)

r = pxsol.rpc.get_account_info(program_data_pubkey.base58(), {})
print(r)
# {
#     "data": [
#         "AwAAACwBAAAAAAAAAUy...AAAAAAAAAAAAAAAAAAAAA==",
#         "base64"
#     ],
#     "executable": false,
#     "lamports": 543193200,
#     "owner": "BPFLoaderUpgradeab1e11111111111111111111111",
#     "rentEpoch": 18446744073709551615,
#     "space": 77917
# }
```

We can confirm the bytecode of `hello_solana_program.so` is indeed stored in the data field of this account.
