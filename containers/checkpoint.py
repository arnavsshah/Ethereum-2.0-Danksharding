from rlp import Serializable

from config import *

class Checkpoint(Serializable):
    '''
    Checkpoints are the points of justification and finalisation used by the Casper FFG protocol. 
    Validators use them to create AttestationData votes, and 
    the status of recent checkpoints is recorded in BeaconState.
    '''

    Serializable._in_mutable_context = True
    
    fields = (
        ('epoch', Epoch()),  # occurs at the 1st slot of every epoch
        ('root', Root())  # block root of the first block in the epoch (or earlier block is some slots have been skipped)
    )
