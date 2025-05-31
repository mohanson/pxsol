# Solana/Program Development Basics/Entry Point Explanation

Every Solana transaction contains one or more instructions. An instruction is a call to a program account on-chain. It has three main components, as defined in the [source code](https://github.com/anza-xyz/solana-sdk/blob/1276772ee61fbd1f8a60cfec7cd553aa4f6a55f3/instruction/src/lib.rs#L97-L104):

```rs
pub struct Instruction {
    /// The public key of the program that will execute this instruction.
    pub program_id: Pubkey,
    /// Metadata describing the accounts to pass to the program.
    pub accounts: Vec<AccountMeta>,
    /// Opaque data for the program to interpret.
    pub data: Vec<u8>,
}
```

So, whenever an instruction is executed, it gets sent to your program's entry point, `process_instruction()`.

## Program Entry Point Signature

```rs
solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    solana_program::msg!("Hello Solana!");
    Ok(())
}
```

Let's break this down.

**Param** `program_id: &solana_program::pubkey::Pubkey` is the address (public key) of your deployed program account. When the transaction calls this program, Solana fills in this field with your program's address. You can use it for validation, for example, to ensure that a PDA was created by your program:

```rs
let expected_pda = solana_program::pubkey::Pubkey::create_program_address(&[seed], program_id)?;
```

**Param** `accounts: &[solana_program::account_info::AccountInfo]` represents all the accounts involved in the instruction. It corresponds to the `Instruction.accounts` field, which the client provided. Your program cannot access arbitrary accounts on-chain, it can only work with the ones passed here.

Each `AccountInfo` includes:

0. The account's public key (key)
0. Whether the account signed the transaction (is_signer)
0. Whether it's writable (is_writable)
0. Its lamport balance (lamports)
0. Its data (data)
0. Which program owns the account (owner)
0. ...

You typically index into this slice to grab the accounts you need:

```rs
let account_user = &accounts[0];
let account_user_pda = &accounts[1];
```

The order of these accounts is critical: your program must interpret them in exactly the same order the client passed them.

**Param** `data: &[u8]` is the raw byte data from the `Instruction.data` field. It's how the client tells your program "what to do" and with what parameters. Typically, you define your own structure for this and serialize/deserialize it with libraries like [borsh](https://crates.io/crates/borsh) or [serde](https://crates.io/crates/serde), or you parse it manually.

Think of it as a function call's arguments, except it's a single binary blob.

Solana's runtime doesn't allow programs to scan the whole blockchain or pull in arbitrary accounts. It's designed for performance: your program must treat this function as a pure function of the inputs: `program_id`, `accounts`, and `data`, and compute results purely from them.

This approach contrasts with chains like Ethereum, where contracts can freely read storage of other contracts. In Solana, the caller must pre-fetch and pass in all the needed accounts and data, so that the program's execution is fully deterministic and bounded.
