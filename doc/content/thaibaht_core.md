# Solana/Thai Baht Coin/Core Mechanism Implementation

This article introduces the implementation principles, core mechanisms, and some interesting points behind the Thai Baht Coin.

## Instruction Routing

The main function of the Thai Baht Coin contract, `process_instruction()`, acts like a small switchboard:

- When the first byte is `0x00`, it executes the mint operation, where Ada personally mints coins and deposits them into their own account.
- When the first byte is `0x01`, it executes the transfer operation between two accounts.

Switching instructions relies solely on this one byte, simple and direct, perfectly embodying Solana's wild style.

```rs
#![allow(unexpected_cfgs)]

use solana_program::sysvar::Sysvar;

solana_program::entrypoint!(process_instruction);

pub fn process_instruction_mint(
    _: &solana_program::pubkey::Pubkey,
    _: &[solana_program::account_info::AccountInfo],
    _: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    Ok(())
}

pub fn process_instruction_transfer(
    _: &solana_program::pubkey::Pubkey,
    _: &[solana_program::account_info::AccountInfo],
    _: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    Ok(())
}

pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    assert!(data.len() >= 1);
    match data[0] {
        0x00 => process_instruction_mint(program_id, accounts, &data[1..]),
        0x01 => process_instruction_transfer(program_id, accounts, &data[1..]),
        _ => unreachable!(),
    }
}
```

## Creating Data Accounts

Before each transfer or minting, the contract checks whether the target PDA data account has been initialized. If not, it immediately uses `invoke_signed()` to call `solana_program::system_instruction::create_account()` to create the account and pay the rent for the PDA data account to ensure rent exemption.

The data account is initialized with 8 bytes of `u64::MIN`, representing a 0 Thai Baht balance.

This automatic account creation logic is very user-friendly, allowing users to transfer funds without having to initialize their data accounts manually. The mint and transfer instructions that initialize the PDA data account are as follows:

```rs
pub fn process_instruction_mint(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_user_pda = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent

    // Data account is not initialized. Create an account and write data into it.
    if **account_user_pda.try_borrow_lamports().unwrap() == 0 {
        let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(8);
        let bump_seed =
            solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,
                account_user_pda.key,
                rent_exemption,
                8,
                program_id,
            ),
            accounts,
            &[&[&account_user.key.to_bytes(), &[bump_seed]]],
        )?;
        account_user_pda.data.borrow_mut().copy_from_slice(&u64::MIN.to_be_bytes());
    }
}
```

```rs
pub fn process_instruction_transfer(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_user_pda = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_into = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_into_pda = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent

    // Data account is not initialized. Create an account and write data into it.
    if **account_into_pda.try_borrow_lamports().unwrap() == 0 {
        let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(8);
        let bump_seed =
            solana_program::pubkey::Pubkey::find_program_address(&[&account_into.key.to_bytes()], program_id).1;
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,
                account_into_pda.key,
                rent_exemption,
                8,
                program_id,
            ),
            accounts,
            &[&[&account_into.key.to_bytes(), &[bump_seed]]],
        )?;
        account_into_pda.data.borrow_mut().copy_from_slice(&u64::MIN.to_be_bytes());
    }
}
```

## Only Ada Can Mint Coins

Don't think anyone can mint Thai Baht coins in Ada's world! At the beginning of the mint operation, we perform a strict verification:

```rs
assert_eq!(*account_user.key, solana_program::pubkey!("6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt"));
```

Only Ada herself can sign to mint coins. No shortcuts, no cheating, and prevent inflation from the start (Note: this restriction does not apply to Ada herself)!

The minting process is also straightforward: First, read Ada's balance, then retrieve the amount to mint from the transaction data, add the two numbers, and write the new balance back to the PDA data account. In this example, the numbers are stored in big-endian format.

```rs
// Mint.
let mut buf = [0u8; 8];
buf.copy_from_slice(&account_user_pda.data.borrow());
let old = u64::from_be_bytes(buf);
buf.copy_from_slice(&data);
let inc = u64::from_be_bytes(buf);
let new = old.checked_add(inc).unwrap();
account_user_pda.data.borrow_mut().copy_from_slice(&new.to_be_bytes());
```

## Transfer Instruction

For the transfer operation, we first initialize the recipient's PDA account (if it hasn't been created yet), then read the balances from both the sender's and the recipient's PDA data accounts. After that, we retrieve the transfer amount from the transaction data, adjust the balances of both parties, and finally write the new balances back to their respective PDA data accounts.

It's important to verify that the sender's PDA account actually belongs to the sender during the transfer operation, to prevent someone else from stealing your funds!

```rs
let account_need_pda =
        solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).0;
assert_eq!(account_user_pda.key, &account_need_pda);
```

Rust's `.checked_sub()` and `.checked_add()` have overflow detection to prevent you from accidentally turning negative balances into millions on-chain. The transfer process is as follows:

```rs
// Transfer.
let mut buf = [0u8; 8];
buf.copy_from_slice(&account_user_pda.data.borrow());
let old_user = u64::from_be_bytes(buf);
buf.copy_from_slice(&account_into_pda.data.borrow());
let old_into = u64::from_be_bytes(buf);
buf.copy_from_slice(&data);
let inc = u64::from_be_bytes(buf);
let new_user = old_user.checked_sub(inc).unwrap();
let new_into = old_into.checked_add(inc).unwrap();
account_user_pda.data.borrow_mut().copy_from_slice(&new_user.to_be_bytes());
account_into_pda.data.borrow_mut().copy_from_slice(&new_into.to_be_bytes());
Ok(())
```
