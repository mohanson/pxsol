import io
import pxsol


def test_bool():
    for case in [
        [False, bytearray([0x00])],
        [True, bytearray([0x01])],
    ]:
        assert pxsol.borsh.Encode.bool(case[0]) == case[1]
        assert pxsol.borsh.Decode.bool(io.BytesIO(case[1])) == case[0]


def test_number():
    case = [255, bytearray([255])]
    assert pxsol.borsh.Encode.u8(case[0]) == case[1]
    assert pxsol.borsh.Decode.u8(io.BytesIO(case[1])) == case[0]
    case = [-128, bytearray([128])]
    assert pxsol.borsh.Encode.i8(case[0]) == case[1]
    assert pxsol.borsh.Decode.i8(io.BytesIO(case[1])) == case[0]
    case = [65535, bytearray([255, 255])]
    assert pxsol.borsh.Encode.u16(case[0]) == case[1]
    assert pxsol.borsh.Decode.u16(io.BytesIO(case[1])) == case[0]
    case = [-32768, bytearray([0, 128])]
    assert pxsol.borsh.Encode.i16(case[0]) == case[1]
    assert pxsol.borsh.Decode.i16(io.BytesIO(case[1])) == case[0]
    case = [4294967295, bytearray([255, 255, 255, 255])]
    assert pxsol.borsh.Encode.u32(case[0]) == case[1]
    assert pxsol.borsh.Decode.u32(io.BytesIO(case[1])) == case[0]
    case = [-2147483648, bytearray([0, 0, 0, 128])]
    assert pxsol.borsh.Encode.i32(case[0]) == case[1]
    assert pxsol.borsh.Decode.i32(io.BytesIO(case[1])) == case[0]
    case = [18446744073709551615, bytearray([255, 255, 255, 255, 255, 255, 255, 255])]
    assert pxsol.borsh.Encode.u64(case[0]) == case[1]
    assert pxsol.borsh.Decode.u64(io.BytesIO(case[1])) == case[0]
    case = [-9223372036854775808, bytearray([0, 0, 0, 0, 0, 0, 0, 128])]
    assert pxsol.borsh.Encode.i64(case[0]) == case[1]
    assert pxsol.borsh.Decode.i64(io.BytesIO(case[1])) == case[0]
    case = [340282366920938463463374607431768211455, bytearray([255] * 16)]
    assert pxsol.borsh.Encode.u128(case[0]) == case[1]
    assert pxsol.borsh.Decode.u128(io.BytesIO(case[1])) == case[0]
    case = [-170141183460469231731687303715884105728, bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 128])]
    assert pxsol.borsh.Encode.i128(case[0]) == case[1]
    assert pxsol.borsh.Decode.i128(io.BytesIO(case[1])) == case[0]
    case = [0.5, bytearray([0, 0, 0, 63])]
    assert pxsol.borsh.Encode.f32(case[0]) == case[1]
    assert pxsol.borsh.Decode.f32(io.BytesIO(case[1])) == case[0]
    case = [-0.5, bytearray([0, 0, 0, 0, 0, 0, 224, 191])]
    assert pxsol.borsh.Encode.f64(case[0]) == case[1]
    assert pxsol.borsh.Decode.f64(io.BytesIO(case[1])) == case[0]


def test_array_constant():
    case = [[1, 2, 3], bytearray([1, 0, 2, 0, 3, 0])]
    assert pxsol.borsh.Encode.array_constant(pxsol.borsh.Encode.i16)(case[0]) == case[1]
    assert pxsol.borsh.Decode.array_constant(pxsol.borsh.Decode.i16, 3)(io.BytesIO(case[1])) == case[0]


def test_array_variable():
    case = [[1, 1], bytearray([2, 0, 0, 0, 1, 0, 1, 0])]
    assert pxsol.borsh.Encode.array_variable(pxsol.borsh.Encode.i16)(case[0]) == case[1]
    assert pxsol.borsh.Decode.array_variable(pxsol.borsh.Decode.i16)(io.BytesIO(case[1])) == case[0]


def test_struct():
    case = [
        [123, 'hello', 1400, 13],
        bytearray([
            0x7b, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x05, 0x00, 0x00, 0x00, 0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x78, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x01, 0x0d, 0x00,
        ])
    ]
    assert pxsol.borsh.Encode.struct([
        pxsol.borsh.Encode.u128,
        pxsol.borsh.Encode.string,
        pxsol.borsh.Encode.i64,
        pxsol.borsh.Encode.option(pxsol.borsh.Encode.u16),
    ])(case[0]) == case[1]
    assert pxsol.borsh.Decode.struct([
        pxsol.borsh.Decode.u128,
        pxsol.borsh.Decode.string,
        pxsol.borsh.Decode.i64,
        pxsol.borsh.Decode.option(pxsol.borsh.Decode.u16),
    ])(io.BytesIO(case[1])) == case[0]


def test_hash_map():
    case = [{'k': 'v'}, bytearray([1, 0, 0, 0, 1, 0, 0, 0, 107, 1, 0, 0, 0, 118])]
    assert pxsol.borsh.Encode.hash_map([pxsol.borsh.Encode.string, pxsol.borsh.Encode.string])(case[0]) == case[1]
    assert pxsol.borsh.Decode.hash_map([
        pxsol.borsh.Decode.string,
        pxsol.borsh.Decode.string,
    ])(io.BytesIO(case[1])) == case[0]


def test_hash_set():
    case = [[1, 2, 3], bytearray([3, 0, 0, 0, 1, 2, 3])]
    assert pxsol.borsh.Encode.hash_set(pxsol.borsh.Encode.u8)(case[0]) == case[1]
    assert pxsol.borsh.Decode.hash_set(pxsol.borsh.Decode.u8)(io.BytesIO(case[1])) == case[0]


def test_option():
    case = [1, bytearray([1, 1])]
    assert pxsol.borsh.Encode.option(pxsol.borsh.Encode.u8)(case[0]) == case[1]
    assert pxsol.borsh.Decode.option(pxsol.borsh.Decode.u8)(io.BytesIO(case[1])) == case[0]


def test_string():
    case = ['hello', bytearray([5, 0, 0, 0, 104, 101, 108, 108, 111])]
    assert pxsol.borsh.Encode.string(case[0]) == case[1]
    assert pxsol.borsh.Decode.string(io.BytesIO(case[1])) == case[0]
