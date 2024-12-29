import hashlib
import io
import json
import pxsol.base58
import pxsol.eddsa
import typing


class PriKey:
    # Solana's private key is a 32-byte array, selected arbitrarily. In general, the private key is not used in
    # isolation; instead, it forms a 64-byte keypair together with the public key, which is also a 32-byte array.
    # Most solana wallets, such as phantom, import and export private keys in base58-encoded keypair format.

    def __init__(self, p: bytearray) -> None:
        assert len(p) == 32
        self.p = p

    def __hash__(self) -> int:
        return self.int()

    def __repr__(self) -> str:
        return self.base58()

    def __eq__(self, other) -> bool:
        return self.p == other.p

    def base58(self) -> str:
        # Convert the private key to base58 representation.
        return pxsol.base58.encode(self.p)

    @classmethod
    def base58_decode(cls, data: str) -> typing.Self:
        # Convert the base58 representation to private key.
        return PriKey(pxsol.base58.decode(data))

    def hex(self) -> str:
        # Convert the private key to hex representation.
        return self.p.hex()

    @classmethod
    def hex_decode(cls, data: str) -> typing.Self:
        # Convert the hex representation to private key.
        return PriKey(bytearray.fromhex(data))

    def int(self) -> int:
        # Convert the private key to u256 number, in big endian.
        return int.from_bytes(self.p)

    @classmethod
    def int_decode(cls, data: int) -> typing.Self:
        # Convert the u256 number to private key, in big endian.
        return PriKey(bytearray(data.to_bytes(32)))

    def pubkey(self):
        # Get the eddsa public key corresponding to the private key.
        return PubKey(pxsol.eddsa.pubkey(self.p))

    def sign(self, data: bytearray) -> bytearray:
        # Sign a message of arbitrary length. Unlike secp256k1, the resulting signature is deterministic.
        return pxsol.eddsa.sign(self.p, data)

    def wif(self) -> str:
        # Convert the private key to wallet import format. This is the format supported by most third-party wallets.
        pubkey = self.pubkey()
        return pxsol.base58.encode(self.p + pubkey.p)

    @classmethod
    def wif_decode(cls, data: str) -> typing.Self:
        # Convert the wallet import format to private key. This is the format supported by most third-party wallets.
        pripub = pxsol.base58.decode(data)
        prikey = PriKey(pripub[:32])
        pubkey = PubKey(pripub[32:])
        assert prikey.pubkey() == pubkey
        return prikey


class PubKey:
    # Solana's public key is a 32-byte array. The base58 representation of the public key is also referred to as the
    # address.

    def __init__(self, p: bytearray) -> None:
        assert len(p) == 32
        self.p = p

    def __hash__(self) -> int:
        return self.int()

    def __repr__(self) -> str:
        return self.base58()

    def __eq__(self, other) -> bool:
        return self.p == other.p

    def base58(self) -> str:
        # Convert the public key to base58 representation.
        return pxsol.base58.encode(self.p)

    @classmethod
    def base58_decode(cls, data: str) -> typing.Self:
        # Convert the base58 representation to public key.
        return PubKey(pxsol.base58.decode(data))

    def derive(self, seed: bytearray) -> typing.Self:
        # Program Derived Address (PDA). PDAs are addresses derived deterministically using a combination of
        # user-defined seeds, a bump seed, and a program's ID.
        # See: https://solana.com/docs/core/pda
        data = bytearray()
        data.extend(seed)
        data.append(0xff)
        data.extend(self.p)
        data.extend(bytearray('ProgramDerivedAddress'.encode()))
        for i in range(255, -1, -1):
            data[len(seed)] = i
            hash = bytearray(hashlib.sha256(data).digest())
            # The pda should fall off the ed25519 curve.
            if not pxsol.eddsa.pt_exists(hash):
                return PubKey(hash)
        raise Exception

    def hex(self) -> str:
        # Convert the public key to hex representation.
        return self.p.hex()

    @classmethod
    def hex_decode(cls, data: str) -> typing.Self:
        # Convert the hex representation to public key.
        return PubKey(bytearray.fromhex(data))

    def int(self) -> int:
        # Convert the public key to u256 number, in big endian.
        return int.from_bytes(self.p)

    @classmethod
    def int_decode(cls, data: int) -> typing.Self:
        # Convert the u256 number to public key, in big endian.
        return PubKey(bytearray(data.to_bytes(32)))


