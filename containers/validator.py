from rlp import Serializable
from rlp.sedes import boolean

from config import *

class Validator(Serializable):
    '''
    This is the data structure that stores most of the information about an individual validator, 
    with only validators' balances stored elsewhere.
    '''

    fields = (
        ('pubkey', BLSPubkey), # stored raw
        ('effective_balance', Gwei),  # Balance at stake
        ('slashed', boolean),
    )

    # adding and removing validators, and validator withdrawals are not implemented
    # fixed set of validators are assumed at the start of the simulation     