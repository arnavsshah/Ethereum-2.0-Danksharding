from typing import List

Slot = int  # 1 slot ~ 1 block
Epoch = int  # 32 slots = 1 epoch

CommitteeIndex = int  # index of committee in a slot (if there are multiple)
ValidatorIndex = int  # validator registry index

Gwei = int  # an amount in Gwei (10^−9 Ether)

Root = str  # Merkle root
Bytes32 = str
Hash32 = str  # a 256-bit hash

BLSPubkey = str  # BLS12-381 public key
BLSSignature = str  # BLS12-381 signature

# length = 8
ParticipationFlags = List[bool]

ExecutionAddress = str # Address of an account on the execution layer that receives the block fee


