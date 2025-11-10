# Solana/Program Development Basics/Setting Up the Rust Development Environment

In the blockchain world, Solana has long been known for its speed and high concurrency. If you have some web3 experience, you've probably heard that Solana does things differently: it doesn't use the EVM, doesn't use Solidity, and programs are written in Rust, deployed as BPF bytecode.

> We already have enough EVM blockchain projects!

At first glance, this might sound intimidating, but once you get started, you'll find that Solana's program system is clean, highly performant, and follows a very engineering- and template-friendly approach to resource management. Once you manage to write your first working program, you'll be able to build almost any type of program in the Solana ecosystem.

This article will guide you step by step in setting up the Solana program development environment, preparing you for the learning and hands-on experiments to come.

## Why Write Solana Contracts in Rust

Solana's runtime isn't based on the EVM, it's based on the Berkeley Packet Filter (BPF), a bytecode format that's been battle-tested for running in kernels and sandboxes.

The Berkeley Packet Filter, born in the early 1990s (yes, it's older than many young hackers), was originally designed for packet capture in Unix systems. In short, it's a highly efficient mechanism for filtering network packets, letting the kernel decide which packets should be dropped and which should be sent to user-space programs, like a gatekeeper deciding who gets into the neighborhood. At its core is a small, elegant virtual machine that runs a simple instruction set (compared to the massive instruction sets of x86 or ARM, BPF's instruction set is like a pocket-sized robot). Over time, developers realized that they could use this BPF instruction set for much more, and BPF evolved into a powerful sandboxed execution environment.

Rust is currently the most mature language for writing Solana BPF programs, for several reasons:

- Rust's compiler is very strict about memory and type safety, which reduces low-level bugs.
- Rust's performance is close to C/C++ but with greater safety.
- Most importantly: Solana's official SDK is written in Rust and has a well-established ecosystem.

So, whether you're a web developer, a seasoned smart contract engineer, or a systems programmer, if you want to write Solana programs, Rust is the one and only choice.

## Installing the Rust Toolchain

If you're already a Rust user, you can skip this step. Otherwise, head to the [Rust installation page](https://www.rust-lang.org/tools/install) and follow the instructions to install Rust. For Linux, macOS, and Windows Subsystem for Linux, the installation command is the same:

```sh
$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

After installing, run:

```sh
$ rustup --version
$ cargo --version
```

To confirm everything is set up.

## Anchor Development Framework (Optional but Not Recommended for Now)

Anchor is a development framework for Solana programs. It has some nice features, like programs templates, automatic handling of PDA account permissions, and support for integration testing. However, for beginners, jumping into program development with a framework too soon can prevent you from truly understanding Solana's underlying program logic.

Since most Solana tutorials and documentation tend to rely on frameworks, I want to make it clear here: the upcoming sections of this chapter will not depend on the Anchor framework, and you don't need to install Anchor for now.
