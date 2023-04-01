from config.custom_constants import *
from config.custom_presets import *
from config.custom_types import *

class Validator():
    '''
    This is the data structure that stores most of the information about an individual validator, 
    with only validators' balances stored elsewhere.
    '''
    pubkey: BLSPubkey  # stored raw
    effective_balance: Gwei  # Balance at stake
    slashed: bool

    # adding and removing validators, and validator withdrawals are not implemented
    # fixed set of validators are assumed at the start of the simulation     