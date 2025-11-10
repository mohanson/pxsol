# Solana/Program Development Basics/Creating a Data Account with Rent-Exemption

We're going to implement the first feature of an on-chain data storage system. When a user tries to upload data for the first time to their own dedicated data account, we'll handle the following tasks:

0. When the user uploads for the first time, the program will create a PDA data account for them.
0. The length of the uploaded data can be customized.
0. The created account will automatically be rent-exempt to prevent it from being purged in the future.

## Involved Accounts

Before we start coding, let's consider which accounts are involved in this feature.

0. The user's main wallet account. Creating a PDA data account requires the user's main wallet as the seed, and it must provide the lamports needed for rent exemption. This account must be writable and sign the transaction.
0. The user's newly created data account. We'll create a PDA data account and write data into it. This account must be writable but does not need to sign.
0. The system program account. Only the system program can create new accounts. This account is read-only and does not need to sign.
0. The sysvar rent account. Solana exposes various cluster state data to programs through sysvar accounts. In this example, we need to know how many lamports are required to make the data account rent-exempt. Since this value can change dynamically with the cluster, we need to access the sysvar rent account. This account is read-only and does not need to sign. You can learn more about sysvar accounts on [this page](https://docs.anza.xyz/runtime/sysvars).

Here's a summary of the account list:

| Account Index |     Address     | Needs Signature | Writable | Permission(0-3) |         Role          |
| ------------- | --------------- | --------------- | -------- | --------------- | --------------------- |
| 0             | ...             | Yes             | Yes      | 3               | User's regular wallet |
| 1             | ...             | No              | Yes      | 1               | User's data account   |
| 2             | `1111111111...` | No              | No       | 0               | System                |
| 3             | `SysvarRent...` | No              | No       | 0               | Sysvar rent           |

To retrieve the account information in the `process_instruction()` function's accounts parameter:

```rs
let accounts_iter = &mut accounts.iter();
let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
let account_data = solana_program::account_info::next_account_info(accounts_iter)?;
let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent
```

## Calculating Rent Exemption

Solana provides a function to determine the minimum balance required for rent exemption:

```rs
let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
```

The parameter `data.len()` is the number of bytes you plan to store in the PDA account. The return value is the number of lamports needed for rent exemption.

## Deriving the PDA Data Account Address

Use `solana_program::pubkey::Pubkey::find_program_address` to derive the PDA address and bump value. In this example, we only need the bump value:

```rs
let bump_seed = solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;
```

## Checking if the PDA Already Exists

Solana's SDK doesn't provide a direct way to check if an account exists. Instead, we rely on the fact that any existing account must be rent-exempt, so its balance will never be zero:

```rs
if **account_data.try_borrow_lamports().unwrap() == 0 {
    // Data account is not initialized.
}
```

## Creating the PDA Account

You'll need to use the system program's `solana_program::system_instruction::create_account` instruction to create the account:

```rs
solana_program::system_instruction::create_account(
    account_user.key,
    account_data.key,
    rent_exemption,
    data.len() as u64,
    program_id,
)
```

Since a PDA has no private key and cannot sign on its own, you must sign on its behalf using the program's seeds:

```rs
solana_program::program::invoke_signed(
    &solana_program::system_instruction::create_account(
        account_user.key,
        account_data.key,
        rent_exemption,
        data.len() as u64,
        program_id,
    ),
    accounts,
    &[&[&account_user.key.to_bytes(), &[bump_seed]]],
)?;
```

The Solana Rust SDK has a function `invoke()` that is very similar to `invoke_signed()`. Both are used to execute instructions, but there's an important difference: in this example, we're operating on a PDA, which doesn't have a private key and therefore cannot sign directly. However, as the program owns the PDA, it can sign on its behalf. So, instead of using `invoke()`, we must use `invoke_signed()` to inform the Solana system: "This account doesn't have a signature, but as its creator, I'm signing for it."

Done! You now have a rent-exempt PDA data account.

## Writing Data

Finally, let's write the data into the account. It's simple:

```rs
account_data.data.borrow_mut().copy_from_slice(data);
```

## Complete Code

```rs
#![allow(unexpected_cfgs)]

use solana_program::sysvar::Sysvar;

solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_data = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent

    let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
    let bump_seed = solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;

    // Data account is not initialized. Create an account and write data into it.
    if **account_data.try_borrow_lamports().unwrap() == 0 {
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,
                account_data.key,
                rent_exemption,
                data.len() as u64,
                program_id,
            ),
            accounts,
            &[&[&account_user.key.to_bytes(), &[bump_seed]]],
        )?;
        account_data.data.borrow_mut().copy_from_slice(data);
        return Ok(());
    }
    Ok(())
}
```
