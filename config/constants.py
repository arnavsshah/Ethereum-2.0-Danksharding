from .custom_types import *

# Misc
GENESIS_SLOT = 0
GENESIS_EPOCH = 0

JUSTIFICATION_BITS_LENGTH = 4
ENDIANNESS = 'big'  # little in eth spec - changed here to support pyrlp's big_endian_int format


# Participation flag indices
TIMELY_SOURCE_FLAG_INDEX = 0  # attestation with correct source checkpoint within integer_squareroot(SLOTS_PER_EPOCH) ~ 5 slots
TIMELY_TARGET_FLAG_INDEX = 1  # attestation with correct target checkpoint within (SLOTS_PER_EPOCH) = 32 slots
TIMELY_HEAD_FLAG_INDEX = 2  # attestation with the correct head within 1 slot (basically immediately)


# Incentivization weights
TIMELY_SOURCE_WEIGHT = 14  # reward proportion for attestation to the source epoch 
TIMELY_TARGET_WEIGHT = 26  # reward proportion for attestation to the target epoch
TIMELY_HEAD_WEIGHT = 14  # reward proportion for attestation to the head block 
PROPOSER_WEIGHT = 10  # reward proportion for proposing a block - eth spec is 8 (2 for sync reward weight added)
WEIGHT_DENOMINATOR = 64  # total of all reward proportions

PARTICIPATION_FLAG_WEIGHTS = [TIMELY_SOURCE_WEIGHT, TIMELY_TARGET_WEIGHT, TIMELY_HEAD_WEIGHT]


# Withdrawal Prefixes not included


# Domain types
DOMAIN_BEACON_PROPOSER = bytes.fromhex('00000000')
DOMAIN_BEACON_ATTESTER = bytes.fromhex('01000000')
DOMAIN_RANDAO = bytes.fromhex('02000000')
DOMAIN_DEPOSIT = bytes.fromhex('03000000')
DOMAIN_VOLUNTARY_EXIT = bytes.fromhex('04000000')
DOMAIN_SELECTION_PROOF = bytes.fromhex('05000000')
DOMAIN_AGGREGATE_AND_PROOF = bytes.fromhex('06000000')
DOMAIN_SYNC_COMMITTEE = bytes.fromhex('07000000')
DOMAIN_SYNC_COMMITTEE_SELECTION_PROOF = bytes.fromhex('08000000')
DOMAIN_CONTRIBUTION_AND_PROOF = bytes.fromhex('09000000')


