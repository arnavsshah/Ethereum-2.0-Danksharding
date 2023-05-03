from rlp import Serializable, encode, decode
from rlp.sedes import big_endian_int, binary, List, boolean, CountableList
from config import *

sender_type = type(big_endian_int)

class A(Serializable):
    Serializable._in_mutable_context = True

    fields = (
        ('sender', sender_type()),
    )

a = A(2)
b = A(2)

e1 = encode(a)
e2 = encode(b)

d1 = decode(e1, A)
d2 = decode(e2, A)

print(e1 == e2)
print(d1, d2)


