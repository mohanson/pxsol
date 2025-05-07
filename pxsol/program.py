import hashlib
import pxsol.core
import typing

# Solana programs mainly use two serialization formats, bincode and borsh. Their specifications can be found on the
# following web pages:
# Bincode: https://github.com/bincode-org/bincode/blob/trunk/docs/spec.md
# Borsh: https://github.com/near/borsh#specification


class AssociatedTokenAccount:
    # See: https://github.com/solana-program/associated-token-account

    pubkey = pxsol.core.PubKey.base58_decode('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL')

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
        # associated token account. The tokens are moved from the nested associated token account to the wallet's
        # associated token account, and the nested account lamports are moved to the wallet. Note: Nested token
        # accounts are an anti-pattern, and almost always created unintentionally, so this instruction should only be
        # used to recover from errors. Account references:
        # 0. -w nested associated token account, must be owned by 3.
        # 1. -r token mint for the nested associated token account.
        # 2. -w wallet's associated token account.
        # 3. -r owner associated token account address, must be owned by 5.
        # 4. -r token mint for the owner associated token account.
        # 5. sw wallet address for the owner associated token account.
        # 6. -r spl token program.
        r = bytearray([0x02])
        return r


class ComputeBudget:
    # See: https://github.com/anza-xyz/agave/tree/master/sdk/compute-budget-interface
    # See: https://github.com/solana-program/compute-budget

    pubkey = pxsol.core.PubKey.base58_decode('ComputeBudget111111111111111111111111111111')

    @classmethod
    def request_heap_frame(cls, size: int) -> bytearray:
        # Request a specific transaction-wide program heap region size in bytes. The value requested must be a multiple
        # of 1024. This new heap region size applies to each program executed in the transaction, including all calls
        # to cpis.
        r = bytearray([0x01])
        r.extend(bytearray(size.to_bytes(4, 'little')))
        return r

    @classmethod
    def set_compute_unit_limit(cls, size: int) -> bytearray:
        # Set a specific compute unit limit that the transaction is allowed to consume.
        r = bytearray([0x02])
        r.extend(bytearray(size.to_bytes(4, 'little')))
        return r

    @classmethod
    def set_compute_unit_price(cls, unit: int) -> bytearray:
        # Set a compute unit price in "micro-lamports" to pay a higher transaction fee for higher transaction
        # prioritization. There are 10^6 micro-lamports in one lamport.
        assert unit <= 4  # Are you sure you want to pay such a high fee? You must have filled in the wrong number bro!
        r = bytearray([0x03])
        r.extend(bytearray(unit.to_bytes(8, 'little')))
        return r

    @classmethod
    def set_loaded_accounts_data_size_limit(cls, size: int) -> bytearray:
        # Set a specific transaction-wide account data size limit, in bytes, is allowed to load.
        r = bytearray([0x04])
        r.extend(bytearray(size.to_bytes(4, 'little')))
        return r


class LoaderUpgradeable:
    # The bpf loader program is the program that owns all executable accounts on solana. When you deploy a program, the
    # owner of the program account is set to the the bpf loader program.
    # See: https://github.com/anza-xyz/solana-sdk/blob/master/loader-v3-interface/src/instruction.rs
    # See: https://github.com/anza-xyz/solana-sdk/blob/master/program/src/bpf_loader_upgradeable.rs

    pubkey = pxsol.core.PubKey.base58_decode('BPFLoaderUpgradeab1e11111111111111111111111')

    # Account data is serialized by bincode. The enum type takes 4 bytes, and the option takes 1 byte.
    # Size of a buffer account's serialized metadata, calculated by the formula 4 + 1 + 32.
    size_program_buffer = 37
    # Size of a programdata account's serialized metadata, calculated by the formula 4 + 8 + 1 + 32.
    size_program_data = 45
    # Size of a serialized program account. calculated by the formula 4 + 32.
    size_program = 36

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
    def extend_program(cls, size: int) -> bytearray:
        # Extend a program's program data account by the specified number of bytes. Only upgradeable program's can be
        # extended. Account references:
        # 0. -w the program data account.
        # 1. -w the program data account's associated program account.
        # 2. -r system program, optional, used to transfer lamports from the payer to the program data account.
        # 3. sw The payer account, optional, that will pay necessary rent exemption costs for the increased storage.
        r = bytearray([0x06, 0x00, 0x00, 0x00])
        r.extend(bytearray(size.to_bytes(4, 'little')))
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


