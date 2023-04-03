from rlp.sedes import big_endian_int, binary, boolean, List

Slot = big_endian_int  # 1 slot ~ 1 block
Epoch = big_endian_int  # 32 slots = 1 epoch

CommitteeIndex = big_endian_int  # index of committee in a slot (if there are multiple)
ValidatorIndex = big_endian_int  # validator registry index

Gwei = big_endian_int  # an amount in Gwei (10^−9 Ether)

Bytes20 = binary
Bytes32 = binary
Bytes48 = binary
Bytes96 = binary

Root = Bytes32  # Merkle root
Hash32 = Bytes32  # a 256-bit hash

BLSPubkey = Bytes48  # BLS12-381 public key
BLSSignature = Bytes96  # BLS12-381 signature

# length = 8 and values can be 0 or 1 (boolean)
ParticipationFlags = List([boolean for i in range(8)])

ExecutionAddress = Bytes20 # Address of an account on the execution layer that receives the block fee

