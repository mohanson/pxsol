import hashlib
import io
import json
import pxsol.base58
import pxsol.eddsa
import secrets
import typing


class PriKey:
    # Solana's private key is a 32-byte array, selected arbitrarily. In general, the private key is not used in
    # isolation; instead, it forms a 64-byte keypair together with the public key, which is also a 32-byte array.
    # Most solana wallets, such as phantom, import and export private keys in base58-encoded keypair format.

    def __init__(self, p: bytearray) -> None:
        assert len(p) == 32
        self.p = p

    def __eq__(self, other) -> bool:
        return self.p == other.p

    def __hash__(self) -> int:
        return self.int()

    def __repr__(self) -> str:
        return json.dumps(self.json())

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

    def json(self) -> str:
        return self.base58()

    def pubkey(self):
        # Get the eddsa public key corresponding to the private key.
        return PubKey(pxsol.eddsa.pubkey(self.p))

    @classmethod
    def random(cls) -> typing.Self:
        return PriKey(bytearray(secrets.token_bytes(32)))

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

    def __eq__(self, other) -> bool:
        return self.p == other.p

    def __hash__(self) -> int:
        return self.int()

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def base58(self) -> str:
        # Convert the public key to base58 representation.
        return pxsol.base58.encode(self.p)

    @classmethod
    def base58_decode(cls, data: str) -> typing.Self:
        # Convert the base58 representation to public key.
        return PubKey(pxsol.base58.decode(data))

    def derive(self, seed: bytearray, host: typing.Self) -> typing.Self:
        # Create new pubkey with seed and host.
        data = bytearray()
        data.extend(self.p)
        data.extend(seed)
        data.extend(host.p)
        assert not data.endswith(bytearray('ProgramDerivedAddress'.encode()))
        return PubKey(bytearray(hashlib.sha256(data).digest()))

    def derive_pda(self, seed: bytearray) -> typing.Self:
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

    def json(self) -> str:
        return self.base58()


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

    def __init__(self, required_signatures: int, readonly_signatures: int, readonly: int) -> None:
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


class TokenExtensionMetadataPointer:
    # Metadata pointer extension data for mints.

    def __init__(self, auth: PubKey, hold: PubKey) -> None:
        # Authority that can set the metadata address.
        self.auth = auth
        # Account address that holds the metadata.
        self.hold = hold

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'auth': self.auth.base58(),
            'hold': self.hold.base58(),
        }

    def serialize(self) -> bytearray:
        r = bytearray()
        r.extend(self.auth.p)
        r.extend(self.hold.p)
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> typing.Self:
        return TokenExtensionMetadataPointer(
            PubKey(data[0x00:0x20]),
            PubKey(data[0x20:0x40]),
        )


class TokenExtensionMetadata:
    # Metadata pointer extension data for mints.
    # See: https://github.com/solana-program/token-metadata/tree/main/interface.

    def __init__(
        self,
        auth_update: PubKey,
        mint: PubKey,
        name: str,
        symbol: str,
        uri: str,
        addition: typing.Dict[str, str],
    ) -> None:
        # The authority that can sign to update the metadata.
        self.auth_update = auth_update
        # The associated mint, used to counter spoofing to be sure that metadata belongs to a particular mint.
        self.mint = mint
        # The longer name of the token.
        self.name = name
        # The shortened symbol for the token.
        self.symbol = symbol
        # The URI pointing to richer metadata.
        self.uri = uri
        # Any additional metadata about the token as key-value pairs. The program must avoid storing the same key twice.
        self.addition = addition

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def json(self) -> typing.Dict:
        return {
            'auth_update': self.auth_update.base58(),
            'mint': self.mint.base58(),
            'name': self.name,
            'symbol': self.symbol,
            'uri': self.uri,
            'addition': self.addition,
        }

    def serialize(self) -> bytearray:
        r = bytearray()
        r.extend(self.auth_update.p)
        r.extend(self.mint.p)
        r.extend(bytearray(len(self.name).to_bytes(4, 'little')))
        r.extend(bytearray(self.name.encode()))
        r.extend(bytearray(len(self.symbol).to_bytes(4, 'little')))
        r.extend(bytearray(self.symbol.encode()))
        r.extend(bytearray(len(self.uri).to_bytes(4, 'little')))
        r.extend(bytearray(self.uri.encode()))
        r.extend(bytearray(len(self.addition).to_bytes(4, 'little')))
        for k, v in self.addition.items():
            r.extend(bytearray(len(k).to_bytes(4, 'little')))
            r.extend(bytearray(k.encode()))
            r.extend(bytearray(len(v).to_bytes(4, 'little')))
            r.extend(bytearray(v.encode()))
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> typing.Self:
        return TokenExtensionMetadata.serialize_decode_reader(io.BytesIO(data))

    @classmethod
    def serialize_decode_reader(cls, reader: io.BytesIO) -> typing.Self:
        m = TokenExtensionMetadata(
            PubKey(bytearray(reader.read(32))),
            PubKey(bytearray(reader.read(32))),
            reader.read(int.from_bytes(reader.read(4), 'little')).decode(),
            reader.read(int.from_bytes(reader.read(4), 'little')).decode(),
            reader.read(int.from_bytes(reader.read(4), 'little')).decode(),
            {},
        )
        l = int.from_bytes(reader.read(4), 'little')
        for _ in range(l):
            k = reader.read(int.from_bytes(reader.read(4), 'little')).decode()
            v = reader.read(int.from_bytes(reader.read(4), 'little')).decode()
            m.addition[k] = v
        return m