class System:
    # The system program is responsible for the creation of accounts.
    # See: https://github.com/solana-program/system
    # See: https://github.com/anza-xyz/agave/blob/master/sdk/program/src/system_instruction.rs

    pubkey = pxsol.core.PubKey(bytearray(32))

    @classmethod
    def create_account(cls, lamports: int, size: int, host: pxsol.core.PubKey) -> bytearray:
        # Create a new account. Account references:
        # 0. sw funding account.
        # 1. sw new account.
        r = bytearray([0x00, 0x00, 0x00, 0x00])
        r.extend(bytearray(int(lamports).to_bytes(8, 'little')))
        r.extend(bytearray(int(size).to_bytes(8, 'little')))
        r.extend(host.p)
        return r

    @classmethod
    def assign(cls, host: pxsol.core.PubKey) -> bytearray:
        # Assign account to a program. Account references:
        # 0. sw assigned account public key.
        r = bytearray([0x01, 0x00, 0x00, 0x00])
        r.extend(host.p)
        return r

    @classmethod
    def transfer(cls, lamports: int) -> bytearray:
        # Transfer lamports. Account references:
        # 0. sw funding account.
        # 1. -w recipient account.
        r = bytearray([0x02, 0x00, 0x00, 0x00])
        r.extend(bytearray(lamports.to_bytes(8, 'little')))
        return r

    @classmethod
    def create_account_with_seed(
        cls,
        base: pxsol.core.PubKey,
        seed: bytearray,
        lamports: int,
        size: int,
        host: pxsol.core.PubKey,
    ) -> bytearray:
        # Create a new account at an address derived from a base pubkey and a seed. Account references:
        # 0. sw funding account.
        # 1. -w created account.
        # 2. sr base account.
        r = bytearray([0x03, 0x00, 0x00, 0x00])
        r.extend(base.p)
        r.extend(bytearray(len(seed).to_bytes(8, 'little')))
        r.extend(seed)
        r.extend(bytearray(int(lamports).to_bytes(8, 'little')))
        r.extend(bytearray(int(size).to_bytes(8, 'little')))
        r.extend(host.p)
        return r

    @classmethod
    def advance_nonce_account(cls) -> bytearray:
        # Consumes a stored nonce, replacing it with a successor. Account references:
        # 0. -w nonce account.
        # 1. -r recent blockhashes sysvar.
        # 2. sr nonce authority.
        r = bytearray([0x04, 0x00, 0x00, 0x00])
        return r

    @classmethod
    def withdraw_nonce_account(cls, lamports: int) -> bytearray:
        # Withdraw funds from a nonce account. Account references:
        # 0. -w nonce account.
        # 1. -w recipient account.
        # 2. -r recentBlockhashes sysvar.
        # 3. -r rent sysvar.
        # 4. sr nonce authority.
        r = bytearray([0x05, 0x00, 0x00, 0x00])
        r.extend(bytearray(lamports.to_bytes(8, 'little')))
        return r

    @classmethod
    def initialize_nonce_account(cls, host: pxsol.core.PubKey) -> bytearray:
        # Drive state of Uninitialized nonce account to Initialized, setting the nonce value. Account references:
        # 0. -w nonce account.
        # 1. -r recent blockhashes sysvar.
        # 2. -r rent sysvar.
        r = bytearray([0x06, 0x00, 0x00, 0x00])
        r.extend(host.p)
        return r

    @classmethod
    def authorize_nonce_account(cls, host: pxsol.core.PubKey) -> bytearray:
        # Change the entity authorized to execute nonce instructions on the account. Account references:
        # 0. -w Nonce account
        # 1. sr Nonce authority
        r = bytearray([0x07, 0x00, 0x00, 0x00])
        r.extend(host.p)
        return r

    @classmethod
    def allocate(cls, size: int) -> bytearray:
        # Allocate space in a (possibly new) account without funding. Account references:
        # 0. sw new account.
        r = bytearray([0x08, 0x00, 0x00, 0x00])
        r.extend(bytearray(size.to_bytes(8, 'little')))
        return r

    @classmethod
    def allocate_with_seed(
        cls,
        base: pxsol.core.PubKey,
        seed: bytearray,
        size: int,
        host: pxsol.core.PubKey,
    ) -> bytearray:
        # Allocate space for and assign an account at an address derived from a base public key and a seed.
        # Account references
        # 0. -w Allocated account
        # 1. sr Base account
        r = bytearray([0x09, 0x00, 0x00, 0x00])
        r.extend(base.p)
        r.extend(bytearray(len(seed).to_bytes(8, 'little')))
        r.extend(seed)
        r.extend(bytearray(size.to_bytes(8, 'little')))
        r.extend(host.p)
        return r

    @classmethod
    def assign_with_seed(cls, base: pxsol.core.PubKey, seed: bytearray, host: pxsol.core.PubKey) -> bytearray:
        # Assign account to a program based on a seed. Account references:
        # 0. -w Assigned account
        # 1. sr Base account
        r = bytearray([0x0a, 0x00, 0x00, 0x00])
        r.extend(base.p)
        r.extend(bytearray(len(seed).to_bytes(8, 'little')))
        r.extend(seed)
        r.extend(host.p)
        return r

    @classmethod
    def transfer_with_seed(cls, lamports: int, seed: bytearray, host: pxsol.core.PubKey) -> bytearray:
        # Transfer lamports from a derived address. Account references:
        # 0. -w Funding account
        # 1. sr Base for funding account
        # 2. -w Recipient account
        r = bytearray([0x0b, 0x00, 0x00, 0x00])
        r.extend(bytearray(lamports.to_bytes(8, 'little')))
        r.extend(bytearray(len(seed).to_bytes(8, 'little')))
        r.extend(seed)
        r.extend(host.p)
        return r

    @classmethod
    def upgrade_nonce_account(cls) -> bytearray:
        # One-time idempotent upgrade of legacy nonce versions in order to bump them out of chain blockhash domain.
        # Account references:
        # 0. -w nonce account.
        r = bytearray([0x0c, 0x00, 0x00, 0x00])
        return r