class AccountMeta:
    # Describes a single account with it's mode. The bit 0 distinguishes whether the account is writable; the bit 1
    # distinguishes whether the account needs to be signed. Details are as follows:
    #   0: readonly
    #   1: writable
    #   2: readonly + signer
    #   3: writable + signer

    def __init__(self, pubkey: PubKey, mode: int) -> None:
        self.pubkey = pubkey
        self.mode = mode

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'pubkey': self.pubkey.base58(),
            'mode': ['-r', '-w', 'sr', 'sw'][self.mode],
        }


class Requisition:
    # A directive for a single invocation of a solana program.

    def __init__(self, program: PubKey, account: typing.List[AccountMeta], data: bytearray) -> None:
        self.program = program
        self.account = account
        self.data = data

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'program': self.program.base58(),
            'account': [e.json() for e in self.account],
            'data': pxsol.base58.encode(self.data),
        }


class ProgramAssociatedTokenAccount:
    # See: https://github.com/solana-labs/solana-program-library/blob/master/associated-token-account/program/src/instruction.rs

    pubkey = PubKey.base58_decode('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL')

    @classmethod
    def create(cls) -> bytearray:
        # Creates an associated token account for the given wallet address and token mint. Returns an error if the
        # account exists. Account references:
        # 0. sw funding account (must be a system account).
        # 1. -w associated token account address to be created.
        # 2. -r wallet address for the new associated token account.
        # 3. -r the token mint for the new associated token account.
        # 4. -r system program.
        # 5. -r spl token program.
        r = bytearray([0x00])
        return r

    @classmethod
    def create_idempotent(cls) -> bytearray:
        # Creates an associated token account for the given wallet address and token mint, if it doesn't already exist.
        # Returns an error if the account exists, but with a different owner. Account references:
        # 0. sw funding account (must be a system account).
        # 1. -w associated token account address to be created.
        # 2. -r wallet address for the new associated token account.
        # 3. -r the token mint for the new associated token account.
        # 4. -r system program.
        # 5. -r spl token program.
        r = bytearray([0x01])
        return r

    @classmethod
    def recover_nested(cls) -> bytearray:
        # Transfers from and closes a nested associated token account: an associated token account owned by an
        # associated token account. Account references:
        # 0. -w nested associated token account, must be owned by 3.
        # 1. -r token mint for the nested associated token account.
        # 2. -w wallet's associated token account.
        # 3. -r owner associated token account address, must be owned by 5.
        # 4. -r token mint for the owner associated token account.
        # 5. sw wallet address for the owner associated token account.
        # 6. -r spl token program.
        r = bytearray([0x02])
        return r


class ProgramComputeBudget:
    # Compute budget instructions.

    pubkey = PubKey.base58_decode('ComputeBudget111111111111111111111111111111')

    @classmethod
    def request_heap_frame(cls, size: int) -> bytearray:
        # Request a specific transaction-wide program heap region size in bytes. The value requested must be a multiple
        # of 1024. This new heap region size applies to each program executed in the transaction, including all calls
        # to cpis.
        r = bytearray([0x01, 0x00, 0x00, 0x00])
        r.extend(bytearray(size.to_bytes(4, 'little')))
        return r

    @classmethod
    def set_compute_unit_limit(cls, size: int) -> bytearray:
        # Set a specific compute unit limit that the transaction is allowed to consume.
        r = bytearray([0x02, 0x00, 0x00, 0x00])
        r.extend(bytearray(size.to_bytes(4, 'little')))
        return r

    @classmethod
    def set_compute_unit_price(cls, price: int) -> bytearray:
        # Set a compute unit price in "micro-lamports" to pay a higher transaction fee for higher transaction
        # prioritization. There are 10^6 micro-lamports in one lamport.
        assert price <= 4  # Are you sure you want to pay such a high fee? You must have filled in the wrong number bro!
        r = bytearray([0x03, 0x00, 0x00, 0x00])
        r.extend(bytearray(price.to_bytes(8, 'little')))
        return r

    @classmethod
    def set_loaded_accounts_data_size_limit(cls, size: int) -> bytearray:
        # Set a specific transaction-wide account data size limit, in bytes, is allowed to load.
        r = bytearray([0x04, 0x00, 0x00, 0x00])
        r.extend(bytearray(size.to_bytes(4, 'little')))
        return r


