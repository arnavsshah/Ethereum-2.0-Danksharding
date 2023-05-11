from .types import *

# Misc
MAX_COMMITTEES_PER_SLOT = 1
TARGET_COMMITTEE_SIZE = 3
MAX_VALIDATORS_PER_COMMITTEE = 3
SHUFFLE_ROUND_COUNT = 10


# aggregator selection
TARGET_AGGREGATORS_PER_COMMITTEE = 3  # makes module=1 in is_aggregator(). See its comment for more details


# Hysterisis parameters
HYSTERESIS_QUOTIENT = 4
HYSTERESIS_DOWNWARD_MULTIPLIER = 1
HYSTERESIS_UPWARD_MULTIPLIER = 5


# Gwei values
# don't know if it will be used for this project (too complex)
MIN_DEPOSIT_AMOUNT = 2**0 * 10**9  # (= 1,000,000,000) - used in deposit contract
MAX_EFFECTIVE_BALANCE = 2**5 * 10**9  # (= 32,000,000,000) - 
EFFECTIVE_BALANCE_INCREMENT = 2**0 * 10**9  # (= 1,000,000,000)


# Time parameters
MIN_ATTESTATION_INCLUSION_DELAY = 1  # ~12 seconds
SLOTS_PER_EPOCH = 4
MIN_SEED_LOOKAHEAD = 1
SLOTS_PER_HISTORICAL_ROOT = 2 ** 5  # (=64)


# subnets
ATTESTATION_SUBNET_COUNT = SLOTS_PER_EPOCH * MAX_COMMITTEES_PER_SLOT


# State list lengths
EPOCHS_PER_SLASHINGS_VECTOR = 2 ** 5  # (=32)
VALIDATOR_REGISTRY_LIMIT = 2**5  # (=32)
EPOCHS_PER_HISTORICAL_VECTOR = 2 ** 6  # (=64)


# Rewards and Penalties
BASE_REWARD_FACTOR = 2**6  # (= 64)
WHISTLEBLOWER_REWARD_QUOTIENT = 2**9  # (= 512)
PROPOSER_REWARD_QUOTIENT = 2**3  # (= 8)
MIN_SLASHING_PENALTY_QUOTIENT = 2**7  # (= 128)
PROPORTIONAL_SLASHING_MULTIPLIER = 1  #
MIN_SLASHING_PENALTY_QUOTIENT_ALTAIR = 2**6  # (= 64)
PROPORTIONAL_SLASHING_MULTIPLIER_ALTAIR = 2  #
MIN_SLASHING_PENALTY_QUOTIENT_BELLATRIX = 2**5  # (= 32)
PROPORTIONAL_SLASHING_MULTIPLIER_BELLATRIX = 3  #


# Max operations per block
MAX_PROPOSER_SLASHINGS = 16
MAX_ATTESTER_SLASHINGS = 2
MAX_ATTESTATIONS = 128


# Sync committee not included


# Execution
MAX_TRANSACTIONS_PER_PAYLOAD = 2**20  # (= 1,048,576) transactions per execution paylod


MAX_VERSIONED_HASHES_LIST_SIZE = 2**24  # (= 16777216) 
MAX_BLOBS_PER_BLOCK = 16
MAX_BLOBS_PER_TX = 2
CHUNKS_PER_BLOB = 4096 