class TokenMint:
    # Account structure for storing token mint information.

    def __init__(
        self,
        auth_mint: PubKey,
        supply: int,
        decimals: int,
        inited: bool,
        auth_freeze: PubKey,
        extensions: typing.Dict[int, bytearray],
    ) -> None:
        # Optional authority used to mint new tokens. The mint authority may only be provided during mint creation. If
        # no mint authority is present then the mint has a fixed supply and no further tokens may be minted.
        self.auth_mint = auth_mint
        # Total supply of tokens.
        self.supply = supply
        # Number of base 10 digits to the right of the decimal place.
        self.decimals = decimals
        # Is `true` if this structure has been initialized.
        self.inited = inited
        # Optional authority to freeze token accounts.
        self.auth_freeze = auth_freeze
        # Extensions available to token mints and accounts.
        self.extensions = extensions

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def extension_metadata_pointer(self) -> TokenExtensionMetadataPointer:
        return TokenExtensionMetadataPointer.serialize_decode(self.extensions[0x12])

    def extension_metadata(self) -> TokenExtensionMetadata:
        return TokenExtensionMetadata.serialize_decode(self.extensions[0x13])

    def json(self) -> typing.Dict:
        extensions = {}
        for k, v in self.extensions.items():
            match k:
                case 0x12: extensions['metadata_pointer'] = self.extension_metadata_pointer().json()
                case 0x13: extensions['metadata'] = self.extension_metadata().json(),
                case _: extensions[k] = v.hex()
        return {
            'auth_mint': self.auth_mint.base58(),
            'supply': self.supply,
            'decimals': self.decimals,
            'inited': self.inited,
            'auth_freeze': self.auth_freeze.base58(),
            'extensions': extensions,
        }

    def serialize(self) -> bytearray:
        r = bytearray(82)
        r[0x00:0x04] = bytearray([0x01, 0x00, 0x00, 0x00])
        r[0x04:0x24] = self.auth_mint.p
        r[0x24:0x2c] = bytearray(self.supply.to_bytes(8, 'little'))
        r[0x2c] = self.decimals
        r[0x2d] = int(self.inited)
        r[0x2e:0x32] = bytearray([0x01, 0x00, 0x00, 0x00])
        r[0x32:0x52] = self.auth_freeze.p
        if len(self.extensions):
            # Mint creators and account owners can opt-in to token-2022 features. Extension data is written after the
            # end of the account data in token, which is the byte at index 165. This means it is always possible to
            # differentiate mints and accounts.
            r.extend(bytearray(83))
            # Append account type mint.
            r.append(0x01)
            for k in sorted(list(self.extensions.keys())):
                v = self.extensions[k]
                r.extend(bytearray(k.to_bytes(2, 'little')))
                r.extend(bytearray(len(v).to_bytes(2, 'little')))
                r.extend(v)
        return r

    @classmethod
    def serialize_decode(cls, data: bytearray) -> typing.Self:
        extensions = {}
        extensions_reader = io.BytesIO(data[166:])
        for _ in range(1 << 32):
            kype_byte = extensions_reader.read(2)
            if not kype_byte:
                break
            kype = int.from_bytes(kype_byte, 'little')
            size_byte = extensions_reader.read(2)
            size = int.from_bytes(size_byte, 'little')
            body = bytearray(extensions_reader.read(size))
            extensions[kype] = body
        return TokenMint(
            PubKey(data[0x04:0x24]),
            int.from_bytes(data[0x24:0x2c], 'little'),
            data[0x2c],
            data[0x2d] != 0x00,
            PubKey(data[0x32:0x52]),
            extensions,
        )
