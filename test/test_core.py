import pxsol
import random


def test_addr():
    prikey = pxsol.core.PriKey(bytearray(int(1).to_bytes(32)))
    pubkey = prikey.pubkey()
    assert pubkey.base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
    prikey = pxsol.core.PriKey(bytearray(int(2).to_bytes(32)))
    pubkey = prikey.pubkey()
    assert pubkey.base58() == '8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH'


def test_compact_u16_encode():
    assert pxsol.core.compact_u16_encode(0x0000), bytearray([0x00])
    assert pxsol.core.compact_u16_encode(0x007f), bytearray([0x7f])
    assert pxsol.core.compact_u16_encode(0x0080), bytearray([0x80, 0x01])
    assert pxsol.core.compact_u16_encode(0x00ff), bytearray([0xff, 0x01])
    assert pxsol.core.compact_u16_encode(0x0100), bytearray([0x80, 0x02])
    assert pxsol.core.compact_u16_encode(0x7fff), bytearray([0xff, 0xff, 0x01])
    assert pxsol.core.compact_u16_encode(0xffff), bytearray([0xff, 0xff, 0x03])


def test_compact_u16_decode():
    assert pxsol.core.compact_u16_decode(bytearray([0x00])) == 0x0000
    assert pxsol.core.compact_u16_decode(bytearray([0x7f])) == 0x007f
    assert pxsol.core.compact_u16_decode(bytearray([0x80, 0x01])) == 0x0080
    assert pxsol.core.compact_u16_decode(bytearray([0xff, 0x01])) == 0x00ff
    assert pxsol.core.compact_u16_decode(bytearray([0x80, 0x02])) == 0x0100
    assert pxsol.core.compact_u16_decode(bytearray([0xff, 0xff, 0x01])) == 0x7fff
    assert pxsol.core.compact_u16_decode(bytearray([0xff, 0xff, 0x03])) == 0xffff


def test_compact_u16_random():
    for _ in range(8):
        n = random.randint(0, 0xffff)
        assert pxsol.core.compact_u16_decode(pxsol.core.compact_u16_encode(n)) == n


def test_pda():
    pubkey = pxsol.core.PubKey.base58_decode('BPFLoaderUpgradeab1e11111111111111111111111')
    seed = bytearray(int(0).to_bytes(32))
    assert pxsol.core.pda(pubkey, seed).base58() == '5ReXsszTZPmCZuH7wHPoEkxqRq3Bb1xWWcim13zDH6LX'
    seed = bytearray(int(1).to_bytes(32))
    assert pxsol.core.pda(pubkey, seed).base58() == 'Eb6T9mLCxAE1FxAXbCGpB5TN3yMbgo9rsP8A8HWGwuXc'


def test_transaction():
    data = bytearray([
        0x01, 0xc5, 0x2e, 0xfc, 0x4e, 0x7b, 0x7f, 0x9c, 0x10, 0x45, 0xd5, 0xc8, 0x2a, 0x87, 0xea, 0x69,
        0x69, 0x1b, 0x0e, 0xa3, 0xd3, 0x29, 0x21, 0x6a, 0xc6, 0xc6, 0xbf, 0x3b, 0x3b, 0x34, 0xe9, 0x02,
        0xc7, 0x40, 0x59, 0xe8, 0xe5, 0x3f, 0xda, 0x0a, 0x0e, 0x5f, 0x7c, 0xc0, 0xc7, 0x11, 0x41, 0x65,
        0xfd, 0x47, 0x31, 0x3e, 0xb7, 0x43, 0xad, 0x85, 0xee, 0xfc, 0x0c, 0xac, 0x79, 0x41, 0x0e, 0x8b,
        0x07, 0x01, 0x00, 0x01, 0x03, 0x4c, 0xb5, 0xab, 0xf6, 0xad, 0x79, 0xfb, 0xf5, 0xab, 0xbc, 0xca,
        0xfc, 0xc2, 0x69, 0xd8, 0x5c, 0xd2, 0x65, 0x1e, 0xd4, 0xb8, 0x85, 0xb5, 0x86, 0x9f, 0x24, 0x1a,
        0xed, 0xf0, 0xa5, 0xba, 0x29, 0x74, 0x22, 0xb9, 0x88, 0x75, 0x98, 0x06, 0x8e, 0x32, 0xc4, 0x44,
        0x8a, 0x94, 0x9a, 0xdb, 0x29, 0x0d, 0x0f, 0x4e, 0x35, 0xb9, 0xe0, 0x1b, 0x0e, 0xe5, 0xf1, 0xa1,
        0xe6, 0x00, 0xfe, 0x26, 0x74, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x2c, 0x1c, 0x25, 0xcc, 0x12, 0xda, 0xd7, 0xee, 0xb2, 0xc4, 0xe6,
        0x7e, 0x11, 0x0e, 0xc3, 0x2b, 0x3b, 0x25, 0xf5, 0x57, 0x80, 0xb7, 0xbf, 0x8c, 0x39, 0xf4, 0x7c,
        0xb6, 0xec, 0x4e, 0xfd, 0x25, 0x01, 0x02, 0x02, 0x00, 0x01, 0x0c, 0x02, 0x00, 0x00, 0x00, 0x00,
        0xca, 0x9a, 0x3b, 0x00, 0x00, 0x00, 0x00,
    ])
    tx = pxsol.core.Transaction.serialize_decode(data)
    assert tx.serialize() == data
    assert tx.json() == pxsol.core.Transaction.json_decode(tx.json()).json()


def test_wif():
    prikey = pxsol.core.PriKey(bytearray(int(1).to_bytes(32)))
    wif = prikey.wif()
    assert wif == '1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA'
    assert pxsol.core.PriKey.wif_decode(wif) == prikey
