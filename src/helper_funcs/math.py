from config.custom_constants import *
from config.custom_presets import *
from config.custom_types import *


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
    return Bytes32(a ^ b for a, b in zip(bytes_1, bytes_2))


def int_to_bytes(data: int) -> bytes:
    """
    Return the bytes serialization of ``data`` interpreted as ``ENDIANNESS``-endian.
    """
    pass



def bytes_to_int(data: bytes) -> int:
    """
    Return the integer deserialization of ``data`` interpreted as ``ENDIANNESS``-endian.
    """
    return int(int.from_bytes(data, ENDIANNESS))