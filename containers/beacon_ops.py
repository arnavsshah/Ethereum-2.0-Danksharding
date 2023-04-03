from rlp import Serializable

from config import *
from containers.beacon_block import SignedBeaconBlockHeader
from containers.attestation import IndexedAttestation

class ProposerSlashing(Serializable):
    '''
    ProposerSlashings may be included in blocks to prove that a validator 
    has broken the rules and ought to be slashed. 
    Proposers receive a reward for correctly submitting these.
    '''

    fields = (
        ('signed_header_1', SignedBeaconBlockHeader),
        ('signed_header_2', SignedBeaconBlockHeader)
    )


class AttesterSlashing(Serializable):
    '''
    AttesterSlashings may be included in blocks to prove that one or more validators 
    in a committee has broken the rules and ought to be slashed. 
    Proposers receive a reward for correctly submitting these.
    '''

    fields = (
        ('attestation_1', IndexedAttestation),
        ('attestation_2', IndexedAttestation)
    )