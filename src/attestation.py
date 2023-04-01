from typing import List

from config.custom_constants import *
from config.custom_presets import *
from config.custom_types import *

from checkpoint import Checkpoint

class AttestationData():
    '''
    This is the fundamental unit of attestation data. 
    Attestations from (committees of) validators are used to provide votes simultaneously 
    for each of the LMD GHOST & Casper FFG consensus mechanisms.
    '''
    slot: Slot
    index: CommitteeIndex

    # LMD GHOST vote
    beacon_block_root: Root
    
    # FFG vote
    source: Checkpoint
    target: Checkpoint

    
class Attestation():
    '''
    This is the form in which attestations make their way around the network. 
    Attestations containing identical AttestationData can be combined into a 
    single attestation by aggregating the signatures.
    '''

    # Length <= MAX_VALIDATORS_PER_COMMITTEE and entries should be 0 or 1
    aggregation_bits: List[int]  # bit-list indicating all validators that have attested to the required data 
    data: AttestationData
    signature: BLSSignature


class IndexedAttestation():
    '''
    This is one of the forms in which aggregated attestations 
    (combined identical attestations from multiple validators in the same committee) are handled.
    Used for attester slashing
    '''

    # Length <= MAX_VALIDATORS_PER_COMMITTEE
    attesting_indices: List[ValidatorIndex]  # list of indices of validators based on the global validator registry.
    data: AttestationData
    signature: BLSSignature