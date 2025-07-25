import pxsol
import pytest
import random


def test_fail_verify():
    # The probability of success is negligible.
    for _ in range(8):
        pubkey = bytearray(random.randbytes(32))
        msg = bytearray(random.randbytes(random.randint(0, 64)))
        sig = bytearray(random.randbytes(64))
        with pytest.raises(AssertionError):
            assert pxsol.eddsa.verify(pubkey, msg, sig)


def test_pt_encode_decode():
    for _ in range(8):
        k = pxsol.ed25519.Fr(random.randint(1, pxsol.ed25519.N - 1))
        p = pxsol.ed25519.G * k
        assert p == pxsol.eddsa.pt_decode(pxsol.eddsa.pt_encode(p))


def test_pt_exists():
    for _ in range(8):
        pt = pxsol.ed25519.G * pxsol.ed25519.Fr(random.randint(1,  pxsol.ed25519.N - 1))
        ptbyte = pxsol.eddsa.pt_encode(pt)
        assert pxsol.eddsa.pt_exists(ptbyte)
        assert pxsol.eddsa.pt_decode(ptbyte) == pt
    for _ in range(8):
        ptbyte = bytearray(random.randbytes(32))
        if not pxsol.eddsa.pt_exists(ptbyte):
            with pytest.raises(AssertionError):
                pxsol.eddsa.pt_decode(ptbyte)


