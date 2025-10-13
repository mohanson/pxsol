# Solana/More Developer Tools/Setting Up the Anchor Environment

Earlier in the book we brought our first idea to Solana and wrote a simple program that can store arbitrary data. We did that in vanilla Rust, but had to deal directly with account validation, serialization, and client packing, busywork that can sap motivation. Anchor exists to take that heavy lifting off your plate so you can focus on what you're building, not just getting code to run.

Anchor is a framework designed for developing on-chain programs on Solana. It helps you build and deploy programs quickly and safely by providing tools and abstractions that simplify the process: automatic account/instruction serialization, built-in safety checks, client generation, and testing utilities.

Here we'll rebuild that storage program using Anchor to showcase its magic. This isn't a tool manual, if you want one, see the official docs: <https://book.anchor-lang.com/>. We'll just set up a clean workbench so you can assemble code and focus on core functionality. You'll see Anchor's mental model, run a full local flow from scratch, and learn to recognize a few small pitfalls along the way.

## Environment Setup

If your machine is missing these tools, install them first: Rust, Solana CLI, Node.js and Yarn, and Anchor itself. You can reuse the commands below; skip any steps you've already completed.

Install Anchor (use avm to manage versions):

```bash
$ cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
$ avm install latest
$ avm use latest
$ anchor --version
```

Prepare Solana CLI and a local cluster:

```bash
$ sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
$ solana --version
$ solana config set --url http://127.0.0.1:8899
$ solana-test-validator -r
```

Install Node.js and Yarn, since Anchor's default tests and clients use TypeScript:

```bash
$ npm install -g yarn
```

Companion code for this chapter is here: <https://github.com/mohanson/pxsol-ss-anchor>. If you're browsing that repo, `Anchor.toml` already points to the local network and wallet path, and `tests/` includes the TypeScript tests. From the repo root, install dependencies:

```bash
$ yarn install
```

Tip: The very first time you run the local validator, don't forget to airdrop some funds to your default wallet:

```bash
$ solana airdrop 2
```

## Create a Project

Let's scaffold the smallest viable program with Anchor and see what it looks like.

```bash
$ anchor init pxsol-ss-anchor
$ cd pxsol-ss-anchor
```

The scaffolding creates a few key paths:

- `programs/<name>/src/lib.rs` is your program entrypoint. You'll see the `#[program]` module and a couple of demo methods.
- `Anchor.toml` is the config hub: program ID, cluster configs, test scripts, etc.
- `tests/` contains the TypeScript tests, which will act as your "client" to click the buttons.

Try building it:

```bash
$ anchor build
```

If you haven't started a local validator yet, launch one in a terminal:

```bash
$ solana-test-validator -r
```

Then run the tests:

```bash
$ anchor test --skip-local-validator
```

This command does three things:

0. Builds the Rust program
0. Deploys it to the local cluster
0. Runs the TypeScript tests under `tests/`

## How to Get Started

When implementing real business logic, you can move along this minimal path:

0. Add a method to `programs/<name>/src/lib.rs`, starting by writing the desired accounts struct and constraints.
0. Write a minimal call script in `tests/`, run `anchor test`, and observe failures.
0. Iterate: fill in logic, complete accounts/space/authority constraints, and keep tuning the test until it passes.
0. Finally, wire up your frontend or backend service.

Once you've made it past these gates, Anchor becomes a trusty ratchet. You don't need to ponder Torx vs hex sizes every day, just tighten the screw you actually care about.
