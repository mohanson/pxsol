# Solana/Deploying Your Token on the Mainnet/Program-Controlled Tokens

Airdrops are like handing out candy to everyone, but to implement an automatic candy distribution program (which we refer to as the airdrop program), you must first ensure the program has enough candy in stock. It's like planning to distribute candy at a party, you first need to make sure you have candy in hand!

On Solana, tokens are not directly stored in wallets or programs; they are managed through associated token accounts. Program-controlled tokens also need to be managed and transferred through associated token accounts.

## Token Transfer Process

Let's revisit associated token accounts. Token transfers don't occur directly between the user's wallet and the receiving account; they happen via associated token accounts. You can think of it like a small dedicated wallet box inside your big wallet, where each small box corresponds to a specific type of token.

Token transfers happen by opening your big wallet, then opening the small wallet box, and finally sending it to another user's small wallet.

To implement program-controlled tokens, the following three account layers are typically required:

* **Program Account**: This is the airdrop program, which controls the ownership of the tokens. It is responsible for allocating and transferring tokens. The program account interacts with other accounts by executing the `invoke` or `invoke_signed` instructions.
* **Program PDA Account**: The program account usually cannot directly own tokens. Instead, the program account can derive a PDA account to store the tokens. This PDA account is generated using the program's address and a specific seed. The signing authority for the derived account is controlled by the program account via `invoke_signed`.
* **Associated Token Account**: This is the account that actually stores the token balance. The associated token account is derived from the program's PDA account.

In simple terms, the relationship between the accounts is: **Program Account -> Program PDA Account -> Associated Token Account**.

The true ownership of the tokens lies with the program PDA account, but thanks to the nature of the PDA account, the program account can sign on behalf of the PDA account, thereby essentially owning the tokens.

## Detailed Working Mechanism

On Solana, the program account controls the PDA account via signing, allowing the program to manage the tokens on behalf of the PDA account. This is because the PDA account itself does not have a private key, and its signing operations can only be completed using a signing seed related to the program account.

Assume you have a program that needs to transfer tokens to a user. The process would be as follows:

1. The program account initiates the transfer request to the PDA account using the `invoke_signed` instruction.
2. The PDA account holds the tokens, and the program signs the transfer with the signing seed, completing the transfer from the PDA account to the user's associated token account.

Core code example:

```rs
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
