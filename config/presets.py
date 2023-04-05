from .custom_types import *

# Misc
MAX_COMMITTEES_PER_SLOT = 64
TARGET_COMMITTEE_SIZE = 128
MAX_VALIDATORS_PER_COMMITTEE = 2048
SHUFFLE_ROUND_COUNT = 90


# Hysterisis parameters not included


# Gwei values
# don't know if it will be used for this project (too complex)
MIN_DEPOSIT_AMOUNT = 2**0 * 10**9  # (= 1,000,000,000) - used in deposit contract
MAX_EFFECTIVE_BALANCE = 2**5 * 10**9  # (= 32,000,000,000) - 
EFFECTIVE_BALANCE_INCREMENT = 2**0 * 10**9  # (= 1,000,000,000)


# Time parameters
MIN_ATTESTATION_INCLUSION_DELAY = 1
SLOTS_PER_EPOCH = 32
MIN_SEED_LOOKAHEAD = 1


# State list lengths
EPOCHS_PER_SLASHINGS_VECTOR = 2 ** 13  # (=8,192) - too compelx to use maybe?
VALIDATOR_REGISTRY_LIMIT = 2**40  # (= 1,099,511,627,776)


# Rewards and Penalties not included yet


# Max operations per block
MAX_PROPOSER_SLASHINGS = 16
MAX_ATTESTER_SLASHINGS = 2
MAX_ATTESTATIONS = 128


# Sync committee not included


# Execution
MAX_TRANSACTIONS_PER_PAYLOAD = 2**20  # (= 1,048,576) transactions per execution paylod
