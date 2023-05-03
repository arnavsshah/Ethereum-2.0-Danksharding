from config import *

def integer_squareroot(n: int) -> int:
    """
    Return the largest integer ``x`` such that ``x**2 <= n``.
    """
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def xor(bytes_1: Bytes32, bytes_2: Bytes32) -> Bytes32:
    """
    Return the exclusive-or of two 32-byte strings.
    """
    return bytes(a ^ b for a, b in zip(bytes_1, bytes_2))


def int_to_bytes(data: int) -> bytes:
    """
    Return the bytes serialization of ``data`` interpreted as ``ENDIANNESS``-endian.
    """
    return data.to_bytes(32, byteorder=ENDIANNESS)


def bytes_to_int(data: bytes) -> int:
    """
    Return the integer deserialization of ``data`` interpreted as ``ENDIANNESS``-endian.
    """
    return int.from_bytes(data, byteorder=ENDIANNESS)


def fake_exponential(numerator: int, denominator: int) -> int:
    """
    Approximates 2 ** (numerator / denominator), with the simplest possible approximation 
    that is continuous and has a continuous derivative
    """

    cofactor = 2 ** (numerator // denominator)
    fractional = numerator % denominator
    return cofactor + (
        fractional * cofactor * 2 +
        (fractional ** 2 * cofactor) // denominator
    ) // (denominator * 3)