# Solana/Transactions/System Program

The Solana System Program, identified by the address `1111111...`, is the most fundamental program in Solana, responsible for providing basic blockchain account management functions. Its primary features include creating accounts, transferring balances, and storing data. By invoking it within transactions, you can implement a variety of complex functionalities, showcasing Solana's programmability.

The list of instructions supported by the System Program is defined in <https://github.com/solana-program/system/blob/main/interface/src/instruction.rs>.

You'll notice that instruction data is defined as an enumeration type and encoded using Bincode. Bincode is a compact encoding method designed such that the encoded size of an object is equal to or smaller than the memory it occupies in a running Rust program.

For detailed Bincode encoding specifications, see <https://github.com/bincode-org/bincode/blob/trunk/docs/spec.md>.

Roughly speaking, for now, we only need to focus on the following Bincode rules:

- All numbers are encoded in little-endian order.
- Enumerations have an index value treated as a u32. During encoding, the index is encoded first, followed by its associated value.

Below is an analysis of the first three main instructions in the System Program. The remaining instructions are left for you to explore on your own after this section, I'm confident you'll be able to do so. Keep it up!

## Create Account

Purpose: Used to create a new account and assign its ownership to the System Program.

Location: `SystemInstruction::CreateAccount`

Accounts:

|     Account     | Permission |                  Description                   |
| --------------- | ---------- | ---------------------------------------------- |
| Funding Account | 3          | Must have sufficient SOL balance to cover fees |
| New Account     | 3          | -                                              |

> Remember how we represent account permissions? We use two bits: bit 0 indicates whether the account is writable, and bit 1 indicates whether it needs to sign.

Data:

|   Name   |  Type  |                    Description                    |
| -------- | ------ | ------------------------------------------------- |
| index    | u32    | Fixed as 0                                        |
| lamports | u64    | Number of lamports to transfer to the new account |
| space    | u64    | Number of bytes of memory to allocate             |
| owner    | pubkey | Address of program that will own the new account  |

## Assign

Purpose: Transfers ownership of an account to a specified program. Solana's account model requires every account to have an owner; the accounts we typically use daily are owned by the System Program.

Location: `SystemInstruction::Assign`

Accounts:

|           Account           | Permission | Description |
| --------------------------- | ---------- | ----------- |
| Assigned account public key | 3          | -           |

Data:

| Name  |  Type  |      Description      |
| ----- | ------ | --------------------- |
| index | u32    | Fixed as 1            |
| owner | pubkey | Owner program account |

## Transfer

Purpose: Transfers SOL balance from one account to another.

Location: `SystemInstruction::Transfer`

Accounts:

|      Account      | Permission | Description |
| ----------------- | ---------- | ----------- |
| Funding account   | 3          | -           |
| Recipient account | 1          | -           |

Data:

|   Name   | Type |        Description        |
| -------- | ---- | ------------------------- |
| index    | u32  | Fixed as 2                |
| lamports | u64  | Amount of SOL to transfer |

## Other Built-in Programs

The execution of the Solana System Program is "account-based", It performs tasks by modifying the state and stored data of accounts. Beyond the System Program, Solana includes several other built-in programs:

- Token Program: The Solana Token Program allows users to create their own tokens and perform operations like transferring, minting, and burning tokens. If you've engaged in on-chain token transactions on Solana, you've likely interacted with this program frequently. Source code: <https://github.com/solana-program/token-2022>.
- Stake Program: The Solana Stake Program enables users to stake SOL tokens in the network, participating in the validation process. Staking is part of Solana's consensus algorithm, allowing users to earn network rewards through staking.
- Rent Program: The Solana Rent Program manages the storage rent mechanism for accounts in the network. Storage space in Solana is limited, so users must pay a "rent fee" when creating accounts to ensure their data remains stored on the network.

## Exercise

Q: What is the public key of the Solana System Program? Please express it in hexadecimal.

A: The public key of the Solana System Program is a 32-byte array of all zeros. It's a "black hole" account, theoretically with no corresponding private key.

```py
import pxsol

pubkey = pxsol.core.PubKey.base58_decode('11111111111111111111111111111111')
assert pubkey.hex() == '0000000000000000000000000000000000000000000000000000000000000000'
```

Q: If Ada wants to transfer 2 SOL to Bob, how should he construct the instruction data?

A: We could manually assemble the data according to the rules above, or use the `pxsol.program` module to build it. Here, we'll demonstrate the latter method:

```py
import pxsol

data = pxsol.program.System.transfer(2 * pxsol.denomination.sol)
assert pxsol.base58.encode(data) == '3Bxs3zxH1DZVrsVy'
```
