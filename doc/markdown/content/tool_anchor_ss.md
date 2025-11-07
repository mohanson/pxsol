# Solana/More Developer Tools/A Simple Data-Storage Program in Anchor

Companion code for this chapter is here: <https://github.com/mohanson/pxsol-ss-anchor>.

In this section we'll build a data storage program with Anchor and walk through the flow from modeling to building. You'll see three key points: the accounts mental model, two instructions (init/update), and details around dynamic reallocation and rent. The code lives in `programs/pxsol-ss-anchor/src/lib.rs`, but we'll explain it conceptually here.

## Designing the Data Format

User data is stored in a PDA program-derived account. In our raw Rust version we didn't heavily constrain the data layout, serialization round-tripped and that was enough. With Anchor, we can define a struct annotated with `#[account]` that describes the storage. This helps development and makes on-chain analysis more straightforward.

```rust
#[account]
pub struct Data {
    pub auth: Pubkey, // The owner of this PDA account
    pub bump: u8,     // The bump used to derive the PDA
    pub data: Vec<u8> // The payload: arbitrary bytes
}

impl Data {
    pub fn space_for(data_len: usize) -> usize {
        // 8 (discriminator) + 32 (auth) + 1 (bump) + 4 (vec len) + data_len
        8 + 32 + 1 + 4 + data_len
    }
}
```

The `space_for()` method computes the required account size. It consists of five parts. We'll use it to calculate the rent-exempt minimum.

## Instruction: Initialize the Program-Derived Account

We define two instructions: `init` and `update`. `init` initializes the PDA; `update` changes its content. Here's `init`, which records the authority, stores the bump, and sets the content to empty:

```rust
pub fn init(ctx: Context<Init>) -> Result<()> {
    let account_user = &ctx.accounts.user;
    let account_user_pda = &mut ctx.accounts.user_pda;
    account_user_pda.auth = account_user.key();
    account_user_pda.bump = ctx.bumps.user_pda;
    account_user_pda.data = Vec::new();
    Ok(())
}
```

The accounts constraints allocate the account and fund rent on first call, with the authority as `payer = user`:

```rust
#[derive(Accounts)]
pub struct Init<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    #[account(
        init,
        payer = user,
        seeds = [SEED, user.key().as_ref()],
        bump,
        space = Data::space_for(0)
    )]
    pub user_pda: Account<'info, Data>,
    pub system_program: Program<'info, System>,
}
```

At this point, the `data` field is empty, but the account has identity and ownership, and is rent-exempt.

## Instruction: Store or Update Data

When updating, we allow the PDA to grow or shrink. Growing requires topping up rent; shrinking returns the surplus lamports to the owner. Think of it in three steps: authorization, reallocation, settlement. Anchor handles rent top-ups and fee debits for reallocation; you handle the refund when shrinking. That is, if new data is larger, Anchor pulls in lamports for rent automatically; if new data is smaller, you should refund excess lamports to the authority.

```rust
pub fn update(ctx: Context<Update>, data: Vec<u8>) -> Result<()> {
    let account_user = &ctx.accounts.user;
    let account_user_pda = &mut ctx.accounts.user_pda;
    // Authorization: only the stored authority can update.
    require_keys_eq!(account_user_pda.auth, account_user.key(), PxsolError::Unauthorized);
    // At this point, Anchor has already reallocated the account according to the `realloc = ...` constraint
    // (using `new_data.len()`), pulling extra lamports from auth if needed to maintain rent-exemption.
    account_user_pda.data = data;
    // If the account was shrunk, Anchor won't automatically refund excess lamports. Refund any surplus (over the
    // new rent-exempt minimum) back to the user.
    let account_user_pda_info = account_user_pda.to_account_info();
    let rent = Rent::get()?;
    let rent_exemption = rent.minimum_balance(account_user_pda_info.data_len());
    let hold = **account_user_pda_info.lamports.borrow();
    if hold > rent_exemption {
        let refund = hold.saturating_sub(rent_exemption);
        // Transfer lamports from PDA to user using the PDA as signer.
        let signer_seeds: &[&[u8]] = &[SEED, account_user.key.as_ref(), &[account_user_pda.bump]];
        let signer = &[signer_seeds];
        let cpictx = CpiContext::new_with_signer(
            ctx.accounts.system_program.to_account_info(),
            system_program::Transfer { from: account_user_pda_info.clone(), to: account_user.to_account_info() },
            signer,
        );
        // It's okay if refund equals current - min_rent; system program enforces balances.
        system_program::transfer(cpictx, refund)?;
    }
    Ok(())
}
```

The corresponding accounts constraints make the instruction's strategies explicit:

```rust
#[derive(Accounts)]
#[instruction(new_data: Vec<u8>)]
pub struct Update<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    #[account(
        mut,
        seeds = [SEED, user.key().as_ref()],
        bump = user_pda.bump,
        realloc = Data::space_for(new_data.len()),
        realloc::payer = user,
        realloc::zero = false,
        constraint = user_pda.auth == user.key() @ PxsolError::Unauthorized,
    )]
    pub user_pda: Account<'info, Data>,
    pub system_program: Program<'info, System>,
}
```

## Tips and Gotchas

- Always check authorization: `require_keys_eq!(...)`
- PDA as signer: use `new_with_signer`, and don't forget the `bump` in seeds.
- Reallocation costs and limits: large one-shot expansions can hit limits; use chunking or multiple updates if needed.
- Funding source: reallocation rent differences come from `user`; insufficient balance will fail the instruction.

## Wrap-up

Our Anchor-based storage program is simple, but it ties together the most common capabilities: account constraints, dynamic reallocation, and PDA signing. Once it runs end-to-end, you can layer on more complex logic. The total code is under 100 lines, an excellent starting point that you can understand quickly, so we won't belabor it here.