class ProgramLoaderUpgradeable:
    # The bpf loader program is the program that owns all executable accounts on solana. When you deploy a program, the
    # owner of the program account is set to the the bpf loader program.
    # See: https://github.com/anza-xyz/agave/blob/master/sdk/program/src/loader_upgradeable_instruction.rs

    pubkey = PubKey.base58_decode('BPFLoaderUpgradeab1e11111111111111111111111')

    size_uninitialized = 4  # Size of a serialized program account.
    size_buffer_metadata = 37  # Size of a buffer account's serialized metadata.
    size_program_data_metadata = 45  # Size of a programdata account's serialized metadata.
    size_program = 36  # Size of a serialized program account.

    @classmethod
    def initialize_buffer(cls) -> bytearray:
        # Initialize a Buffer account. Account references:
        # 0. -w source account to initialize.
        # 1. -r buffer authority. optional, if omitted then the buffer will be immutable.
        r = bytearray([0x00, 0x00, 0x00, 0x00])
        return r

    @classmethod
    def write(cls, offset: int, data: bytearray) -> bytearray:
        # Write program data into a buffer account. Account references:
        # 0. -w buffer account to write program data to.
        # 1. sr buffer authority.
        r = bytearray([0x01, 0x00, 0x00, 0x00])
        r.extend(bytearray(offset.to_bytes(4, 'little')))
        r.extend(bytearray(len(data).to_bytes(8, 'little')))
        r.extend(data)
        return r

    @classmethod
    def deploy_with_max_data_len(cls, size: int) -> bytearray:
        # Deploy an executable program. Account references:
        # 0. sw the payer account that will pay to create the program data account.
        # 1. -w the uninitialized program data account.
        # 2. -w The uninitialized program account.
        # 3. -w The buffer account where the program data has been written.
        # 4. -r rent sysvar.
        # 5. -r clock sysvar.
        # 6. -r system program.
        # 7. sr the program's authority.
        r = bytearray([0x02, 0x00, 0x00, 0x00])
        r.extend(bytearray(size.to_bytes(8, 'little')))
        return r

    @classmethod
    def upgrade(cls) -> bytearray:
        # Upgrade a program. Account references:
        # 0. -w the program data account.
        # 1. -w the program account.
        # 2. -w the buffer account where the program data has been written.
        # 3. -w the spill account.
        # 4. -r rent sysvar.
        # 5. -r clock sysvar.
        # 6. sr the program's authority.
        r = bytearray([0x03, 0x00, 0x00, 0x00])
        return r

    @classmethod
    def set_authority(cls) -> bytearray:
        # Set a new authority that is allowed to write the buffer or upgrade the program. Account references:
        # 0. -w the buffer or program data account to change the authority of.
        # 1. sr the current authority.
        # 2. -r the new authority, optional, if omitted then the program will not be upgradeable.
        r = bytearray([0x04, 0x00, 0x00, 0x00])
        return r

    @classmethod
    def close(cls) -> bytearray:
        # Closes an account owned by the upgradeable loader of all lamports and withdraws all the lamports.
        # 0. -w the account to close, if closing a program must be the program data account.
        # 1. -w the account to deposit the closed account's lamports.
        # 2. sr the account's authority, optional, required for initialized accounts.
        # 3. -w The associated program account if the account to close is a program data account.
        r = bytearray([0x05, 0x00, 0x00, 0x00])
        return r

    @classmethod
    def extend_program(cls, addition: int) -> bytearray:
        # Extend a program's program data account by the specified number of bytes. Only upgradeable program's can be
        # extended. Account references:
        # 0. -w the program data account.
        # 1. -w the program data account's associated program account.
        # 2. -r system program, optional, used to transfer lamports from the payer to the program data account.
        # 3. sw The payer account, optional, that will pay necessary rent exemption costs for the increased storage.
        r = bytearray([0x06, 0x00, 0x00, 0x00])
        r.extend(bytearray(addition.to_bytes(4, 'little')))
        return r

    @classmethod
    def set_authority_checked(cls) -> bytearray:
        # Set a new authority that is allowed to write the buffer or upgrade the program. This instruction differs from
        # set_authority in that the new authority is a required signer. Account references:
        # 0. -w the buffer or program data account to change the authority of.
        # 1. sr the current authority.
        # 2. sr the new authority, optional, if omitted then the program will not be upgradeable.
        r = bytearray([0x07, 0x00, 0x00, 0x00])
        return r


