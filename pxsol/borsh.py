import io
import itertools
import struct
import typing


class Decode:
    F = typing.Callable[[io.BytesIO], typing.Any]

    @classmethod
    def u8(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(1)), 'little')

    @classmethod
    def u16(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(2)), 'little')

    @classmethod
    def u32(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(4)), 'little')

    @classmethod
    def u64(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(8)), 'little')

    @classmethod
    def u128(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(16)), 'little')

    @classmethod
    def i8(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(1)), 'little', signed=True)

    @classmethod
    def i16(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(2)), 'little', signed=True)

    @classmethod
    def i32(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(4)), 'little', signed=True)

    @classmethod
    def i64(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(8)), 'little', signed=True)

    @classmethod
    def i128(cls, reader: io.BytesIO) -> int:
        return int.from_bytes(bytearray(reader.read(16)), 'little', signed=True)

    @classmethod
    def f32(cls, reader: io.BytesIO) -> float:
        return struct.unpack('<f', bytearray(reader.read(4)))[0]

    @classmethod
    def f64(cls, reader: io.BytesIO) -> float:
        return struct.unpack('<d', bytearray(reader.read(8)))[0]

    @classmethod
    def bool(cls, reader: io.BytesIO) -> bool:
        return bytearray(reader.read(1))[0] != 0

    @classmethod
    def array_constant(cls, decode: F, size: int) -> F:
        return lambda reader: [decode(reader) for _ in range(size)]

    @classmethod
    def array_variable(cls, decode: F) -> F:
        return lambda reader: [decode(reader) for _ in range(cls.u32(reader))]

    @classmethod
    def struct(cls, decode: typing.List[F]) -> F:
        return lambda reader: [f(reader) for f in decode]

    @classmethod
    def enum(cls, reader: io.BytesIO) -> int:
        return cls.u8(reader)

    @classmethod
    def hash_map(cls, decode: typing.List[F]) -> typing.Dict:
        return lambda reader: dict([[decode[0](reader), decode[1](reader)] for _ in range(cls.u32(reader))])

    @classmethod
    def hash_set(cls, decode: F) -> F:
        return cls.array_variable(decode)

    @classmethod
    def option(cls, decode: F) -> F:
        return lambda reader: None if cls.u8(reader) == 0 else decode(reader)

    @classmethod
    def string(cls, reader: io.BytesIO) -> str:
        return bytearray(reader.read(cls.u32(reader))).decode()


class Encode:
    F = typing.Callable[[typing.Any], bytearray]

    @classmethod
    def u8(cls, data: int) -> bytearray:
        assert data >= 0x00
        assert data <= 0xff
        return bytearray(data.to_bytes(1, 'little'))

    @classmethod
    def u16(cls, data: int) -> bytearray:
        assert data >= 0x00
        assert data <= 0xffff
        return bytearray(data.to_bytes(2, 'little'))

    @classmethod
    def u32(cls, data: int) -> bytearray:
        assert data >= 0x00
        assert data <= 0xffffffff
        return bytearray(data.to_bytes(4, 'little'))

    @classmethod
    def u64(cls, data: int) -> bytearray:
        assert data >= 0x00
        assert data <= 0xffffffffffffffff
        return bytearray(data.to_bytes(8, 'little'))

    @classmethod
    def u128(cls, data: int) -> bytearray:
        assert data >= 0x00
        assert data <= 0xffffffffffffffffffffffffffffffff
        return bytearray(data.to_bytes(16, 'little'))

    @classmethod
    def i8(cls, data: int) -> bytearray:
        assert data >= -0x80
        assert data <= +0x7f
        return bytearray(data.to_bytes(1, 'little', signed=True))

    @classmethod
    def i16(cls, data: int) -> bytearray:
        assert data >= -0x8000
        assert data <= +0x7fff
        return bytearray(data.to_bytes(2, 'little', signed=True))

    @classmethod
    def i32(cls, data: int) -> bytearray:
        assert data >= -0x80000000
        assert data <= +0x7fffffff
        return bytearray(data.to_bytes(4, 'little', signed=True))

    @classmethod
    def i64(cls, data: int) -> bytearray:
        assert data >= -0x8000000000000000
        assert data <= +0x7fffffffffffffff
        return bytearray(data.to_bytes(8, 'little', signed=True))

    @classmethod
    def i128(cls, data: int) -> bytearray:
        assert data >= -0x80000000000000000000000000000000
        assert data <= +0x7fffffffffffffffffffffffffffffff
        return bytearray(data.to_bytes(16, 'little', signed=True))

    @classmethod
    def f32(cls, data: float) -> bytearray:
        return bytearray(struct.pack('<f', data))

    @classmethod
    def f64(cls, data: float) -> bytearray:
        return bytearray(struct.pack('<d', data))

    @classmethod
    def bool(cls, data: bool) -> bytearray:
        return bytearray([int(data)])

    @classmethod
    def array_constant(cls, encode: F) -> F:
        return lambda data: bytearray(itertools.chain(*[encode(e) for e in data]))

    @classmethod
    def array_variable(cls, encode: F) -> F:
        return lambda data: cls.u32(len(data)) + bytearray(itertools.chain(*[encode(e) for e in data]))

    @classmethod
    def struct(cls, encode: typing.List[F]) -> F:
        return lambda data: bytearray(itertools.chain(*[e[1](e[0]) for e in zip(data, encode)]))

    @classmethod
    def enum(cls, data: int) -> bytearray:
        return cls.u8(data)

    @classmethod
    def hash_map(cls, encode: typing.List[F]) -> F:
        def f(data: typing.Dict) -> bytearray:
            keys = list(data.keys())
            keys.sort()
            r = cls.u32(len(keys))
            for k in keys:
                v = data[k]
                r.extend(encode[0](k))
                r.extend(encode[1](v))
            return r
        return f

    @classmethod
    def hash_set(cls, encode: F) -> F:
        def f(data: typing.List) -> bytearray:
            data = [encode(e) for e in data]
            data.sort()
            r = cls.u32(len(data))
            for e in data:
                r.extend(e)
            return r
        return f

    @classmethod
    def option(cls, encode: F) -> F:
        return lambda x: bytearray([0]) if x is None else bytearray([1]) + encode(x)

    @classmethod
    def string(cls, data: str) -> bytearray:
        return cls.u32(len(data)) + bytearray(data.encode())
