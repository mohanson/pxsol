# Solana/Program Development Basics/Setting Up the Initial Project Structure

In this article, we'll set up a clean, pure Rust Solana program project directory structure as the starting point for our on-chain data storage project.

## Create a Blank Project

First, let's create a standard Rust library project:

```sh
$ cargo new --lib pxsol-ss
$ cd pxsol-ss
```

This project will contain our main program logic, the program that will be deployed on-chain. The project name `pxsol-ss` stands for `pxsol-simple-storage`.

## Configure the Compilation Target

Edit the `Cargo.toml` file and add the following settings:

```toml
[lib]
crate-type = ["cdylib", "lib"]
```

This tells Cargo to generate two types of crates.

The `cdylib` compiles the project as a C-compatible dynamic library. Solana requires programs to be compiled as a `.so` file in cdylib format to deploy on-chain. The `.so` file will be generated using `cargo build-bpf`.

The `lib` tells Cargo to also compile it as a standard Rust library (.rlib). This makes it easier to treat your program logic as a regular Rust module during local development and testing.

In short: you need `cdylib` for deployment, and `lib` for development and testing.

## Add Dependencies

We'll need to pull in Solana's core SDK:

```toml
[dependencies]
solana-program = "1.18.0"
```

## Project Directory Reference

Your final directory structure might look like this:

```text
pxsol-ss/
├── Cargo.toml
└── src/
    └── lib.rs
```

And your Cargo.toml will look like this:

```toml
[package]
name = "pxsol-ss"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib", "lib"]

[dependencies]
solana-program = "1.18"
```

## Create the lib.rs Skeleton

Inside `src/lib.rs`, start with a minimal entrypoint:

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

This program doesn't do anything yet except print a message when called. But it can already be compiled into a Solana-compatible BPF program.

## Try Compiling

Run the following command to perform cross-compilation:

```sh
$ cargo build-sbf -- -Znext-lockfile-bump
```

If all goes well, you'll see a `pxsol_ss.so` file in the `target/deploy/` directory. This is the program file ready to be deployed to Solana.

Note: the `-Znext-lockfile-bump` flag is a temporary workaround because Solana v1.18 depends on Rust 1.75, and there are some compatibility issues if you're using a newer Rust version. You might not need this flag anymore depending on the Solana toolchain updates. For more details, refer to this [GitHub page](https://github.com/solana-foundation/anchor/issues/3392).

## Summary

At this point, you've set up the most basic framework for a Solana program written in pure Rust. This is the first step in creating our user-managed on-chain data storage system.

In the next chapter, we'll dive into implementing account derivation and data storage logic. Time to get hands-on with Solana's account model!