class ProgramSystem:
    # The system program is responsible for the creation of accounts.
    # See: https://github.com/anza-xyz/agave/blob/master/sdk/program/src/system_instruction.rs
    # See: https://github.com/solana-program/system/blob/main/interface/src/instruction.rs

    pubkey = PubKey(bytearray(32))

    @classmethod
    def create_account(cls, value: int, space: int, owner: PubKey) -> bytearray:
        # Create a new account. Account references:
        # 0. sw funding account.
        # 1. sw new account.
        r = bytearray([0x00, 0x00, 0x00, 0x00])
        r.extend(bytearray(int(value).to_bytes(8, 'little')))
        r.extend(bytearray(int(space).to_bytes(8, 'little')))
        r.extend(owner.p)
        return r

    @classmethod
    def assign(cls, owner: PubKey) -> bytearray:
        # Assign account to a program. Account references:
        # 0. sw assigned account public key.
        r = bytearray([0x01, 0x00, 0x00, 0x00])
        r.extend(owner.p)
        return r

    @classmethod
    def transfer(cls, value: int) -> bytearray:
        # Transfer lamports. Account references:
        # 0. sw funding account.
        # 1. -w recipient account.
        r = bytearray([0x02, 0x00, 0x00, 0x00])
        r.extend(bytearray(value.to_bytes(8, 'little')))
        return r


class ProgramSysvarClock:
    # The Clock sysvar contains data on cluster time, including the current slot, epoch, and estimated wall-clock unix
    # timestamp. It is updated every slot.

    pubkey = PubKey.base58_decode('SysvarC1ock11111111111111111111111111111111')


class ProgramSysvarRent:
    # The rent sysvar contains the rental rate. Currently, the rate is static and set in genesis. The rent burn
    # percentage is modified by manual feature activation.

    pubkey = PubKey.base58_decode('SysvarRent111111111111111111111111111111111')


