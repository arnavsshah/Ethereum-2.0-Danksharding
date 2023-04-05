from rlp.sedes import big_endian_int, binary, boolean, List

Slot = big_endian_int  # 1 slot ~ 1 block
Epoch = big_endian_int  # 32 slots = 1 epoch

CommitteeIndex = big_endian_int  # index of committee in a slot (if there are multiple)
ValidatorIndex = big_endian_int  # validator registry index

Gwei = big_endian_int  # an amount in Gwei (10^−9 Ether)

Bytes4 = binary
Bytes20 = binary
Bytes32 = binary
Bytes48 = binary
Bytes96 = binary

Root = Bytes32  # Merkle root
Hash32 = Bytes32  # a 256-bit hash

DomainType = Bytes4  # domain type
Domain = Bytes32  # signature domain

BLSPubkey = Bytes48  # BLS12-381 public key
BLSSignature = Bytes96  # BLS12-381 signature

# < 2 ** 7 (8 bits)
ParticipationFlags = big_endian_int

ExecutionAddress = Bytes20 # Address of an account on the execution layer that receives the block fee

