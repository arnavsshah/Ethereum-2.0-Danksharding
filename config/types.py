from rlp.sedes import big_endian_int, binary, boolean, List

Slot = type(big_endian_int)  # 1 slot ~ 1 block
Epoch = type(big_endian_int)  # 32 slots = 1 epoch

CommitteeIndex = type(big_endian_int)  # index of committee in a slot (if there are multiple)
ValidatorIndex = type(big_endian_int)  # validator registry index

Gwei = type(big_endian_int)  # an amount in Gwei (10^−9 Ether)

Bytes4 = type(binary)
Bytes20 = type(binary)
Bytes32 = type(binary)
Bytes48 = type(binary)
Bytes64 = type(binary)
Bytes96 = type(binary)

Root = Bytes32  # Merkle root
Hash32 = Bytes32  # a 256-bit hash

DomainType = Bytes4  # domain type
Domain = Bytes32  # signature domain

BLSPubkey = Bytes48  # BLS12-381 public key
BLSSignature = Bytes96  # BLS12-381 signature

ECDSASignature = Bytes64  # for transactions 

# < 2 ** 7 (8 bits)
ParticipationFlags = type(big_endian_int)

ExecutionAddress = Bytes20 # Address of an account on the execution layer that receives the block fee

VersionedHash = Bytes32
KZGCommitment = Bytes48
KZGProof = Bytes48
BLSFieldElement = type(big_endian_int)