class ProgramToken:
    # Solana spl token.
    # See: https://github.com/solana-labs/solana-program-library/blob/master/token/program/src/instruction.rs

    pubkey_2020 = PubKey.base58_decode('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
    pubkey_2022 = PubKey.base58_decode('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb')
    pubkey = pubkey_2020
    # See: https://github.com/solana-labs/solana-program-library/blob/master/token/program/src/state.rs#L18
    size_mint = 82

    @classmethod
    def initialize_mint(cls, decimals: int, auth_mint: PubKey, auth_freeze: PubKey) -> bytearray:
        # Initializes a new mint and optionally deposits all the newly minted tokens in an account. Account references:
        # 0. -w the mint to initialize.
        # 1. -r rent sysvar.
        r = bytearray([0x00])
        r.append(decimals)
        r.extend(auth_mint.p)
        r.append(0x01)
        r.extend(auth_freeze.p)
        return r

    @classmethod
    def initialize_account(cls):
        # Initializes a new account to hold tokens. Account references:
        # 0. -w the account to initialize.
        # 1. -r the mint this account will be associated with.
        # 2. -r the new account's owner/multisignature.
        # 3. -r rent sysvar.
        r = bytearray([0x01])
        return r

    @classmethod
    def initialize_multisig(cls, m: int) -> bytearray:
        # Initializes a multisignature account with N provided signers. Account references:
        # 0. -w the multisignature account to initialize.
        # 1. -r rent sysvar
        # 2. -r the signer accounts, must equal to N where 1 <= N <= 11.
        r = bytearray([0x02])
        r.append(m)
        return r

    @classmethod
    def transfer(cls, amount: int) -> bytearray:
        # Transfers tokens from one account to another either directly or via a delegate. Account references:
        # 0. -w the source account.
        # 1. -w the destination account.
        # 2. sr the source account's owner/delegate.
        r = bytearray([0x03])
        r.extend(amount.to_bytes(8, 'little'))
        return r

    @classmethod
    def approve(cls, amount: int) -> bytearray:
        # Approves a delegate.  A delegate is given the authority over tokens on behalf of the source account's owner.
        # Account references:
        # 0. -w the source account.
        # 1. -r the delegate.
        # 2. sr the source account owner.
        r = bytearray([0x04])
        r.extend(amount.to_bytes(8, 'little'))
        return r

    @classmethod
    def revoke(cls) -> bytearray:
        # Revokes the delegate's authority. Account references:
        # 0. -w the source account.
        # 1. sr the source account owner.
        r = bytearray([0x05])
        return r

    @classmethod
    def set_authority(cls, kype: int, pubkey: PubKey) -> bytearray:
        # Sets a new authority of a mint or account. Account references:
        # 0. -w the mint or account to change the authority of.
        # 1. sr the current authority of the mint or account.
        r = bytearray([0x06])
        r.append(kype)
        r.append(0x01)
        r.expandtabs(pubkey.p)
        return r

    @classmethod
    def mint_to(cls, amount: int) -> bytearray:
        # Mints new tokens to an account. Account references:
        # 0. -w the mint
        # 1. -w the account to mint tokens to.
        # 2. sr the mint's minting authority.
        r = bytearray([0x07])
        r.extend(amount.to_bytes(8, 'little'))
        return r

    @classmethod
    def burn(cls, amount: int) -> bytearray:
        # Burns tokens by removing them from an account. Account references:
        # 0. -w the account to burn from.
        # 1. -w the token mint.
        # 2. sr the account's owner/delegate.
        r = bytearray([0x08])
        r.extend(amount.to_bytes(8, 'little'))
        return r

    @classmethod
    def close_account(cls) -> bytearray:
        # Close an account by transferring all its sol to the destination account. Non-native accounts may only be
        # closed if its token amount is zero. Account references:
        # 0. -w the account to close.
        # 1. -w the destination account.
        # 2. sr the account's owner.
        r = bytearray([0x09])
        return r

    @classmethod
    def freeze_account(cls) -> bytearray:
        # Freeze an Initialized account using the Mint's freeze_authority (if set). Account references:
        # 0. -w the account to freeze.
        # 1. -r the token mint.
        # 2. sr the mint freeze authority.
        r = bytearray([0x0a])
        return r

    @classmethod
    def thaw_account(cls) -> bytearray:
        # Thaw a Frozen account using the Mint's freeze_authority (if set). Account references:
        # 0. -w the account to freeze
        # 1. -r the token mint
        # 2. sr the mint freeze authority.
        r = bytearray([0x0b])
        return r

    @classmethod
    def transfer_checked(cls, amount: int, decimals: int) -> bytearray:
        # Transfers tokens from one account to another either directly or via a delegate. Account references:
        # 0. -w the source account.
        # 1. -r the token mint.
        # 2. -w the destination account.
        # 3. sr the source account's owner/delegate.
        r = bytearray([0x0c])
        r.extend(amount.to_bytes(8, 'little'))
        r.append(decimals)
        return r

    @classmethod
    def approve_checked(cls, amount: int, decimals: int) -> bytearray:
        # Approves a delegate. Account references:
        # 0. -w the source account.
        # 1. -r the token mint.
        # 2. -r the delegate.
        # 3. sr the source account owner.
        r = bytearray([0x0d])
        r.extend(amount.to_bytes(8, 'little'))
        r.append(decimals)
        return r

    @classmethod
    def mint_to_checked(cls, amount: int, decimals: int) -> bytearray:
        # Mints new tokens to an account. Account references:
        # 0. -w the mint.
        # 1. -w the account to mint tokens to.
        # 2. sr the mint's minting authority.
        r = bytearray([0x0e])
        r.extend(amount.to_bytes(8, 'little'))
        r.append(decimals)
        return r

    @classmethod
    def burn_checked(cls, amount: int, decimals: int) -> bytearray:
        # Burns tokens by removing them from an account. Account references:
        # 0. -w the account to burn from.
        # 1. -w the token mint.
        # 2. sr the account's owner/delegate.
        r = bytearray([0x0f])
        r.extend(amount.to_bytes(8, 'little'))
        r.append(decimals)
        return r

    @classmethod
    def initialize_account2(cls, owner: PubKey) -> bytearray:
        # Like initialize_account(), but the owner pubkey is passed via instruction data rather than the accounts list.
        # Account references:
        # 0. -w the account to initialize.
        # 1. -r the mint this account will be associated with.
        # 2. -r rent sysvar
        r = bytearray([0x10])
        r.extend(owner.p)
        return r

    @classmethod
    def sync_native(cls) -> bytearray:
        # Given a wrapped / native token account (a token account containing sol) updates its amount field based on the
        # account's underlying `lamports`. Account references:
        # 0. -w the native token account to sync with its underlying lamports.
        r = bytearray([0x11])
        return r

    @classmethod
    def initialize_account3(cls, owner: PubKey) -> bytearray:
        # Like initialize_account2(), but does not require the Rent sysvar to be provided. Account references:
        # 0. -w the account to initialize.
        # 1. -r the mint this account will be associated with.
        r = bytearray([0x12])
        r.extend(owner.p)
        return r

    @classmethod
    def initialize_multisig2(cls, m: int) -> bytearray:
        # Like initialize_multisig(), but does not require the Rent sysvar to be provided. Account references:
        # 0. -w the multisignature account to initialize.
        # 1. -r the signer accounts, must equal to N where 1 <= N <= 11.
        r = bytearray([0x13])
        r.append(m)
        return r

    @classmethod
    def initialize_mint2(cls, decimals: int, auth_mint: PubKey, auth_freeze: PubKey) -> bytearray:
        # Like initialize_mint(), but does not require the Rent sysvar to be provided. Account references:
        # 0. -w the mint to initialize.
        r = bytearray([0x14])
        r.append(decimals)
        r.extend(auth_mint.p)
        r.append(0x01)
        r.extend(auth_freeze.p)
        return r

    @classmethod
    def get_account_data_size(cls) -> bytearray:
        # Gets the required size of an account for the given mint as a little-endian u64. Account references:
        # . -r the mint to calculate for.
        r = bytearray([0x15])
        return r

    @classmethod
    def initialize_immutable_owner(cls) -> bytearray:
        # Initialize the immutable owner extension for the given token account. Account references:
        # 0. -w the account to initialize.
        r = bytearray([0x16])
        return r

    @classmethod
    def amount_to_ui_amount(cls, amount: int) -> bytearray:
        # Convert an amount of tokens to a ui amount string, using the given mint. Account references:
        # 0. -r the mint to calculate for.
        r = bytearray([0x17])
        r.extend(amount.to_bytes(8, 'little'))
        return r

    @classmethod
    def ui_amount_to_amount(cls, amount: str) -> bytearray:
        # Convert a ui amount of tokens to a little-endian u64 raw amount, using the given mint. Account references:
        # 0. -r the mint to calculate for.
        r = bytearray([0x18])
        r.extend(bytearray(amount.encode()))
        return r


def compact_u16_encode(n: int) -> bytearray:
    # Same as u16, but serialized with 1 to 3 bytes. If the value is above 0x7f, the top bit is set and the remaining
    # value is stored in the next bytes. Each byte follows the same pattern until the 3rd byte. The 3rd byte, if
    # needed, uses all 8 bits to store the last byte of the original value.
    assert n >= 0
    assert n <= 0xffff
    if n <= 0x7f:
        return bytearray([n])
    if n <= 0x3fff:
        a = n & 0x7f | 0x80
        b = n >> 7
        return bytearray([a, b])
    if n <= 0xffff:
        a = n & 0x7f | 0x80
        n = n >> 7
        b = n & 0x7f | 0x80
        c = n >> 7
        return bytearray([a, b, c])
    raise Exception


def compact_u16_decode(data: bytearray) -> int:
    return compact_u16_decode_reader(io.BytesIO(data))


def compact_u16_decode_reader(reader: typing.BinaryIO) -> int:
    c = reader.read(1)[0]
    if c <= 0x7f:
        return c
    n = c & 0x7f
    c = reader.read(1)[0]
    m = c & 0x7f
    n += m << 7
    if c <= 0x7f:
        return n
    c = reader.read(1)[0]
    n += c << 14
    return n


class Instruction:
    # A compact encoding of an instruction.

    def __init__(self, program: int, account: typing.List[int], data: bytearray) -> None:
        # Identifies an on-chain program that will process the instruction. This is represented as an u8 index pointing
        # to an account address within the account addresses array.
        self.program = program
        # Array of u8 indexes pointing to the account addresses array for each account required by the instruction.
        self.account = account
        # A u8 byte array specific to the program invoked. This data specifies the instruction to invoke on the program
        # along with any additional data that the instruction requires (such as function arguments).
        self.data = data

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'program': self.program,
            'account': self.account,
            'data': pxsol.base58.encode(self.data)
        }

    def serialize(self) -> bytearray:
        r = bytearray()
        r.append(self.program)
        r.extend(compact_u16_encode(len(self.account)))
        for e in self.account:
            r.append(e)
        r.extend(compact_u16_encode(len(self.data)))
        r.extend(self.data)
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> typing.Self:
        return Instruction.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> typing.Self:
        i = Instruction(0, [], bytearray())
        i.program = int(reader.read(1)[0])
        for _ in range(compact_u16_decode_reader(reader)):
            i.account.append(int(reader.read(1)[0]))
        i.data = bytearray(reader.read(compact_u16_decode_reader(reader)))
        return i


