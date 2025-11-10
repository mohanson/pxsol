# Solana/More Developer Tools/Pinocchio? Pinocchio!

The Solana core team is actively building more tools to help developers write and test on-chain programs more efficiently. One interesting project is [pinocchio](https://github.com/anza-xyz/pinocchio), which released its first version during the writing of this book. I explored it and couldn't wait to include it here.

## Pinocchio?

Pinocchio is a zero-dependency, `no_std` Rust crate for writing Solana on-chain programs. It does not depend on [solana-program](https://crates.io/crates/solana-program); instead it targets the raw ABI between the SVM loader and programs (a serialized byte array) and uses zero-copy parsing to map inputs into usable types. The benefits include:

- Smaller binaries: avoid pulling in a large SDK dependency
- Lower resource usage: cheaper entry decoding and CPI execution
- More control: parse inputs on-demand, disable the memory allocator, improve predictability
- Great for extreme size/perf constraints, or projects stuck in "dependency hell"

Zero-dependency is Pinocchio's core selling point. Unlike solana-program, you don't drag in hundreds of dependencies, but you still get equivalent capabilities. It provides similar types and functions and can often replace solana-program in real projects, or allow easy migration from existing solana-program code.

But clarify this: like solana-program, Pinocchio is a library for writing on-chain programs, not a full framework like Anchor. It doesn't offer macros/codegen or local test/deploy tooling. It's a lighter-weight library that helps you write on-chain code more efficiently.

## Quick Start

To use Pinocchio in your project, just add it as a dependency. At the time of writing, the latest version is 0.9.2; pick a version that suits your needs.

```toml
[dependencies]
pinocchio = "0.9"
```

Then use Pinocchio in `src/lib.rs` as a replacement for solana-program, e.g.:

```rust
use pinocchio::{
  account_info::AccountInfo,
  entrypoint,
  msg,
  ProgramResult,
  pubkey::Pubkey
};

entrypoint!(process_instruction);

pub fn process_instruction(
  _program_id: &Pubkey,
  _accounts: &[AccountInfo],
  _instruction_data: &[u8],
) -> ProgramResult {
  msg!("Hello from my program!");
  Ok(())
}
```

If you're familiar with solana-program, this looks very familiar, just the types and macros come from Pinocchio.

Pinocchio also has more advanced usage that lets you control entry and decoding more flexibly, or disable unneeded features to further reduce binary size and runtime cost. We won't go deep here; consult the [Pinocchio docs](https://docs.rs/pinocchio/latest/pinocchio/) for more. As a beginner's tip: if you just want to get going quickly, start as shown above, and explore advanced options later as needed.

## Migration Guide: From solana-program to Pinocchio

If you already have a solana-program-based on-chain program and want to migrate to Pinocchio, here are some suggestions:

**Entrypoint replacement**

Replace `solana_program::entrypoint::process_instruction` with Pinocchio's `entrypoint!` or `lazy_program_entrypoint!` macros.

**Type replacement**

Most solana_program types have equivalents in Pinocchio—swap import paths. For example:

- `solana_program::pubkey::Pubkey` -> `pinocchio::pubkey::Pubkey`
- `solana_program::account_info::AccountInfo` -> `pinocchio::account_info::AccountInfo`

**Logging replacement**

- `solana_program::msg!` -> `pinocchio::msg!`
- For formatted logging, use `pinocchio-log`'s `log!` macro

**CPI and sysvars**

- Replace `solana_program::program::invoke*` and `sysvar` usage with Pinocchio's interfaces (names and usage are intuitive; changes are usually minor)

From the author's perspective, Pinocchio is not just "another Solana program SDK" but rather a minimal ABI-oriented toolkit. It provides the core building blocks you need while giving control back to you. It doesn't over-wrap or over-abstract on-chain concepts. For developers chasing extreme efficiency and control, it can visibly reduce binary size and runtime resource usage while making engineering simpler and more stable.

In the next section, we'll rewrite the earlier on-chain data storage program using Pinocchio to showcase its practical usage and impact.
