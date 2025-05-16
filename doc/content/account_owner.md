# Solana/Account Model/Ownership and Access Control

In Solana, each account has an `owner` field in its data structure, which points to a program account that owns the account. Only the owner program is permitted to modify the account's `data` field or deduct funds from its balance.

The actual functionality of a Solana account is governed by the rules defined by its owner program. To better understand this, let's use a real-world analogy from the banking system:

Ada opens a bank account at Siam Commercial Bank in Thailand and deposits some money into it. In this scenario:

- Ada has ownership and limited usage rights over the funds in the account.
- The account itself is owned by the bank. A bank account is a tool tied to the bank, an extension of the bank's infrastructure.
- Ada is only allowed to perform actions permitted by the bank, such as transfers or remittances. She cannot destroy the funds in her account because the bank doesn't allow such an operation.

Let's emphasize this again: Every Solana account is associated with a program account, and the logic defined by that program determines how the account can be accessed and operated on. The owner program can be Solana's built-in system program or a user-deployed smart contract. This architecture gives Solana great flexibility, enabling fine-grained control over how accounts are managed.