class MessageHeader:
    # The message header specifies the privileges of accounts included in the transaction's account address array. It
    # is comprised of three bytes, each containing a u8 integer, which collectively specify:
    # 1. The number of required signatures for the transaction.
    # 2. The number of read-only account addresses that require signatures.
    # 3. The number of read-only account addresses that do not require signatures.

    def __init__(
        self,
        required_signatures: int,
        readonly_signatures: int,
        readonly: int
    ) -> None:
        self.required_signatures = required_signatures
        self.readonly_signatures = readonly_signatures
        self.readonly = readonly

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.List:
        return [self.required_signatures, self.readonly_signatures, self.readonly]

    def serialize(self) -> bytearray:
        return bytearray([self.required_signatures, self.readonly_signatures, self.readonly])

    @classmethod
    def serialize_decode(cls, data: bytearray) -> typing.Self:
        assert len(data) == 3
        return MessageHeader(data[0], data[1], data[2])

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> typing.Self:
        return MessageHeader.serialize_decode(bytearray(reader.read(3)))


class Message:
    # List of instructions to be processed atomically.

    def __init__(
        self,
        header: MessageHeader,
        account_keys: typing.List[PubKey],
        recent_blockhash: bytearray,
        instructions: typing.List[Instruction]
    ) -> None:
        self.header = header
        self.account_keys = account_keys
        self.recent_blockhash = recent_blockhash
        self.instructions = instructions

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'header': self.header.json(),
            'account_keys': [e.base58() for e in self.account_keys],
            'recent_blockhash': pxsol.base58.encode(self.recent_blockhash),
            'instructions': [e.json() for e in self.instructions],
        }

    def serialize(self) -> bytearray:
        r = bytearray()
        r.extend(self.header.serialize())
        r.extend(compact_u16_encode(len(self.account_keys)))
        for e in self.account_keys:
            r.extend(e.p)
        r.extend(self.recent_blockhash)
        r.extend(compact_u16_encode(len(self.instructions)))
        for e in self.instructions:
            r.extend(e.serialize())
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> typing.Self:
        return Message.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> typing.Self:
        m = Message(MessageHeader.serialize_decode_reader(reader), [], bytearray(), [])
        for _ in range(compact_u16_decode_reader(reader)):
            m.account_keys.append(PubKey(bytearray(reader.read(32))))
        m.recent_blockhash = bytearray(reader.read(32))
        for _ in range(compact_u16_decode_reader(reader)):
            m. instructions.append(Instruction.serialize_decode_reader(reader))
        return m


