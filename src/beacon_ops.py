from config.custom_constants import *
from config.custom_presets import *
from config.custom_types import *

from beacon_block import SignedBeaconBlockHeader
from attestation import IndexedAttestation

class ProposerSlashing():
    '''
    ProposerSlashings may be included in blocks to prove that a validator 
    has broken the rules and ought to be slashed. 
    Proposers receive a reward for correctly submitting these.
    '''
    signed_header_1: SignedBeaconBlockHeader
    signed_header_2: SignedBeaconBlockHeader


class AttesterSlashing():
    '''
    AttesterSlashings may be included in blocks to prove that one or more validators 
    in a committee has broken the rules and ought to be slashed. 
    Proposers receive a reward for correctly submitting these.
    '''
    attestation_1: IndexedAttestation
    attestation_2: IndexedAttestation