def test_sign_verify():
    # https://datatracker.ietf.org/doc/html/rfc8032#section-7.1
    # Test Vectors for Ed25519
    # TEST 1
    prikey = bytearray([
        0x9d, 0x61, 0xb1, 0x9d, 0xef, 0xfd, 0x5a, 0x60, 0xba, 0x84, 0x4a, 0xf4, 0x92, 0xec, 0x2c, 0xc4,
        0x44, 0x49, 0xc5, 0x69, 0x7b, 0x32, 0x69, 0x19, 0x70, 0x3b, 0xac, 0x03, 0x1c, 0xae, 0x7f, 0x60,
    ])
    pubkey = pxsol.eddsa.pubkey(prikey)
    msg = bytearray([])
    sig = pxsol.eddsa.sign(prikey, msg)
    assert sig == bytearray([
        0xe5, 0x56, 0x43, 0x00, 0xc3, 0x60, 0xac, 0x72, 0x90, 0x86, 0xe2, 0xcc, 0x80, 0x6e, 0x82, 0x8a,
        0x84, 0x87, 0x7f, 0x1e, 0xb8, 0xe5, 0xd9, 0x74, 0xd8, 0x73, 0xe0, 0x65, 0x22, 0x49, 0x01, 0x55,
        0x5f, 0xb8, 0x82, 0x15, 0x90, 0xa3, 0x3b, 0xac, 0xc6, 0x1e, 0x39, 0x70, 0x1c, 0xf9, 0xb4, 0x6b,
        0xd2, 0x5b, 0xf5, 0xf0, 0x59, 0x5b, 0xbe, 0x24, 0x65, 0x51, 0x41, 0x43, 0x8e, 0x7a, 0x10, 0x0b,
    ])
    assert pxsol.eddsa.verify(pubkey, msg, sig)
    # TEST 2
    prikey = bytearray([
        0x4c, 0xcd, 0x08, 0x9b, 0x28, 0xff, 0x96, 0xda, 0x9d, 0xb6, 0xc3, 0x46, 0xec, 0x11, 0x4e, 0x0f,
        0x5b, 0x8a, 0x31, 0x9f, 0x35, 0xab, 0xa6, 0x24, 0xda, 0x8c, 0xf6, 0xed, 0x4f, 0xb8, 0xa6, 0xfb,
    ])
    pubkey = pxsol.eddsa.pubkey(prikey)
    msg = bytearray([0x72])
    sig = pxsol.eddsa.sign(prikey, msg)
    assert sig == bytearray([
        0x92, 0xa0, 0x09, 0xa9, 0xf0, 0xd4, 0xca, 0xb8, 0x72, 0x0e, 0x82, 0x0b, 0x5f, 0x64, 0x25, 0x40,
        0xa2, 0xb2, 0x7b, 0x54, 0x16, 0x50, 0x3f, 0x8f, 0xb3, 0x76, 0x22, 0x23, 0xeb, 0xdb, 0x69, 0xda,
        0x08, 0x5a, 0xc1, 0xe4, 0x3e, 0x15, 0x99, 0x6e, 0x45, 0x8f, 0x36, 0x13, 0xd0, 0xf1, 0x1d, 0x8c,
        0x38, 0x7b, 0x2e, 0xae, 0xb4, 0x30, 0x2a, 0xee, 0xb0, 0x0d, 0x29, 0x16, 0x12, 0xbb, 0x0c, 0x00,
    ])
    assert pxsol.eddsa.verify(pubkey, msg, sig)
    # TEST 3
    prikey = bytearray([
        0xc5, 0xaa, 0x8d, 0xf4, 0x3f, 0x9f, 0x83, 0x7b, 0xed, 0xb7, 0x44, 0x2f, 0x31, 0xdc, 0xb7, 0xb1,
        0x66, 0xd3, 0x85, 0x35, 0x07, 0x6f, 0x09, 0x4b, 0x85, 0xce, 0x3a, 0x2e, 0x0b, 0x44, 0x58, 0xf7,
    ])
    pubkey = pxsol.eddsa.pubkey(prikey)
    msg = bytearray([0xaf, 0x82])
    sig = pxsol.eddsa.sign(prikey, msg)
    assert sig == bytearray([
        0x62, 0x91, 0xd6, 0x57, 0xde, 0xec, 0x24, 0x02, 0x48, 0x27, 0xe6, 0x9c, 0x3a, 0xbe, 0x01, 0xa3,
        0x0c, 0xe5, 0x48, 0xa2, 0x84, 0x74, 0x3a, 0x44, 0x5e, 0x36, 0x80, 0xd7, 0xdb, 0x5a, 0xc3, 0xac,
        0x18, 0xff, 0x9b, 0x53, 0x8d, 0x16, 0xf2, 0x90, 0xae, 0x67, 0xf7, 0x60, 0x98, 0x4d, 0xc6, 0x59,
        0x4a, 0x7c, 0x15, 0xe9, 0x71, 0x6e, 0xd2, 0x8d, 0xc0, 0x27, 0xbe, 0xce, 0xea, 0x1e, 0xc4, 0x0a,
    ])
    assert pxsol.eddsa.verify(pubkey, msg, sig)
    # TEST SHA(abc)
    prikey = bytearray([
        0x83, 0x3f, 0xe6, 0x24, 0x09, 0x23, 0x7b, 0x9d, 0x62, 0xec, 0x77, 0x58, 0x75, 0x20, 0x91, 0x1e,
        0x9a, 0x75, 0x9c, 0xec, 0x1d, 0x19, 0x75, 0x5b, 0x7d, 0xa9, 0x01, 0xb9, 0x6d, 0xca, 0x3d, 0x42,
    ])
    pubkey = pxsol.eddsa.pubkey(prikey)
    msg = bytearray([
        0xdd, 0xaf, 0x35, 0xa1, 0x93, 0x61, 0x7a, 0xba, 0xcc, 0x41, 0x73, 0x49, 0xae, 0x20, 0x41, 0x31,
        0x12, 0xe6, 0xfa, 0x4e, 0x89, 0xa9, 0x7e, 0xa2, 0x0a, 0x9e, 0xee, 0xe6, 0x4b, 0x55, 0xd3, 0x9a,
        0x21, 0x92, 0x99, 0x2a, 0x27, 0x4f, 0xc1, 0xa8, 0x36, 0xba, 0x3c, 0x23, 0xa3, 0xfe, 0xeb, 0xbd,
        0x45, 0x4d, 0x44, 0x23, 0x64, 0x3c, 0xe8, 0x0e, 0x2a, 0x9a, 0xc9, 0x4f, 0xa5, 0x4c, 0xa4, 0x9f,
    ])
    sig = pxsol.eddsa.sign(prikey, msg)
    assert sig == bytearray([
        0xdc, 0x2a, 0x44, 0x59, 0xe7, 0x36, 0x96, 0x33, 0xa5, 0x2b, 0x1b, 0xf2, 0x77, 0x83, 0x9a, 0x00,
        0x20, 0x10, 0x09, 0xa3, 0xef, 0xbf, 0x3e, 0xcb, 0x69, 0xbe, 0xa2, 0x18, 0x6c, 0x26, 0xb5, 0x89,
        0x09, 0x35, 0x1f, 0xc9, 0xac, 0x90, 0xb3, 0xec, 0xfd, 0xfb, 0xc7, 0xc6, 0x64, 0x31, 0xe0, 0x30,
        0x3d, 0xca, 0x17, 0x9c, 0x13, 0x8a, 0xc1, 0x7a, 0xd9, 0xbe, 0xf1, 0x17, 0x73, 0x31, 0xa7, 0x04,
    ])
    assert pxsol.eddsa.verify(pubkey, msg, sig)
