import hashlib
import sol.ed25519

# Edwards-Curve Digital Signature Algorithm (EdDSA)
# See https://datatracker.ietf.org/doc/html/rfc8032#ref-CURVE25519


def hash(data: bytearray) -> bytearray:
    return bytearray(hashlib.sha512(data).digest())


def pt_encode(pt: sol.ed25519.Pt) -> bytearray:
    # A curve point (x,y), with coordinates in the range 0 <= x,y < p, is coded as follows. First, encode the
    # y-coordinate as a little-endian string of 32 octets. The most significant bit of the final octet is always zero.
    # To form the encoding of the point, copy the least significant bit of the x-coordinate to the most significant bit
    # of the final octet.
    # See https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.2
    n = pt.y.x | ((pt.x.x & 1) << 255)
    return bytearray(n.to_bytes(32, 'little'))


def pt_decode(pt: bytearray) -> sol.ed25519.Pt:
    # Decoding a point, given as a 32-octet string, is a little more complicated.
    # See https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.3
    #
    # First, interpret the string as an integer in little-endian representation. Bit 255 of this number is the least
    # significant bit of the x-coordinate and denote this value x_0. The y-coordinate is recovered simply by clearing
    # this bit. If the resulting value is >= p, decoding fails.
    uint = int.from_bytes(pt, 'little')
    sign = uint >> 255
    yint = uint & ((1 << 255) - 1)
    assert yint < sol.ed25519.P
    # To recover the x-coordinate, the curve equation implies x^2 = (y^2 - 1) / (d y^2 + 1) (mod p). The denominator is
    # always non-zero mod p.
    y = sol.ed25519.Fq(yint)
    x_x = (y * y - sol.ed25519.Fq(1)) / (sol.ed25519.D * y * y + sol.ed25519.Fq(1))
    # To compute the square root of (u/v), the first step is to compute the candidate root x = (u/v)^((p+3)/8).
    x = x_x ** ((sol.ed25519.P + 3) // 8)
    # Again, there are three cases:
    # 1. If v x^2 = u (mod p), x is a square root.
    # 2. If v x^2 = -u (mod p), set x <-- x * 2^((p-1)/4), which is a square root.
    # 3. Otherwise, no square root exists for modulo p, and decoding fails.
    if x*x != x_x:
        x = x * sol.ed25519.Fq(2) ** ((sol.ed25519.P - 1) // 4)
        assert x*x == x_x
    # Finally, use the x_0 bit to select the right square root. If x = 0, and x_0 = 1, decoding fails.  Otherwise, if
    # x_0 != x mod 2, set x <-- p - x.  Return the decoded point (x,y).
    if x == sol.ed25519.Fq(0):
        assert not sign
    if x.x & 1 != sign:
        x = -x
    return sol.ed25519.Pt(x, y)


def sign(prikey: bytearray, m: bytearray) -> bytearray:
    # The inputs to the signing procedure is the private key, a 32-octet string, and a message M of arbitrary size.
    # See https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.6
    assert len(prikey) == 32
    h = hash(prikey)
    a = int.from_bytes(h[:32], 'little')
    a &= (1 << 254) - 8
    a |= (1 << 254)
    a = sol.ed25519.Fr(a)
    prefix = h[32:]
    A = pt_encode(sol.ed25519.G * a)
    r = sol.ed25519.Fr(int.from_bytes(hash(prefix + m), 'little'))
    R = sol.ed25519.G * r
    Rs = pt_encode(R)
    h = sol.ed25519.Fr(int.from_bytes(hash(Rs + A + m), 'little'))
    s = r + h * a
    return Rs + bytearray(s.x.to_bytes(32, 'little'))