class Transaction:
    # An atomically-committed sequence of instructions.

    def __init__(self, signatures: typing.List[bytearray], message: Message) -> None:
        self.signatures = signatures
        self.message = message

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'signatures': [pxsol.base58.encode(e) for e in self.signatures],
            'message': self.message.json()
        }

    def requisition(self) -> typing.List[Requisition]:
        # Convert the transaction to requisitions.
        r = []
        for i in self.message.instructions:
            program = (self.message.account_keys[i.program])
            account = [self.message.account_keys[a] for a in i.account]
            r.append(Requisition(program, AccountMeta(account, 0), i.data))
        return r

    @classmethod
    def requisition_decode(cls, pubkey: PubKey, data: typing.List[Requisition]) -> typing.Self:
        # Convert the requisitions to transaction.
        account_flat: typing.List[AccountMeta] = [AccountMeta(pubkey, 3)]
        for r in data:
            account_flat.append(AccountMeta(r.program, 0))
            account_flat.extend(r.account)
        account_list: typing.List[AccountMeta] = []
        account_dict: typing.Dict[PubKey, int] = {}
        for a in account_flat:
            if a.pubkey not in account_dict:
                account_list.append(a)
                account_dict[a.pubkey] = len(account_list) - 1
                continue
            account_list[account_dict[a.pubkey]].mode |= a.mode
        account_list.sort(key=lambda x: x.mode, reverse=True)
        tx = pxsol.core.Transaction([], pxsol.core.Message(pxsol.core.MessageHeader(0, 0, 0), [], bytearray(), []))
        tx.message.account_keys.extend([e.pubkey for e in account_list])
        tx.message.header.required_signatures = len([k for k in account_list if k.mode >= 2])
        tx.message.header.readonly_signatures = len([k for k in account_list if k.mode == 2])
        tx.message.header.readonly = len([k for k in account_list if k.mode == 0])
        for r in data:
            program = tx.message.account_keys.index(r.program)
            account = [tx.message.account_keys.index(a.pubkey) for a in r.account]
            tx.message.instructions.append(Instruction(program, account, r.data))
        return tx

    def serialize(self) -> bytearray:
        r = bytearray()
        r.extend(compact_u16_encode(len(self.signatures)))
        for e in self.signatures:
            r.extend(e)
        r.extend(self.message.serialize())
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> typing.Self:
        return Transaction.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> typing.Self:
        s = []
        for _ in range(compact_u16_decode_reader(reader)):
            s.append(bytearray(reader.read(64)))
        return Transaction(s, Message.serialize_decode_reader(reader))

    def sign(self, prikey: typing.List[PriKey]) -> None:
        # Sign the transaction using the given private keys.
        assert self.message.header.required_signatures == len(prikey)
        m = self.message.serialize()
        for k in prikey:
            self.signatures.append(k.sign(m))
