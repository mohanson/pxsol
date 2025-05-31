# Solana/Program Development Basics/Compiling and Deploying the Program

## Compile

Use the following command to compile your program.

```sh
$ cargo build-sbf -- -Znext-lockfile-bump
```

## Deploy the Program

Use the following Python code to deploy the target program on-chain:

```py
import pathlib
import pxsol

# Enable log
pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

program_data = pathlib.Path('target/deploy/pxsol_ss.so').read_bytes()
program_pubkey = ada.program_deploy(bytearray(program_data))
print(program_pubkey) # DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E
```

During deployment, you'll see a flurry of transactions in the logs. Deploying a program on Solana is slightly different from other blockchains like Ethereum. The deployment process involves several steps, each corresponding to one or more transactions:

0. Create a program account.
0. Upload the program code in segments (chunked writes). Because Solana limits the size of a single transaction (a serialized transaction can be at most 1232 bytes), and your program code might be tens of thousands of bytes or more, you must split the BPF bytecode into chunks and upload it in multiple transactions.
0. Once all bytes are uploaded, the final step is to call the BPF Loader's finalize method, marking the account as finalized. From this point on, it becomes a fully functional Solana program.

Though the process is more involved, it's part of Solana's high-performance design.
