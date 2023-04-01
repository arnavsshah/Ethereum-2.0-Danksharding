from typing import List

from custom_types import *

# Misc
GENESIS_SLOT = Slot(0)
GENESIS_EPOCH = Epoch(0)
# length = 4
JUSTIFICATION_BITS_LENGTH = List[int]

# Participation flag indices
TIMELY_SOURCE_FLAG_INDEX = 0  # attestation with correct source checkpoint within integer_squareroot(SLOTS_PER_EPOCH) ~ 5 slots
TIMELY_TARGET_FLAG_INDEX = 1  # attestation with correct target checkpoint within (SLOTS_PER_EPOCH) = 32 slots
TIMELY_HEAD_FLAG_INDEX = 2  # attestation with the correct head within 1 slot (basically immediately)


# Incentivization weights
TIMELY_SOURCE_WEIGHT = 14  # reward proportion for attestation to the source epoch 
TIMELY_TARGET_WEIGHT = 26  # reward proportion for attestation to the target epoch
TIMELY_HEAD_WEIGHT = 14  # reward proportion for attestation to the head block 
SYNC_REWARD_WEIGHT = 2  # reward proportion for participating in sync committees
PROPOSER_WEIGHT = 8  # reward proportion for proposing a block
WEIGHT_DENOMINATOR = 64  # total of all reward proportions


# Withdrawal Prefixes not included


# Domain types not included yet


