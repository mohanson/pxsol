# Solana/More Developer Tools/Rewriting the Simple Data Storage Program with Pinocchio

This section builds on [pxsol-ss](https://github.com/mohanson/pxsol-ss) to demonstrate how to rewrite it with Pinocchio. The final course code lives in the [pxsol-ss-pinocchio](https://github.com/mohanson/pxsol-ss-pinocchio) repository.

## Migration Work

The first changes we need are how we query `rent_exemption` and `bump_seed`. Here's the before/after:

**Old**

```rs
let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
let bump_seed = solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;
```

**New**

```rs
let rent_exemption = pinocchio::sysvars::rent::Rent::get()?.minimum_balance(data.len());
let bump_seed = &[pinocchio::pubkey::find_program_address(&[&account_user.key()[..]], program_id).1];
```

To check if the PDA is already initialized:

**Old**

```rs
if **account_data.try_borrow_lamports().unwrap() == 0 { ...
```

**New**

```rs
if account_data.lamports() == 0 { ...
```

To call the system program and create the PDA: in Pinocchio, system calls are wrapped in the `pinocchio_system` crate with a cleaner API. Before/after:

**Old**

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

**New**

```rs
pinocchio_system::instructions::CreateAccount {
    from: &account_user,
    to: &account_data,
    lamports: rent_exemption,
    space: data.len() as u64,
    owner: program_id,
}
.invoke_signed(&[signer])?;
```

To write data into the PDA:

**Old**

```rs
account_data.data.borrow_mut().copy_from_slice(data);
```

**New**

```rs
account_data.try_borrow_mut_data().unwrap().copy_from_slice(data);
```

To adjust balances:

**Old**

```rs
**account_user.lamports.borrow_mut() = account_user.lamports() + account_data.lamports() - rent_exemption;
**account_data.lamports.borrow_mut() = rent_exemption;
```

**New**

```rs
*account_user.try_borrow_mut_lamports().unwrap() += account_data.lamports() - rent_exemption;
*account_data.try_borrow_mut_lamports().unwrap() = rent_exemption;
```

Migration done—here's the full code:

```rs
use pinocchio::sysvars::Sysvar;

pinocchio::entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &pinocchio::pubkey::Pubkey,
    accounts: &[pinocchio::account_info::AccountInfo],
    data: &[u8],
) -> pinocchio::ProgramResult {
    let account_user = accounts[0];
    let account_data = accounts[1];

    let rent_exemption = pinocchio::sysvars::rent::Rent::get()?.minimum_balance(data.len());
    let bump_seed = &[pinocchio::pubkey::find_program_address(&[&account_user.key()[..]], program_id).1];
    let signer_seed = pinocchio::seeds!(account_user.key(), bump_seed);
    let signer = pinocchio::instruction::Signer::from(&signer_seed);

    // Data account is not initialized. Create an account and write data into it.
    if account_data.lamports() == 0 {
        pinocchio_system::instructions::CreateAccount {
            from: &account_user,
            to: &account_data,
            lamports: rent_exemption,
            space: data.len() as u64,
            owner: program_id,
        }
        .invoke_signed(&[signer])?;
        account_data.try_borrow_mut_data().unwrap().copy_from_slice(data);
        return Ok(());
    }

    // Fund the data account to let it rent exemption.
    if rent_exemption > account_data.lamports() {
        pinocchio_system::instructions::Transfer {
            from: &account_user,
            to: &account_data,
            lamports: rent_exemption - account_data.lamports(),
        }
        .invoke()?;
    }

    // Withdraw excess funds and return them to users. Since the funds in the pda account belong to the program, we do
    // not need to use instructions to transfer them here.
    if rent_exemption < account_data.lamports() {
        *account_user.try_borrow_mut_lamports().unwrap() += account_data.lamports() - rent_exemption;
        *account_data.try_borrow_mut_lamports().unwrap() = rent_exemption;
    }
    // Realloc space.
    account_data.resize(data.len())?;
    // Overwrite old data with new data.
    account_data.try_borrow_mut_data().unwrap().copy_from_slice(data);

    Ok(())
}
```

Finally, let's test that the program works. Run these to build, deploy, and test:

```sh
$ python make.py deploy
# 2025/05/20 16:06:38 main: deploy program pubkey="T6vZUAQyiFfX6968XoJVmXxpbZwtnKfQbNNBYrcxkcp"

# Save some data.
$ python make.py save "The quick brown fox jumps over the lazy dog"

# Load data.
$ python make.py load
# The quick brown fox jumps over the lazy dog.

# Save some data and overwrite the old data.
$ python make.py save "片云天共远, 永夜月同孤."
# Load data.
$ python make.py load
# 片云天共远, 永夜月同孤.
```

## Key Metrics Comparison

|               | pxsol-ss  | pxsol-ss-pinocchio |
| ------------- | --------- | ------------------ |
| Build time    | 1m10.242s | 0m1.930s           |
| Artifact size | 75K       | 29K                |
| Dependencies  | 189       | 7                  |

From these metrics you can see clear improvements in build time, artifact size, and dependency count after rewriting with Pinocchio. This shows Pinocchio is a compelling alternative to solana-program for simplifying development and boosting efficiency. We strongly recommend using Pinocchio for new Solana program development.
