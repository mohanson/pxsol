# Solana/Deploying Your Token on the Mainnet/Implementing the Airdrop Program

The airdrop program we are going to implement includes two main functions:

1. For any user calling the airdrop program, the program will automatically create an associated token account for them.
2. Transfer 5 PXS tokens to them.

The contract program implementation is as follows. The program internally calls two instructions to accomplish the above functionality.

```rs
solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    _: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    _: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_user_spla = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana_auth = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana_spla = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mint = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_spl = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?;

    solana_program::program::invoke(
        &spl_associated_token_account::instruction::create_associated_token_account_idempotent(
            &account_user.key,
            &account_user.key,
            &account_mint.key,
            &account_spl.key,
        ),
        accounts,
    )?;
    let account_seed = &[];
    let account_bump = solana_program::pubkey::Pubkey::find_program_address(&[account_seed], account_mana.key).1;
    solana_program::program::invoke_signed(
        &spl_token_2022::instruction::transfer_checked(
            &account_spl.key,
            &account_mana_spla.key,
            &account_mint.key,
            &account_user_spla.key,
            &account_mana_auth.key,
            &[],
            5000000000,
            9,
        )?,
        accounts,
        &[&[account_seed, &[account_bump]]],
    )?;

    Ok(())
}
```

After compiling the program, use the following code to deploy it on the mainnet.

```py
import pxsol
pxsol.config.current = pxsol.config.mainnet

user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode('Put your private key here'))
with open('target/deploy/pxsol_spl.so', 'rb') as f:
    data = bytearray(f.read())
mana = user.program_deploy(data)
print(mana) # HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6
```

Our airdrop contract is deployed at `HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6` on the mainnet.

Here's a brief analysis of the accounts involved in the airdrop program:


|               Account                | Permissions |                          Description                           |
| ------------------------------------ | ----------- | -------------------------------------------------------------- |
| User Account                         | 3           | /                                                              |
| User Associated Token Account        | 1           | /                                                              |
| Program Account                      | 0           | Mainnet address `HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6` |
| Program PDA Account                  | 0           | Mainnet address `5yAqR4gSYfs7CqpR4mgN5DNT4xczwiATuybaAa33xGip` |
| Program PDA Associated Token Account | 1           | Mainnet address `G7C9Px4x1G5YE2NmUHG6BeuqavoDsQQsHGpfs7nvMcq9` |
| SPL Token Mint Account               | 0           | Mainnet address `6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH` |
| System Program                       | 0           | Mainnet address `11111111111111111111111111111111`             |
| Native Program: Token-2022           | 0           | Mainnet address `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`  |
| Native Program: Associated Token     | 0           | Mainnet address `ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL` |


Finally, don't forget that we need to transfer some tokens to the **Program PDA Account**. The transfer operation is as follows:

```py
import pxsol
pxsol.config.current = pxsol.config.mainnet

user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode('Put your private key here'))
pubkey_mint = pxsol.core.PubKey.base58_decode('6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH')
pubkey_mana = pxsol.core.PubKey.base58_decode('HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6')
pubkey_mana_seed = bytearray([])
pubkey_mana_auth = pubkey_mana.derive_pda(pubkey_mana_seed)
user.spl_transfer(pubkey_mint, pubkey_mana_auth, 90000000 * 10**9)
```

We initially transferred 90 million PXS tokens to the airdrop program. You can view the current PXS balance of the airdrop program via [this page](https://explorer.solana.com/address/5yAqR4gSYfs7CqpR4mgN5DNT4xczwiATuybaAa33xGip/tokens).
