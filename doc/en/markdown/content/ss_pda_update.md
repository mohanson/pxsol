# Solana/Program Development Basics/Updating Data Accounts and Dynamic Rent Adjustment

Solana accounts require rent payments for storage; the longer the data, the higher the rent. If you update your data and it becomes longer, the existing rent might not be enough, and the account will no longer be rent-exempt. On the other hand, if the new data is shorter, you've overpaid for rent, and the program can refund the excess!

In this article, we'll walk you through how to implement dynamic rent adjustment.

## Updating Data Account Contents

On-chain accounts can be updated using `.data.borrow_mut()`, but this method cannot change the account space. Usually, you need to recreate or reallocate the data account space by using `.realloc()`.

```rs
// Realloc space.
account_data.realloc(data.len(), false)?;
// Overwrite old data with new data.
account_data.data.borrow_mut().copy_from_slice(data);
```

## Supplementing Rent

If the new data is larger than the old data, you need to add more rent to the PDA account using the system program's `solana_program::system_instruction::transfer` function.

```rs
// Fund the data account to let it rent exemption.
if rent_exemption > account_data.lamports() {
    solana_program::program::invoke(
        &solana_program::system_instruction::transfer(
            account_user.key,
            account_data.key,
            rent_exemption - account_data.lamports(),
        ),
        accounts,
    )?;
}
```

## Refunding Excess Rent

If the new data is shorter than the old data, you can refund the excess rent from the PDA account. Refunding does not require executing system program instructions, simply update the balances of the two accounts.

```rs
// Withdraw excess funds and return them to users. Since the funds in the pda account belong to the program, we do
// not need to use instructions to transfer them here.
if rent_exemption < account_data.lamports() {
    **account_user.lamports.borrow_mut() = account_user.lamports() + account_data.lamports() - rent_exemption;
    **account_data.lamports.borrow_mut() = rent_exemption;
}
```

You might be wondering why we don't use `solana_program::system_instruction::transfer` here. The answer lies in permissions. Remember that each data account has an owner program? The owner program can freely manipulate the data account's balance without needing additional authorization.

- When supplementing rent, the program transfers funds from your wallet account, so it requires your authorization.
- When refunding rent, the program moves funds it already controls (the data account's funds), so it doesn't need your authorization.