class SysvarClock:
    # The Clock sysvar contains data on cluster time, including the current slot, epoch, and estimated wall-clock unix
    # timestamp. It is updated every slot.

    pubkey = pxsol.core.PubKey.base58_decode('SysvarC1ock11111111111111111111111111111111')


class SysvarRent:
    # The rent sysvar contains the rental rate. Currently, the rate is static and set in genesis. The rent burn
    # percentage is modified by manual feature activation.

    pubkey = pxsol.core.PubKey.base58_decode('SysvarRent111111111111111111111111111111111')


class Token:
    # Solana spl token.
    # See: https://github.com/solana-program/token-2022

    pubkey_2020 = pxsol.core.PubKey.base58_decode('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
    pubkey_2022 = pxsol.core.PubKey.base58_decode('TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb')
    pubkey = pubkey_2022
    # See: https://github.com/solana-labs/solana-program-library/blob/master/token/program-2022/src/state.rs
    size_mint = 82
    # The minimum for any account with extensions.
    size_extensions_base = 165 + 1
    # See: https://github.com/solana-labs/solana-program-library/blob/master/token/program-2022/src/extension/metadata_pointer/mod.rs
    size_extensions_metadata_pointer = 4 + 64
    # See: https://github.com/solana-labs/solana-program-library/blob/master/token-metadata/interface/src/state.rs
    size_extensions_metadata = 4 + 64 + 4 * 3 + 4

    @classmethod
    def initialize_mint(cls, decimals: int, auth_mint: pxsol.core.PubKey, auth_freeze: pxsol.core.PubKey) -> bytearray:
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
    def initialize_account(cls) -> bytearray:
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
        r.extend(bytearray(amount.to_bytes(8, 'little')))
        return r

    @classmethod
    def approve(cls, amount: int) -> bytearray:
        # Approves a delegate. A delegate is given the authority over tokens on behalf of the source account's owner.
        # Account references:
        # 0. -w the source account.
        # 1. -r the delegate.
        # 2. sr the source account owner.
        r = bytearray([0x04])
        r.extend(bytearray(amount.to_bytes(8, 'little')))
        return r

    @classmethod
    def revoke(cls) -> bytearray:
        # Revokes the delegate's authority. Account references:
        # 0. -w the source account.
        # 1. sr the source account owner.
        r = bytearray([0x05])
        return r

    @classmethod
    def set_authority(cls, auth_type: int, auth: pxsol.core.PubKey) -> bytearray:
        # Sets a new authority of a mint or account. Argument auth_type is an enumeration value, please refer to the
        # rust source code. Account references:
        # 0. -w the mint or account to change the authority of.
        # 1. sr the current authority of the mint or account.
        r = bytearray([0x06])
        r.append(auth_type)
        r.append(0x01)
        r.expandtabs(auth.p)
        return r

    @classmethod
    def mint_to(cls, amount: int) -> bytearray:
        # Mints new tokens to an account. Account references:
        # 0. -w the mint
        # 1. -w the account to mint tokens to.
        # 2. sr the mint's minting authority.
        r = bytearray([0x07])
        r.extend(bytearray(amount.to_bytes(8, 'little')))
        return r

    @classmethod
    def burn(cls, amount: int) -> bytearray:
        # Burns tokens by removing them from an account. Account references:
        # 0. -w the account to burn from.
        # 1. -w the token mint.
        # 2. sr the account's owner/delegate.
        r = bytearray([0x08])
        r.extend(bytearray(amount.to_bytes(8, 'little')))
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
        r.extend(bytearray(amount.to_bytes(8, 'little')))
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
        r.extend(bytearray(amount.to_bytes(8, 'little')))
        r.append(decimals)
        return r

    @classmethod
    def mint_to_checked(cls, amount: int, decimals: int) -> bytearray:
        # Mints new tokens to an account. Account references:
        # 0. -w the mint.
        # 1. -w the account to mint tokens to.
        # 2. sr the mint's minting authority.
        r = bytearray([0x0e])
        r.extend(bytearray(amount.to_bytes(8, 'little')))
        r.append(decimals)
        return r

    @classmethod
    def burn_checked(cls, amount: int, decimals: int) -> bytearray:
        # Burns tokens by removing them from an account. Account references:
        # 0. -w the account to burn from.
        # 1. -w the token mint.
        # 2. sr the account's owner/delegate.
        r = bytearray([0x0f])
        r.extend(bytearray(amount.to_bytes(8, 'little')))
        r.append(decimals)
        return r

    @classmethod
    def initialize_account2(cls, host: pxsol.core.PubKey) -> bytearray:
        # Like initialize_account(), but the owner pubkey is passed via instruction data rather than the accounts list.
        # Account references:
        # 0. -w the account to initialize.
        # 1. -r the mint this account will be associated with.
        # 2. -r rent sysvar
        r = bytearray([0x10])
        r.extend(host.p)
        return r

    @classmethod
    def sync_native(cls) -> bytearray:
        # Given a wrapped / native token account (a token account containing sol) updates its amount field based on the
        # account's underlying `lamports`. Account references:
        # 0. -w the native token account to sync with its underlying lamports.
        r = bytearray([0x11])
        return r

    @classmethod
    def initialize_account3(cls, host: pxsol.core.PubKey) -> bytearray:
        # Like initialize_account2(), but does not require the Rent sysvar to be provided. Account references:
        # 0. -w the account to initialize.
        # 1. -r the mint this account will be associated with.
        r = bytearray([0x12])
        r.extend(host.p)
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
    def initialize_mint2(cls, decimals: int, auth_mint: pxsol.core.PubKey, auth_freeze: pxsol.core.PubKey) -> bytearray:
        # Like initialize_mint(), but does not require the Rent sysvar to be provided. Account references:
        # 0. -w the mint to initialize.
        r = bytearray([0x14])
        r.append(decimals)
        r.extend(auth_mint.p)
        r.append(0x01)
        r.extend(auth_freeze.p)
        return r

    @classmethod
    def get_account_data_size(cls, extension_type: typing.List[int]) -> bytearray:
        # Gets the required size of an account for the given mint as a little-endian u64. Account references:
        # 0. -r the mint to calculate for.
        r = bytearray([0x15])
        for e in extension_type:
            r.extend(e.to_bytes(2, 'little'))
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
        r.extend(bytearray(amount.to_bytes(8, 'little')))
        return r

    @classmethod
    def ui_amount_to_amount(cls, amount: str) -> bytearray:
        # Convert a ui amount of tokens to a little-endian u64 raw amount, using the given mint. Account references:
        # 0. -r the mint to calculate for.
        r = bytearray([0x18])
        r.extend(bytearray(amount.encode()))
        return r

    @classmethod
    def withdraw_excess_lamports(cls) -> bytearray:
        # This instruction is to be used to rescue sol sent to any token program owned account by sending them to any
        # other account, leaving behind only lamports for rent exemption. Account references:
        # 0. -w source account owned by the token program.
        # 1. -w destination account.
        # 2. sr authority.
        r = bytearray([0x26])
        return r

    @classmethod
    def metadata_pointer_extension_initialize(cls, auth: pxsol.core.PubKey, mint: pxsol.core.PubKey) -> bytearray:
        # Initialize a new mint with a metadata pointer. Account references:
        # 0. -w the mint to initialize.
        r = bytearray([0x27, 0x00])
        r.extend(auth.p)
        r.extend(mint.p)
        return r

    @classmethod
    def metadata_pointer_extension_update(cls, mint: pxsol.core.PubKey) -> bytearray:
        # Update the metadata pointer address. Only supported for mints that include the metadata pointer extension.
        # Account references:
        # 0. -w the mint.
        # 1. sr the metadata pointer authority.
        r = bytearray([0x27, 0x01])
        r.extend(mint.p)
        return r

    @classmethod
    def metadata_initialize(cls, name: str, symbol: str, uri: str) -> bytearray:
        # Initializes a tlv entry with the basic token-metadata fields. Account references:
        # 0. -w metadata.
        # 1. -r update authority.
        # 2. -r mint.
        # 3. sr mint authority.
        r = bytearray(hashlib.sha256(b'spl_token_metadata_interface:initialize_account').digest()[:8])
        r.extend(bytearray(len(name).to_bytes(4, 'little')))
        r.extend(bytearray(name.encode()))
        r.extend(bytearray(len(symbol).to_bytes(4, 'little')))
        r.extend(bytearray(symbol.encode()))
        r.extend(bytearray(len(uri).to_bytes(4, 'little')))
        r.extend(bytearray(uri.encode()))
        return r

    @classmethod
    def metadata_update_field(cls, field: str, value: str) -> bytearray:
        # Updates a field in a token-metadata account. The field can be one of the required fields (name, symbol, uri),
        # or a totally new field denoted by a "key" string. Account references:
        # 0. -w metadata account.
        # 1. sr update authority.
        r = bytearray(hashlib.sha256(b'spl_token_metadata_interface:updating_field').digest()[:8])
        match field:
            case 'name':
                r.append(0x00)
            case 'symbol':
                r.append(0x01)
            case 'uri':
                r.append(0x02)
            case _:
                r.append(0x03)
                r.extend(bytearray(len(field).to_bytes(4, 'little')))
                r.extend(bytearray(field.encode()))
        r.extend(bytearray(len(value).to_bytes(4, 'little')))
        r.extend(bytearray(value.encode()))
        return r

    @classmethod
    def metadata_remove_key(cls, idempotent: bool, key: str) -> bytearray:
        # Removes a key-value pair in a token-metadata account. This only applies to additional fields, and not the
        # base name / symbol / uri fields. Account references:
        # 0. -w metadata account.
        # 1. sr update authority.
        r = bytearray(hashlib.sha256(b'spl_token_metadata_interface:remove_key_ix').digest()[:8])
        r.append(int(idempotent))
        r.extend(bytearray(len(key).to_bytes(4, 'little')))
        r.extend(bytearray(key.encode()))
        return r

    @classmethod
    def metadata_update_authority(cls, auth: pxsol.core.PubKey) -> bytearray:
        # Updates the token-metadata authority. Account references:
        # 0. -w metadata account.
        # 1. sr current update authority.
        r = bytearray(hashlib.sha256(b'spl_token_metadata_interface:update_the_authority').digest()[:8])
        r.extend(auth.p)
        return r

    @classmethod
    def metadata_emit(cls) -> bytearray:
        # Emits the token-metadata as return data. Account references:
        # 0. -r metadata account.
        r = bytearray(hashlib.sha256(b'spl_token_metadata_interface:emitter').digest()[:8])
        r.append(0x00)
        r.append(0x00)
        return r
