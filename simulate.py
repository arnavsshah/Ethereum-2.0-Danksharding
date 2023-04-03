from rlp import Serializable, encode, decode
from rlp.sedes import big_endian_int, binary, List, boolean, CountableList

Slot = big_endian_int


class A(Serializable):
    fields = (
        ('sender', CountableList(big_endian_int, max_length=3)),
    )

a = A([1,2,3,4])
e = encode(a)
d = decode(e, A)
print(e, list(a.sender))
